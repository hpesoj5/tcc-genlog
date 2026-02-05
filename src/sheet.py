import gspread
from gspread.cell import Cell
from google.oauth2.service_account import Credentials
from datetime import date, datetime, timedelta
from utility import isfloat, isdate, format_date, EAS_ENTRY_STD_DEV, DATE_READ_FORMAT, DATE_WRITE_FORMAT, DATE_COL, ADDRESS_COL, ENTRY_COL, RUNTIME_COL, READING_COL, FUEL_COL, NAME_COL
import streamlit as st
import pandas as pd
import numpy as np

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

        if len(dates) == 0:
            return None

        else:
            return (datetime.strptime(dates[-1], DATE_READ_FORMAT).date(), rows)

    def get_latest_reading(self) -> float | None:
        """
        Returns the latest entry runtime reading. Returns None if no reading exists.
        API CALLS: 1
        """
        
        readings = self.sheet.col_values(READING_COL)
        self.data['readings'] = readings
        readings = [float(reading) for reading in readings if isfloat(reading)]

        if len(readings) == 0:
            return None

        else:
            return readings[-1]

    def get_latest_pol_date_reading(self) -> date | None:
        """
        Returns the last POL top up date, as well as the reading after the top up. Returns None is no top up exists.
        API CALLS: 1-3
        """

        if "dates" not in self.data:
            self.get_latest_date()
        if "readings" not in self.data:
            self.get_latest_reading()

        if self.data['dates'] is None or self.data['readings'] is None:
            return None
        
        entries = tuple(zip(self.data['dates'], self.sheet.col_values(ENTRY_COL), self.data['readings']))

        for entry_date, entry, reading in reversed(entries):
            if entry == "TOP UP POL":
                return (datetime.strptime(entry_date, DATE_READ_FORMAT).date(), float(reading))

        return None

    def autofill(self, gen: str, name: str="", end_date: date=date.today(), end_val: int | None = None):
        """
        Fills the spreadsheet with 0.5h runtime entries, automatically closes sheets every month and logs POL top ups
        API CALLS: 4
        """

        self.data.clear()

        # GET DATA FROM SHEET
        latest_date = self.get_latest_date()                            # 1 API CALL
        latest_reading = self.get_latest_reading()                      # 1 API CALL
        latest_pol_date_reading = self.get_latest_pol_date_reading()    # 1 API CALL

        if latest_date is None or latest_reading is None:
            raise ValueError("Sheet needs at least one runtime entry before autofill")

        if end_val is not None and end_val <= latest_reading:
            raise ValueError("Final reading is lower than initial reading")

        # SET PARAMETERS
        latest_date, row = latest_date
        num_weeks = (end_date - latest_date).days // 7

        if end_val is None:
            weekly_average = 0.5
            weekly_increments = np.full(num_weeks, weekly_average)

        else:
            diff = end_val - latest_reading
            weekly_average = diff / num_weeks
            
            deviations = np.random.normal(0, EAS_ENTRY_STD_DEV, num_weeks)

            weekly_increments = weekly_average + deviations

            total_sum = weekly_increments.sum()
            adjustment_factor = diff / total_sum

            weekly_increments *= adjustment_factor
            weekly_increments = np.round(weekly_increments, 2)

            final_adjustment = round(diff - weekly_increments[:-1].sum(), 2)

            weekly_increments[-1] = final_adjustment

            if weekly_increments.min() < 0:
                raise ValueError("Difference between last reading and target reading too small, good luck bro")

        index = 0 # to loop through weekly_increments

        runtime = 0.0 if latest_pol_date_reading is None else latest_reading - latest_pol_date_reading[1] # runtime since last POL top up
        limit = 20.0 # maximum runtime between consecutive POL top ups

        cell_list = []

        while latest_date + timedelta(days=7) <= end_date:

            if latest_date.month != (latest_date + timedelta(days=7)).month: # closes book for previous month
                row += 1
                cell_list.append(Cell(row=row, col=ADDRESS_COL, value=f"BOOK CLOSED FOR {latest_date.strftime('%b').upper()} {latest_date.strftime('%Y')}"))

            # EAS update
            latest_date += timedelta(days=7)
            latest_reading += weekly_increments[index]
            runtime += weekly_increments[index]
            row += 1

            cell_list.extend([
                Cell(row=row, col=DATE_COL, value=date.strftime(latest_date, DATE_WRITE_FORMAT)),
                Cell(row=row, col=ADDRESS_COL, value="JC1"),
                Cell(row=row, col=ENTRY_COL, value="EAS"),
                Cell(row=row, col=RUNTIME_COL, value=weekly_increments[index]),
                Cell(row=row, col=READING_COL, value=round(latest_reading, 2)),
                Cell(row=row, col=NAME_COL, value=name)
            ])

            # top up POL
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

            index += 1

        if len(cell_list) > 0:
            self.sheet.update_cells(cell_list) # 1 API CALL

        print(f"Autofill generator {gen} success!") # debug text
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
