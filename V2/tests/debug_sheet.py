import gspread
from dotenv import load_dotenv
import os

load_dotenv()
gc = gspread.service_account(filename=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
spreadsheet_id = os.getenv("SPREADSHEET_ID")

print("Trying to open sheet:", spreadsheet_id)
try:
    sh = gc.open_by_key(spreadsheet_id)
    print("Sheet opened:", sh.title)
except Exception as e:
    print("Error:", e)
