import gspread
from google.oauth2.service_account import Credentials
from pathlib import Path
from datetime import date, datetime
from generators import generators

def authenticate():
    root_dir = Path(__file__).resolve().parent
    cred_path = root_dir.parent / 'credentials/service-account-credentials.json'

    # Set up Google Sheets credentials
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file(cred_path, scopes=SCOPES)
    
    client = gspread.authorize(creds)
    sheet = client.open('tcc-genlog')
    
    return sheet

DATE_WRITE_FORMAT = '%d/%m/%y'
DATE_COL = 1
EVENT_COL = 2
REMARKS_COL = 3
RUNTIME_COL = 4

class Sheet:
    """
    The class for a google sheet tab/sheet. Has functions to read and write data onto the sheet.
    """
    def __init__(self, sheet: gspread.spreadsheet.Spreadsheet, gen: str):
        self.sheet = sheet.worksheet(gen)

    def get_latest_date(self):
        date = self.sheet.col_values(DATE_COL)[-1]
        return datetime.strptime(date, DATE_WRITE_FORMAT).date() if date != "Date" else None
    
    def get_latest_pol_date(self):
        events = zip(self.sheet.col_values(DATE_COL), self.sheet.col_values(EVENT_COL))
        for event_date, event in reversed(events):
            if event == "POL RECEIVED FROM TCC":
                return datetime.strptime(event_date, DATE_WRITE_FORMAT).date()

        return None

    def get_latest_runtime(self):
        res = self.sheet.col_values(RUNTIME_COL)[-1]
        return res if res != "Stationary Runtime" else None
    
    # def autofill(self, end_date: date): # TO FINISH ONCE FORMAT OF LOGBOOK IS KNOWN
    #     latest_date = self.get_latest_date()
    #     latest_pol_date = self.get_latest_pol_date()
    #     latest_runtime = self.get_latest_runtime()

    # def write(self, event_date: date)                  TO WRITE MANUAL ENTRIES E.G. ROT 3

    # def top_up_pol(self, event_date: date):