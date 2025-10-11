import asyncio
import os
import io
import numpy as np
import sounddevice as sd
import soundfile as sf
from openai import OpenAI
import edge_tts

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Set OPENAI_API_KEY in your environment variables.")

client = OpenAI(api_key=OPENAI_API_KEY)

SAMPLE_RATE = 16000
CHUNK_DURATION = 3  # seconds per chunk

async def tts_play(text: str):
    """Convert text to speech and play via sounddevice"""
    tts_file = "tts_output.wav"
    communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
    await communicate.save(tts_file)  # save TTS to WAV

    data, fs = sf.read(tts_file, dtype='float32')
    sd.play(data, fs)
    sd.wait()

async def process_audio_chunk(audio_chunk: np.ndarray):
    """Convert audio chunk to a proper WAV file in memory and send to Whisper"""
    wav_buffer = io.BytesIO()
    sf.write(wav_buffer, audio_chunk, SAMPLE_RATE, format="WAV", subtype="PCM_16")
    wav_buffer.seek(0)

    try:
        whisper_resp = client.audio.transcriptions.create(
            model="whisper-1",
            file=("audio.wav", wav_buffer, "audio/wav")
        )
        transcript = whisper_resp.text
        print(f"User said: {transcript}")
        return transcript
    except Exception as e:
        print("Whisper error:", e)
        return None

async def generate_gpt_response(prompt: str):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        reply = response.choices[0].message.content
        print(f"GPT says: {reply}")
        return reply
    except Exception as e:
        print("GPT error:", e)
        return None

async def live_loop():
    print("🎤 Live voice loop started. Speak into your mic...")

    while True:
        audio_chunk = sd.rec(int(SAMPLE_RATE * CHUNK_DURATION), samplerate=SAMPLE_RATE, channels=1, dtype='int16')
        sd.wait()
        audio_chunk = np.squeeze(audio_chunk)

        transcript = await process_audio_chunk(audio_chunk)
        if not transcript:
            continue

        reply = await generate_gpt_response(transcript)
        if not reply:
            continue

        await tts_play(reply)

if __name__ == "__main__":
    asyncio.run(live_loop())
