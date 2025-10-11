from twilio.rest import Client

# Replace with your actual Twilio credentials
ACCOUNT_SID = 'ACc23cb486bff4052400ea4875c30b02d6'
AUTH_TOKEN = 'f929c022d6741cf66c00aa2ab9080d7d'
TWILIO_NUMBER = '+19862864864'  # Your Twilio number

client = Client(ACCOUNT_SID, AUTH_TOKEN)

def make_call(to_number, message):
    """Makes a voice call and speaks the given message using Twilio TTS."""
    call = client.calls.create(
        to=to_number,
        from_=TWILIO_NUMBER,
        twiml=f'<Response><Say voice="alice">{message}</Say></Response>'
    )
    print(f"Call initiated to {to_number}. Call SID: {call.sid}")
