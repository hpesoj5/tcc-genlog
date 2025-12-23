from datetime import date, datetime, timedelta
import os
DATE_FORMAT = "%d%m%y"

def get_details():
    res = {}
    # VEHICLE NUMBER
    res['vehicle_no'] = input("Vehicle number: ")

    # GENERATOR NUMBER
    res['gen'] = input("Gen 1 or 2: ")

    # START AND END GENERATOR STATIONARY RUNTIME
    res['start_val'] = float(input("Last recorded runtime value: "))
    res['end_val'] = float(input("Target runtime value: "))

    # START AND END DATES
    start_date = input("Last recorded date (DDMMYY): ")
    res['start_date'] = datetime.strptime(start_date, DATE_FORMAT).date()
    end_date = input("End date (DDMMYY): ")
    res['end_date'] = datetime.strptime(end_date, DATE_FORMAT).date()

    # DATE OF LAST POL TOP UP
    pol_date = input("Last POL top up date (DDMMYY): ")
    res['pol_date'] = datetime.strptime(pol_date, DATE_FORMAT).date()

    # BOOL TO CHECK IF EACH ENTRY WILL BE 0.5H
    res['fixed'] = True if input("Fix each entry at 0.5h (Y) / amount required to reach target value (N) (Y/N) ").lower() == 'y' else False

    return res

def write_log(vehicle_no, gen, start_val, end_val, start_date, end_date, pol_date, fixed):

    path = os.path.join("genlogs", f"{vehicle_no}_gen{gen}.txt")
    print(path)

    diff = round(end_val - start_val, 2)
    num_weeks = (end_date - start_date).days // 7
    increment = 0.5 if fixed else round((diff) / num_weeks, 2)
    remainder = 0 if fixed else round(diff - num_weeks * increment, 2)

    runtime = 0
    limit = 20 - ((start_date - pol_date)).days // 7 * 0.5
    with open(path, "w") as f:
        while start_date + timedelta(days=7) <= end_date:
            start_date += timedelta(days=7)
            if remainder > 0:
                increment += 0.01
                remainder -= 0.01
                remainder = round(remainder, 2)
            start_val += increment
            runtime += increment
            
            f.write(f"{date.strftime(start_date, '%d/%m/%y')} --------------- EAS ----------------------------- {increment:.2f} ----- {start_val:.2f} ---------\n")
            if runtime >= limit:
                f.write(f"{date.strftime(start_date, '%d/%m/%y')} ----- POL RECEIVED FROM TCC ----- TOP UP POL --------------- {start_val:.2f} ----- 60l\n")
                runtime = 0
                limit = 20
            
            if start_date.month != (start_date + timedelta(days=7)).month:
                f.write(f"---------------- BOOK CLOSED FOR {start_date.strftime('%b').upper()} {start_date.strftime('%Y')} ----------------------------------------------\n")
        
    print(f"Generator logs created for {vehicle_no} Gen {gen}")

def genlog():

    details = get_details() # returns vehicle_no, gen, start_val, end_val, start_date, end_date, pol_date, fixed
    
    write_log(**details)

if __name__ == "__main__":
    genlog()