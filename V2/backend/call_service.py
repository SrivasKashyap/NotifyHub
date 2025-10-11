import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_PHONE_NUMBER")

client = Client(account_sid, auth_token)

def make_call(to_phone, appointment_id):
    """
    Initiates a call to the given phone number and asks Yes/No question.
    appointment_id will be sent so we can update the correct row.
    """
    ngrok_url = os.getenv("NGROK_URL")  # Public URL for webhook
    call = client.calls.create(
        to=to_phone,
        from_=twilio_number,
        url=f"{ngrok_url}/voice?appointment_id={appointment_id}"
    )
    print(f"Call initiated: {call.sid}")
