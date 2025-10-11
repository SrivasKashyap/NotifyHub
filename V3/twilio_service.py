import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

# Load credentials
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_PHONE_NUMBER")

client = Client(account_sid, auth_token)

def make_call(to_number, message="Hello, this is a test call from NotifyHub!"):
    """
    Places a call to the given number and plays a message.
    """
    try:
        call = client.calls.create(
            to=to_number,
            from_=twilio_number,
            twiml=f'<Response><Say>{message}</Say></Response>'
        )
        return call.sid
    except Exception as e:
        print(f"❌ Call failed: {e}")
        return None
