from sheets_service import read_numbers, update_status
from twilio_service import make_call

if __name__ == "__main__":
    print("Fetching pending numbers from Google Sheet...")
    numbers = read_numbers()

    if not numbers:
        print("No pending numbers found.")
    else:
        for name, phone, idx in numbers:
            print(f"Placing call to {name} — {phone} (Row {idx+2})")
            try:
                sid = make_call(phone, name)
                update_status(idx, f"Call placed (SID: {sid})")
                print(f"Call placed successfully, SID: {sid}")
            except Exception as e:
                update_status(idx, f"Call failed: {e}")
                print(f"Error placing call: {e}")

    
