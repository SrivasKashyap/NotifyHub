import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Define scope for Google Sheets + Drive
SCOPE = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

# Path to your service account key
CREDS_PATH = "credentials/service_account.json"


def get_client():
    """Authenticate and return gspread client."""
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_PATH, SCOPE)
    client = gspread.authorize(creds)
    return client


def get_sheet(sheet_name="Appointments"):
    """Open Google Sheet by name (default: Appointments)."""
    client = get_client()
    sheet = client.open(sheet_name).sheet1  # first worksheet
    return sheet


def get_next_patient(sheet_name="Appointments"):
    """
    Fetch the next patient who has not been called yet.
    Assumes the sheet has columns:
    Name | Phone | Date | Time | Status (Call) | Appointment Confirmed
    """
    sheet = get_sheet(sheet_name)
    records = sheet.get_all_records()

    for idx, row in enumerate(records, start=2):  # start=2 because row 1 is header
        if row.get("Status (Call)", "").strip() == "":
            return {
                "row": idx,
                "name": row.get("Name"),
                "phone": row.get("Phone"),
                "date": row.get("Date"),
                "time": row.get("Time")
            }
    return None  # no patients left


def update_status(row, status, sheet_name="Appointments"):
    """Update the Status (Call) column for a given row number (col 5)."""
    sheet = get_sheet(sheet_name)
    sheet.update_cell(row, 5, status)  # col 5 = Status (Call)
    print(f"📌 Updated call status for row {row} → {status}")


def update_appointment(row, response, sheet_name="Appointments"):
    """Update the Appointment Confirmed column for a given row number (col 6)."""
    sheet = get_sheet(sheet_name)
    sheet.update_cell(row, 6, response)  # col 6 = Appointment Confirmed
    print(f"📌 Updated appointment confirmation for row {row} → {response}")


def update_appointment_by_name(name, response, sheet_name="Appointments"):
    """
    Update the Appointment Confirmed column for a given patient by name.
    This is useful for webhook calls from Vapi.
    """
    sheet = get_sheet(sheet_name)
    records = sheet.get_all_records()

    for idx, row in enumerate(records, start=2):  # skip header
        if row.get("Name", "").strip().lower() == name.strip().lower():
            sheet.update_cell(idx, 6, response)  # col 6 = Appointment Confirmed
            print(f"📌 Updated {name}'s appointment status → {response}")
            return True

    print(f"⚠️ Could not find patient {name} in sheet")
    return False
