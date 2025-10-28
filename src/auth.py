import gspread
from google.oauth2.service_account import Credentials
from pathlib import Path
import os

def authenticate():
    root_dir = Path(__file__).resolve().parent
    cred_path = root_dir.parent / 'credentials/service-account-credentials.json'

    # Set up Google Sheets credentials
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file(cred_path, scopes=SCOPES)
    
    client = gspread.authorize(creds)
    sheet = client.open('tcc-genlog')
    
    return sheet