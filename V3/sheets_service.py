import os
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
from dotenv import load_dotenv

load_dotenv()

SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SPREADSHEET_ID = os.getenv("SHEETS_SPREADSHEET_ID")
RANGE_NAME = os.getenv("SHEETS_RANGE", "Sheet1!A2:C")

# Load service account credentials
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

# Create an authorized session using requests (not httplib2)
authed_session = AuthorizedSession(creds)


def read_numbers():
    """
    Reads rows from Google Sheet and returns [(name, phone, row_index)]
    for rows where Status column is empty.
    """
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/{RANGE_NAME}"
    response = authed_session.get(url)
    response.raise_for_status()
    result = response.json()

    rows = result.get('values', [])
    pending = []
    for idx, row in enumerate(rows):
        if len(row) >= 2 and (len(row) < 3 or not row[2].strip()):
            pending.append((row[0], row[1], idx))
    return pending


def update_status(row_index, status):
    """
    Updates the Status column for the given row index (0-based in range).
    """
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/Sheet1!C{row_index + 2}?valueInputOption=RAW"
    body = {"values": [[status]]}
    response = authed_session.put(url, json=body)
    response.raise_for_status()
    return response.json()
