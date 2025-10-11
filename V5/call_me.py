from sheets_utils import get_next_patient, update_status
from vapi_utils import make_call

def main():
    patient = get_next_patient()

    if not patient:
        print("🎉 No pending patients found in the sheet.")
        return

    print(f"📞 Calling {patient['name']} at {patient['phone']} "
          f"for appointment on {patient['date']} at {patient['time']}...")

    # Call using the correct parameters
    result = make_call(patient["phone"], patient["name"], patient["date"], patient["time"])

    if result:
        update_status(patient["row"], "Called")
        print(f"✅ Updated call status for {patient['name']} → Called")
    else:
        update_status(patient["row"], "Failed")
        print(f"❌ Marked call status for {patient['name']} → Failed")


if __name__ == "__main__":
    main()
