import os
from dotenv import load_dotenv
import gspread
status_col_idx = 3  # if "Status" is in column C


load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

spreadsheet_id = os.getenv("SPREADSHEET_ID")
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if not spreadsheet_id:
    raise ValueError("SPREADSHEET_ID not found in .env file")
if not credentials_path:
    raise ValueError("GOOGLE_APPLICATION_CREDENTIALS not found in .env file")

gc = gspread.service_account(filename=credentials_path)
sh = gc.open_by_key(spreadsheet_id)
worksheet = sh.sheet1

def normalize_number(number: str) -> str:
    """Strip spaces, plus signs, and leading zeros for matching."""
    return "".join(filter(str.isdigit, str(number)))

def update_status(phone_number: str, new_status: str):
    target_num = normalize_number(phone_number)
    print(f"[DEBUG] Normalized caller number: '{target_num}'")

    records = worksheet.get_all_records()
    for idx, record in enumerate(records, start=2):
        sheet_num = normalize_number(record.get('Phone', ''))
        print(f"[DEBUG] Row {idx}: sheet='{sheet_num}' vs caller='{target_num}'")

        if sheet_num == target_num or sheet_num.endswith(target_num[-6:]) or target_num.endswith(sheet_num[-6:]):
            worksheet.update_cell(idx, status_col_idx, new_status)
            return f"✅ Updated row {idx} for {phone_number} with status '{new_status}'"

    return f"❌ No match for {phone_number} in sheet."



