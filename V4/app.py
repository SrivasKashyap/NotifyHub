# app.py
import os
import io
import json
import base64
import wave
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
from openai import OpenAI
import numpy as np

# ---------------- Load env ----------------
load_dotenv()
BASE_URL = os.getenv("BASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BASE_URL or not OPENAI_API_KEY:
    raise RuntimeError("Set BASE_URL and OPENAI_API_KEY in .env")

# Build WebSocket URL
if BASE_URL.startswith("https://"):
    STREAM_URL = BASE_URL.replace("https://", "wss://").rstrip("/") + "/media"
elif BASE_URL.startswith("http://"):
    STREAM_URL = BASE_URL.replace("http://", "ws://").rstrip("/") + "/media"
else:
    raise RuntimeError("BASE_URL must start with http:// or https://")

print("Using STREAM_URL:", STREAM_URL)

# ---------------- OpenAI ----------------
client = OpenAI(api_key=OPENAI_API_KEY)
ASR_MODEL = "whisper-1"
CHAT_MODEL = "gpt-4o-mini"
TTS_MODEL = "gpt-4o-mini-tts"
TTS_VOICE = "verse"

# ---------------- Twilio audio constants ----------------
TWILIO_SAMPLE_RATE = 8000
TWILIO_FRAME_MS = 20
TWILIO_CHUNK_SAMPLES = int(TWILIO_SAMPLE_RATE * (TWILIO_FRAME_MS / 1000.0))  # 160
TWILIO_BYTES_PER_SAMPLE = 1  # μ-law 8-bit
BUFFER_MS = 1500  # ASR buffer length
BUFFER_BYTES = int(TWILIO_SAMPLE_RATE * (BUFFER_MS / 1000.0)) * 2  # PCM16 bytes

# ---------------- μ-law constants ----------------
MULAW_BIAS = 0x84
MULAW_MAX = 0x1FFF

# ---------------- App ----------------
app = FastAPI()

# ---------------- μ-law / PCM helpers ----------------
def mulaw_bytes_to_pcm16_bytes(mulaw_bytes: bytes) -> bytes:
    if not mulaw_bytes:
        return b""
    mu = np.frombuffer(mulaw_bytes, dtype=np.uint8).astype(np.int16)
    mu = ~mu & 0xFF
    sign = (mu & 0x80) != 0
    exponent = (mu & 0x70) >> 4
    mantissa = mu & 0x0F
    magnitude = ((mantissa << 3) + MULAW_BIAS) << exponent
    pcm = magnitude - MULAW_BIAS
    pcm = pcm.astype(np.int16)
    pcm[sign] = -pcm[sign]
    return pcm.tobytes()

def pcm16_bytes_to_mulaw_bytes(pcm16_bytes: bytes) -> bytes:
    if not pcm16_bytes:
        return b""
    pcm = np.frombuffer(pcm16_bytes, dtype=np.int16).astype(np.int32)
    sign = (pcm < 0)
    pcm_abs = np.clip(np.abs(pcm), 0, MULAW_MAX)
    pcm_biased = pcm_abs + MULAW_BIAS

    exponents = np.zeros_like(pcm_biased, dtype=np.int16)
    temp = pcm_biased.copy()
    for e in range(7, 0, -1):
        mask = (1 << (e + 3))
        exponents = np.where(temp & mask, e, exponents)
    mantissa = (pcm_biased >> (exponents + 3)) & 0x0F
    mu = (~(((sign.astype(np.int16) << 7) & 0x80) | (exponents << 4) | mantissa)) & 0xFF
    return mu.astype(np.uint8).tobytes()

def resample_pcm16_bytes(pcm16_bytes: bytes, src_rate: int, dst_rate: int) -> bytes:
    if src_rate == dst_rate or not pcm16_bytes:
        return pcm16_bytes
    pcm = np.frombuffer(pcm16_bytes, dtype=np.int16).astype(np.float32)
    new_len = int(len(pcm) * dst_rate / src_rate)
    if new_len <= 0:
        return b""
    x_old = np.linspace(0, 1, num=len(pcm))
    x_new = np.linspace(0, 1, num=new_len)
    resampled = np.interp(x_new, x_old, pcm).astype(np.int16)
    return resampled.tobytes()

def wav_from_pcm16(pcm16_bytes: bytes, sample_rate: int) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm16_bytes)
    return buf.getvalue()

# ---------------- OpenAI helpers ----------------
async def asr_whisper_wav(pcm16_bytes: bytes) -> str:
    pcm16_16k = resample_pcm16_bytes(pcm16_bytes, TWILIO_SAMPLE_RATE, 16000)
    wav_bytes = wav_from_pcm16(pcm16_16k, 16000)
    # Save debug WAV
    with open("debug_asr.wav", "wb") as f: f.write(wav_bytes)
    resp = client.audio.transcriptions.create(
        model=ASR_MODEL,
        file=("chunk.wav", io.BytesIO(wav_bytes), "audio/wav"),
        response_format="json"
    )
    return (resp.text or "").strip()

async def chat_reply_for_history(history: List[Dict], user_text: str) -> str:
    messages = history + [{"role": "user", "content": user_text}]
    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
        temperature=0.5
    )
    return resp.choices[0].message.content.strip()

async def tts_to_mulaw_frames(text: str):
    speech = client.audio.speech.create(
        model=TTS_MODEL,
        voice=TTS_VOICE,
        input=text,
        response_format="wav"
    )
    wav_bytes = speech.read()
    with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
        n_channels, sampwidth, rate, n_frames = wf.getnchannels(), wf.getsampwidth(), wf.getframerate(), wf.getnframes()
        raw = wf.readframes(n_frames)

        # Convert to PCM16 mono
        if sampwidth == 2:
            pcm16 = np.frombuffer(raw, dtype=np.int16)
        elif sampwidth == 4:
            pcm16 = (np.frombuffer(raw, dtype=np.float32) * 32767).astype(np.int16)
        else:
            raise RuntimeError("Unsupported TTS sample width")
        if n_channels == 2:
            pcm16 = ((pcm16[0::2] + pcm16[1::2]) // 2).astype(np.int16)

    # Resample to 8 kHz
    pcm8k = resample_pcm16_bytes(pcm16.tobytes(), rate, TWILIO_SAMPLE_RATE)
    # Save debug TTS WAV
    with open("debug_tts.wav", "wb") as f:
        f.write(wav_from_pcm16(pcm8k, TWILIO_SAMPLE_RATE))

    mulaw = pcm16_bytes_to_mulaw_bytes(pcm8k)
    chunk_size = TWILIO_CHUNK_SAMPLES * TWILIO_BYTES_PER_SAMPLE
    for i in range(0, len(mulaw), chunk_size):
        yield base64.b64encode(mulaw[i:i+chunk_size]).decode("ascii")

# ---------------- Conversation store ----------------
conversations: Dict[str, List[Dict]] = {}
SYSTEM_PROMPT = {
    "role": "system",
    "content": "You are a concise, friendly voice assistant. Keep replies short (1–2 sentences)."
}

# ---------------- FastAPI endpoints ----------------
@app.post("/voice")
async def voice():
    twiml = f"""
    <Response>
        <Say>Connecting you to your AI assistant now.</Say>
        <Connect>
            <Stream url="{STREAM_URL}" />
        </Connect>
    </Response>
    """
    return Response(content=twiml.strip(), media_type="application/xml")

@app.websocket("/media")
async def media(ws: WebSocket):
    await ws.accept()
    print("🔌 WebSocket accepted")
    stream_sid = None
    pcm_buffer = bytearray()

    try:
        while True:
            raw = await ws.receive_text()
            msg = json.loads(raw)
            event = msg.get("event")

            if event == "start":
                stream_sid = msg["start"]["streamSid"]
                print(f"🎙️ Start streamSid={stream_sid}")
                if stream_sid not in conversations:
                    conversations[stream_sid] = [SYSTEM_PROMPT.copy()]
                continue

            if event == "media":
                payload_b64 = msg["media"]["payload"]
                mulaw = base64.b64decode(payload_b64)
                pcm_buffer.extend(mulaw_bytes_to_pcm16_bytes(mulaw))

                if len(pcm_buffer) >= BUFFER_BYTES:
                    chunk = bytes(pcm_buffer)
                    pcm_buffer.clear()
                    try:
                        text = await asr_whisper_wav(chunk)
                    except Exception as e:
                        print("ASR error:", e)
                        text = ""
                    if text:
                        print(f"🗣️ User ({stream_sid}): {text}")
                        conv = conversations.get(stream_sid, [SYSTEM_PROMPT.copy()])
                        conv.append({"role": "user", "content": text})

                        try:
                            reply = await chat_reply_for_history(conv, text)
                        except Exception as e:
                            print("LLM error:", e)
                            reply = "Sorry, I had a processing issue."
                        conv.append({"role": "assistant", "content": reply})
                        conversations[stream_sid] = conv
                        print(f"🤖 Reply: {reply}")

                        async for frame64 in tts_to_mulaw_frames(reply):
                            await ws.send_text(json.dumps({
                                "event": "media",
                                "streamSid": stream_sid,
                                "media": {"payload": frame64}
                            }))

                        await ws.send_text(json.dumps({
                            "event": "mark",
                            "streamSid": stream_sid,
                            "mark": {"name": f"done-{datetime.utcnow().timestamp()}"}
                        }))

            elif event == "stop":
                print(f"🛑 streamSid={stream_sid} stopped")
                break

    except WebSocketDisconnect:
        print("⚠️ WebSocket disconnected")
    except Exception as e:
        print("❌ WebSocket error:", e)
    finally:
        try: await ws.close()
        except: pass
        print(f"🔒 WebSocket closed (streamSid={stream_sid})")
