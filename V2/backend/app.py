from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from sheets_service import update_status

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello! Your Flask app is running."

@app.route("/voice", methods=["POST"])
def voice():
    appointment_id = request.args.get("appointment_id", "")  # Optional ID
    caller = request.values.get("From", "")

    print(f"[DEBUG] Incoming call for appointment_id={appointment_id}, caller={caller}")

    resp = VoiceResponse()
    gather = Gather(
        input="speech",
        action="https://8aecbb83c79c.ngrok-free.app/handle_response",
        method="POST",
        timeout=5
    )
    gather.say("Is your appointment fixed? Please say yes or no after the beep.")
    resp.append(gather)

    # Fallback if no speech is received
    resp.say("We did not receive your response. Goodbye!")
    return Response(str(resp), mimetype="application/xml")

@app.route("/handle_response", methods=["POST"])
def handle_response():
    speech_result = request.values.get("SpeechResult", "").strip().lower()
    caller = request.values.get("From", "").strip()

    print(f"[DEBUG] handle_response called")
    print(f"[DEBUG] Raw SpeechResult: '{speech_result}'")
    print(f"[DEBUG] Caller Number from Twilio: '{caller}'")

    resp = VoiceResponse()

    if any(word in speech_result for word in ["yes", "yep", "yeah", "affirmative"]):
        result = update_status(caller, "Yes")
        print(f"[DEBUG] Sheet update result: {result}")
        resp.say("Thank you! Your appointment is confirmed.")
    elif any(word in speech_result for word in ["no", "nope", "nah", "negative"]):
        result = update_status(caller, "No")
        print(f"[DEBUG] Sheet update result: {result}")
        resp.say("Okay, your appointment is not confirmed.")
    else:
        print("[DEBUG] Could not understand the response.")
        resp.say("Sorry, I did not understand your response.")

    resp.hangup()
    return Response(str(resp), mimetype="application/xml")

if __name__ == "__main__":
    app.run(debug=True)
