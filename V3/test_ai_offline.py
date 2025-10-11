import sounddevice as sd
import numpy as np
import whisper
import requests
import pyttsx3
import tempfile
import wave
import json

# Settings
DURATION = 5  # seconds to record
SAMPLE_RATE = 16000
MODEL = "base"  # whisper model
OLLAMA_URL = "http://localhost:11434/api/generate"

# Initialize Whisper & TTS
whisper_model = whisper.load_model(MODEL)
tts_engine = pyttsx3.init()

import warnings
warnings.filterwarnings("ignore", category=UserWarning)


def record_voice(filename="input.wav"):
    print("🎙️ Recording your voice for 5 seconds...")
    recording = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="int16")
    sd.wait()
    wave_file = wave.open(filename, "wb")
    wave_file.setnchannels(1)
    wave_file.setsampwidth(2)
    wave_file.setframerate(SAMPLE_RATE)
    wave_file.writeframes(recording.tobytes())
    wave_file.close()
    print(f"✅ Recording saved as {filename}")
    return filename

def transcribe_audio(filename="input.wav"):
    print("📝 Transcribing...")
    result = whisper_model.transcribe(filename)
    text = result["text"].strip()
    print(f"You said: {text}")
    return text

def ask_ollama(prompt, model="mistral"):
    print("🤖 Thinking...")
    response = requests.post(
        OLLAMA_URL,
        json={"model": model, "prompt": prompt},
        stream=True
    )
    reply = ""
    for line in response.iter_lines():
        if line:
            try:
                data = json.loads(line.decode("utf-8"))
                if "response" in data:
                    reply += data["response"]
            except json.JSONDecodeError:
                continue
    print(f"Assistant: {reply.strip()}")
    return reply.strip()

def speak(text):
    print("🔊 Speaking...")
    tts_engine.say(text)
    tts_engine.runAndWait()

if __name__ == "__main__":
    audio_file = record_voice()
    user_text = transcribe_audio(audio_file)
    ai_response = ask_ollama(user_text)
    speak(ai_response)
