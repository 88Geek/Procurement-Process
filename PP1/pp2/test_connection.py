import gspread
from google.oauth2.service_account import Credentials

# Path to your credentials.json file
CREDENTIALS_FILE = "credentials.json"

# Define the scope (permissions)
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Authorize
creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

# Open the sheet by ID
SHEET_ID = "1BosXISXJ7rkUr57W3zy8DA7FQJkmDUqt9Fif95AOJq0"
sheet = client.open_by_key(SHEET_ID)

# Get the first worksheet (Form responses usually go here)
worksheet = sheet.get_worksheet(0)

# Fetch the first 5 rows
rows = worksheet.get_all_values()[:5]

print("✅ Connected successfully! Sample rows:")
for row in rows:
    print(row)
