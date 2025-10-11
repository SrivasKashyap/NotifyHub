import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.sheets_service import read_appointments, update_status

print("Reading appointments from sheet...")
appointments = read_appointments()
print("Appointments:", appointments)

if appointments:
    print("Updating status of first appointment...")
    result = update_status(2, "Completed")  # Row 2 assuming row 1 is header
    print(result)
else:
    print("No appointments found.")
