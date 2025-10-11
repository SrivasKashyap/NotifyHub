# dial.py
import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

ACCOUNT_SID  = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN   = os.getenv("TWILIO_AUTH_TOKEN")
FROM_NUMBER  = os.getenv("TWILIO_PHONE_NUMBER")
TO_NUMBER    = os.getenv("MY_VERIFIED_NUMBER")     # Must be verified on trial
NGROK_URL    = os.getenv("NGROK_URL")              # e.g., https://xxxx.ngrok-free.app

if not all([ACCOUNT_SID, AUTH_TOKEN, FROM_NUMBER, TO_NUMBER, NGROK_URL]):
    raise SystemExit("Missing env vars. Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, MY_VERIFIED_NUMBER, NGROK_URL")

client = Client(ACCOUNT_SID, AUTH_TOKEN)

call = client.calls.create(
    to=TO_NUMBER,
    from_=FROM_NUMBER,
    url=f"{NGROK_URL}/answer"   # Twilio will POST here immediately
)

print("Call SID:", call.sid)
