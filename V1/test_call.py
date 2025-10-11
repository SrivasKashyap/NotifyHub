from ai_call_module.sheet_handler import get_phone_numbers, update_call_status
from ai_call_module.call_handler import make_call
from datetime import datetime

# Get data from the sheet
contacts = get_phone_numbers()

# Loop through contacts and call
for index, row in enumerate(contacts, start=2):  # start=2 because row 1 is header
    phone = row.get('Phone')
    name = row.get('Name', 'there')
    message = f"Hello {name}, this is a reminder for your appointment."

    if phone:
        try:
            make_call(phone, message)
            status = "Call Placed"
        except Exception as e:
            print(f"Error calling {phone}: {e}")
            status = "Failed"
    else:
        print(f"Skipping contact without phone: {row}")
        status = "No Number"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    update_call_status(index, status)
