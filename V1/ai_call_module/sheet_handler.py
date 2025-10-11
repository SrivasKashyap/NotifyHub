import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Setup the Google Sheets API connection
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Open the sheet
sheet = client.open("Hello").sheet1  # Make sure the sheet name matches

def get_phone_numbers():
    return sheet.get_all_records()

def update_status(row_number, status):
    sheet.update_cell(row_number, 3, status)  # Column C (Status)

def update_timestamp(row_number):
    sheet.update_cell(row_number, 4, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  # Column D (Timestamp)
def update_call_status_by_number(phone_number, status):
    sheet = client.open("Appointments").sheet1
    records = sheet.get_all_records()
    for i, row in enumerate(records):
        if str(row.get("Phone")).endswith(phone_number[-10:]):
            sheet.update_cell(i+2, 3, status)  # Assuming column C is Status
            break
