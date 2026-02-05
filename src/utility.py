from datetime import datetime, date

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

EAS_ENTRY_STD_DEV = 0.02

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

def format_date(d: str):
    if (not d.isdigit()):
        return d
    else:
        if (len(d) < 6):
            d = '0' + d
        d_date = datetime.strptime(d, DATE_READ_FORMAT)
        return datetime.strftime(d_date, DATE_WRITE_FORMAT)
