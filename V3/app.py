import os
import subprocess
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse
import whisper
import requests

app = Flask(__name__)

# Load Whisper tiny model for fastest transcription
whisper_model = whisper.load_model("tiny")

# AI model
AI_MODEL = "phi3:mini"  # fast small model suitable for short real-time answers

# Twilio credentials
TWILIO_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")

def download_recording(url, filename="input.mp3"):
    """Download Twilio recording with authentication"""
    for ext in ["mp3", "wav"]:
        try:
            r = requests.get(f"{url}.{ext}", auth=(TWILIO_SID, TWILIO_TOKEN))
            if r.status_code == 200:
                with open(filename, "wb") as f:
                    f.write(r.content)
                print(f"🎙️ Recording saved as {filename} ({ext})")
                return filename
        except Exception as e:
            print("Download error:", e)
    raise Exception("Failed to download recording")

def run_ai_pipeline(audio_file):
    """Transcribe and query AI for very short response"""
    try:
        # Step 1: Transcribe
        print("📝 Transcribing...")
        result = whisper_model.transcribe(audio_file)
        user_text = result.get("text", "").strip()
        print("You said:", user_text)

        if not user_text:
            return "I didn't catch that."

        # Step 2: Query AI (force short output)
        prompt = f"Answer in 1-3 words: {user_text}"
        process = subprocess.Popen(
            ["ollama", "run", AI_MODEL],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8"
        )
        try:
            response, _ = process.communicate(input=prompt, timeout=10)  # 10s max
        except subprocess.TimeoutExpired:
            process.kill()
            response = "Too slow."

        return response.strip()

    except Exception as e:
        print("Pipeline error:", e)
        return "Sorry, there was an error."

@app.route("/answer", methods=["POST"])
def answer_call():
    """Initial answer or loop back"""
    resp = VoiceResponse()
    resp.say("Please speak after the beep.")
    resp.record(
        max_length=5,  # short recording to stay within Twilio timeout
        action="/process",
        finish_on_key="*",
        play_beep=True
    )
    return Response(str(resp), mimetype="text/xml")

@app.route("/process", methods=["POST"])
def process_recording():
    """Transcribe + AI + respond, then loop"""
    recording_url = request.form.get("RecordingUrl")
    print(f"Recording available at: {recording_url}")

    # Download recording
    audio_file = download_recording(recording_url)

    # Get AI response
    ai_response = run_ai_pipeline(audio_file)
    print("Assistant:", ai_response)

    resp = VoiceResponse()
    resp.say(ai_response)

    # Short pause before beep for next turn
    resp.pause(length=1)

    # Loop back for next user input
    resp.say("Please speak after the beep.")
    resp.record(
        max_length=5,
        action="/process",
        finish_on_key="*",
        play_beep=True
    )

    return Response(str(resp), mimetype="text/xml")

if __name__ == "__main__":
    app.run(debug=True)
