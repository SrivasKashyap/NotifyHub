import os
from twilio.rest import Client
from dotenv import load_dotenv
load_dotenv()


# Load env variables
BASE_URL = os.getenv("BASE_URL", "https://xxxx.ngrok-free.app")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
MY_PHONE_NUMBER = os.getenv("MY_PHONE_NUMBER")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

call = client.calls.create(
    to=MY_PHONE_NUMBER,
    from_=TWILIO_PHONE_NUMBER,
    url=f"{BASE_URL}/voice"
)

print("Placed call. SID:", call.sid)
