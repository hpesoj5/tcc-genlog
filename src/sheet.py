import gspread
from gspread.cell import Cell
from google.oauth2.service_account import Credentials
from pathlib import Path
from datetime import date, datetime, timedelta
from generators import generators
import streamlit as st
import pandas as pd

def isfloat(str: str) -> bool:
    try:
        float(str)
        return True
    except ValueError:
        return False

def isdate(date: date) -> bool:
    try:
        datetime.strptime(date, DATE_READ_FORMAT).date()
        return True
    except ValueError:
        return False

def authenticate() -> gspread.spreadsheet.Spreadsheet | None:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    try:
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPES)

        client = gspread.authorize(creds)
        sheet = client.open('tcc-genlog')
        print("Google service account authentication success!")

        return sheet

    except Exception as e:
        print(f"Error with Google service account authentication: {e}")
        return None

DATE_READ_FORMAT = '%d%m%y'
DATE_WRITE_FORMAT = '%d%m%y'
DATE_COL = 1
ADDRESS_COL = 2
ENTRY_COL = 3
RUNTIME_COL = 7
READING_COL = 8
FUEL_COL = 10
NAME_COL = 13
NUM_COLS = 13

def format_date(d: str):
    if (not d.isdigit()):
        return d
    else:
        if (len(d) < 6):
            d = '0' + d
        d_date = datetime.strptime(d, DATE_READ_FORMAT)
        return datetime.strftime(d_date, DATE_WRITE_FORMAT)

class Sheet:
    """
    The class for a google sheet tab/sheet. Has functions to read and write data onto the sheet.
    """
    def __init__(self, sheet: gspread.spreadsheet.Spreadsheet, gen: str):
        self.sheet = sheet.worksheet(gen)
        self.data = {} # THIS IS TO STORE DATE AND READING VALUES, ENSURING THAT EACH COLUMN IS CALLED AT MOST ONCE EVERY AUTOFILL QUERY

    def get_latest_date(self) -> date | None:
        """
        Returns the latest entry date, together with the row number. Returns None if no date exists.

        API CALLS: 1
        """
        dates = self.sheet.col_values(DATE_COL)
        self.data['dates'] = dates
        rows = len(dates)
        dates = [date for date in dates if isdate(date)]

        return (datetime.strptime(dates[-1], DATE_READ_FORMAT).date(), rows) if len(dates) > 0 else None

    def get_latest_reading(self) -> float | None:
        """
        Returns the latest entry runtime reading. Returns None if no reading exists.

        API CALLS: 1
        """
        readings = self.sheet.col_values(READING_COL)
        self.data['readings'] = readings
        readings = [float(reading) for reading in readings if isfloat(reading)]

        return readings[-1] if len(readings) > 0 else None

    def get_latest_pol_date_reading(self) -> date | None:
        """
        Returns the last POL top up date, as well as the reading after the top up. Returns None is no top up exists.

        API CALLS: 1-3
        """
        if "dates" not in self.data:
            self.get_latest_date()

        if "readings" not in self.data:
            self.get_latest_reading()

        entries = tuple(zip(self.data['dates'], self.sheet.col_values(ENTRY_COL), self.data['readings']))
        for entry_date, entry, reading in reversed(entries):
            if entry == "TOP UP POL":
                return (datetime.strptime(entry_date, DATE_READ_FORMAT).date(), float(reading))

        return None

    def autofill(self, gen: str, name: str="", end_date: date=date.today()):
        """
        Fills the spreadsheet with 0.5h runtime entries, automatically closes sheets every month and logs POL top ups

        API CALLS: 4
        """
        self.data.clear()
        # GET DATA FROM SHEET
        latest_date = self.get_latest_date() # 1 API CALL
        latest_date, row = latest_date
        latest_reading = self.get_latest_reading() # 1 API CALL
        latest_pol_date_reading = self.get_latest_pol_date_reading() # 1 API CALL

        if latest_date == None or latest_reading == None:
            print("Error: Need at least one runtime entry before autofill")
            return False
        # print(latest_date, latest_reading, latest_pol_date_reading)
        # SET PARAMETERS
        increment = 0.5

        # SET RUNTIME SINCE LAST POL TOP UP AND LIMIT BETWEEN POL TOP UPS
        runtime = 0.0 if latest_pol_date_reading == None else latest_reading - latest_pol_date_reading[1]
        limit = 20.0

        # WRITE TO SPREADSHEET
        cell_list = []

        while latest_date + timedelta(days=7) <= end_date:
            # CLOSE BOOK FOR PREVIOUS MONTH
            if latest_date.month != (latest_date + timedelta(days=7)).month:
                row += 1
                cell_list.append(Cell(row=row, col=ADDRESS_COL, value=f"BOOK CLOSED FOR {latest_date.strftime('%b').upper()} {latest_date.strftime('%Y')}"))

            # INCREMENT EVERYTHING FOR EAS UPDATE
            latest_date += timedelta(days=7)
            latest_reading += increment
            runtime += increment
            row += 1

            cell_list.extend([
                Cell(row=row, col=DATE_COL, value=date.strftime(latest_date, DATE_WRITE_FORMAT)),
                Cell(row=row, col=ADDRESS_COL, value="JC1"),
                Cell(row=row, col=ENTRY_COL, value="EAS"),
                Cell(row=row, col=RUNTIME_COL, value=increment),
                Cell(row=row, col=READING_COL, value=round(latest_reading, 2)),
                Cell(row=row, col=NAME_COL, value=name)
            ])

            # TOP UP POL
            if runtime >= limit:
                row += 1
                cell_list.extend([
                    Cell(row=row, col=DATE_COL, value=date.strftime(latest_date, DATE_WRITE_FORMAT)),
                    Cell(row=row, col=ADDRESS_COL, value="POL RECEIVED FROM TCC"),
                    Cell(row=row, col=ENTRY_COL, value="TOP UP POL"),
                    Cell(row=row, col=READING_COL, value=round(latest_reading, 2)),
                    Cell(row=row, col=FUEL_COL, value="60l"),
                    Cell(row=row, col=NAME_COL, value=name)
                ])
                runtime = 0.0

        if len(cell_list) > 0:
            self.sheet.update_cells(cell_list) # 1 API CALL

        print(f"Autofilled sheet {gen}")
        return True

    def get_sheet_as_df(self) -> pd.DataFrame:
        df = pd.DataFrame(self.sheet.get_all_records())
        df = df.rename(columns={
            "To (State address. Each journey to be written on a separate line)": "Location",
            "Requisitioner's Designation and Purpose": "Purpose",
            "Time": "Started",
            "": "Arrived",
            "Travelling Time in minutes": "Travelling Time/min",
            "Meter reading at journey's end. If not working write \"N.W.\"": "Meter reading",
            "Driver's No. if any and Signature": "Driver's No. & Signature",
            "Name and initials of person accompanying vehicle / authorising the journey": "Name",
        }).drop([0])
        df['Date'] = df['Date'].astype('string').apply(format_date)
        return df
