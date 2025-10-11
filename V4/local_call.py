import asyncio
import base64
import json
import sounddevice as sd
import numpy as np
import websockets
import uuid
from queue import Queue

# ---------- Config ----------
WS_URL = "ws://127.0.0.1:5000/media"
STREAM_SID = str(uuid.uuid4())

TWILIO_SAMPLE_RATE = 8000
TWILIO_FRAME_MS = 20
TWILIO_CHUNK_SAMPLES = int(TWILIO_SAMPLE_RATE * TWILIO_FRAME_MS / 1000)

DEVICE_INDEX = 14  # Your mic
CHANNELS = 1

# μ-law constants
MULAW_BIAS = 0x84
MULAW_MAX = 0x1FFF

# Thread-safe queue for audio
audio_queue = Queue()

# ---------- μ-law encode ----------
def pcm16_to_mulaw(pcm16: np.ndarray) -> bytes:
    pcm = pcm16.astype(np.int32)
    sign = (pcm < 0)
    pcm = np.clip(np.abs(pcm), 0, MULAW_MAX)
    pcm += MULAW_BIAS
    exponents = np.zeros_like(pcm, dtype=np.int16)
    temp = pcm.copy()
    for e in range(7, 0, -1):
        mask = (1 << (e + 3))
        exponents = np.where(temp & mask, e, exponents)
    mantissa = (pcm >> (exponents + 3)) & 0x0F
    mu = (~(((sign.astype(np.int16) << 7) & 0x80) | (exponents << 4) | mantissa)) & 0xFF
    return mu.astype(np.uint8).tobytes()

# ---------- Sounddevice callback ----------
def audio_callback(indata, frames, time, status):
    # Convert float32 [-1,1] -> PCM16
    pcm16 = (indata[:, 0] * 32767).astype(np.int16)
    audio_queue.put(pcm16)

# ---------- Async stream sender ----------
async def send_stream():
    async with websockets.connect(WS_URL) as ws:
        await ws.send(json.dumps({"event": "start", "start": {"streamSid": STREAM_SID}}))
        print(f"Started streamSid={STREAM_SID}")

        while True:
            # Collect enough samples for 20ms frame
            frame_samples = np.zeros(TWILIO_CHUNK_SAMPLES, dtype=np.int16)
            collected = 0
            while collected < TWILIO_CHUNK_SAMPLES:
                chunk = audio_queue.get()
                take = min(len(chunk), TWILIO_CHUNK_SAMPLES - collected)
                frame_samples[collected:collected+take] = chunk[:take]
                collected += take
            # μ-law encode
            mulaw = pcm16_to_mulaw(frame_samples)
            payload_b64 = base64.b64encode(mulaw).decode("ascii")
            # Send over WS
            await ws.send(json.dumps({
                "event": "media",
                "streamSid": STREAM_SID,
                "media": {"payload": payload_b64}
            }))

# ---------- Main ----------
if __name__ == "__main__":
    try:
        DEVICE_INFO = sd.query_devices(DEVICE_INDEX)
        NATIVE_RATE = int(DEVICE_INFO["default_samplerate"])
        print(f"Using device {DEVICE_INDEX} ({DEVICE_INFO['name']}) at {NATIVE_RATE} Hz")

        with sd.InputStream(
            device=DEVICE_INDEX,
            channels=CHANNELS,
            samplerate=NATIVE_RATE,
            blocksize=int(NATIVE_RATE * TWILIO_FRAME_MS / 1000),
            dtype='float32',
            callback=audio_callback
        ):
            asyncio.run(send_stream())
    except KeyboardInterrupt:
        print("\nStopped by user")
