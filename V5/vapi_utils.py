import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

VAPI_API_KEY = os.getenv("VAPI_API_KEY")
ASSISTANT_ID = os.getenv("VAPI_ASSISTANT_ID")
PHONE_NUMBER_ID = os.getenv("VAPI_PHONE_NUMBER_ID")
DEFAULT_COUNTRY_CODE = os.getenv("DEFAULT_COUNTRY_CODE", "+91")

BASE_URL = "https://api.vapi.ai/call"


def normalize_phone_number(number: str, country_code: str = DEFAULT_COUNTRY_CODE) -> str:
    """Convert a plain number into E.164 format."""
    number = str(number).strip()
    if number.startswith("+"):
        return number
    if number.startswith("0"):
        number = number[1:]
    return f"{country_code}{number}"


def make_call(phone_number: str, name: str, date: str, time: str):
    """Place an outbound call via Vapi. Only include allowed fields."""
    phone_number = normalize_phone_number(phone_number)

    url = BASE_URL
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }

    # Only send allowed fields
    payload = {
        "assistantId": ASSISTANT_ID,
        "phoneNumberId": PHONE_NUMBER_ID,
        "customer": {
            "number": phone_number
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code in (200, 201):
        print(f"✅ Call triggered successfully for {name} at {phone_number}")
        return response.json()
    else:
        print(f"❌ Failed to trigger call: {response.text}")
        return None
