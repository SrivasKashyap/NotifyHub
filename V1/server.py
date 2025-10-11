from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse
from ai_call_module.sheet_handler import update_call_status_by_number

app = Flask(__name__)

@app.route("/voice", methods=['POST'])
def voice():
    response = VoiceResponse()
    gather = response.gather(num_digits=1, action="/handle-response", method="POST")
    gather.say("Hi. This is a reminder call. Press 1 to confirm. Press 2 to cancel.", voice='alice')
    return Response(str(response), mimetype='text/xml')

@app.route("/handle-response", methods=['POST'])
def handle_response():
    digit = request.form.get('Digits')
    from_number = request.form.get('From')

    if digit == '1':
        status = "Confirmed"
    elif digit == '2':
        status = "Canceled"
    else:
        status = "No response"

    update_call_status_by_number(from_number, status)

    response = VoiceResponse()
    response.say(f"Thank you. Your appointment has been {status.lower()}. Goodbye.", voice='alice')
    return Response(str(response), mimetype='text/xml')

if __name__ == "__main__":
    app.run(port=5000)
