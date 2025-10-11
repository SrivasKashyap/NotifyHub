from twilio.rest import Client
import gspread

# Twilio credentials
account_sid = 'ACc23cb486bff4052400ea4875c30b02d6'
auth_token = 'f929c022d6741cf66c00aa2ab9080d7d'
twilio_number = '+19862864864'  # Your Twilio phone number (with +)

client = Client(account_sid, auth_token)

# Google Sheets setup
gc = gspread.service_account(filename='config/credentials.json')
sh = gc.open('NotifyHub_Appointments')
worksheet = sh.sheet1  # Or specify your sheet name

def get_numbers():
    # Assuming phone numbers are in first column starting from row 2 (skip header)
    numbers = worksheet.col_values(2)[1:]  # Use column 2 since Phone is 2nd column
    return numbers

def make_calls():
    numbers = get_numbers()
    for number in numbers:
        
        print(f"Calling number: '{number}'")
        call = client.calls.create(
            url='https://8aecbb83c79c.ngrok-free.app/voice',  # Your public /voice endpoint
            to=number,
            from_=twilio_number
        )
        print(f"Call SID: {call.sid}")

if __name__ == "__main__":
    make_calls()
