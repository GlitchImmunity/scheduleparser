import pandas as pd
import smtplib
import tkinter as tk
from tkinter.filedialog import askopenfilename
from icalendar import Calendar, Event, vText
from configparser import ConfigParser
from datetime import datetime, timedelta
from os.path import basename
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

days = ["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"]
hours = {
    "11:45PM": 0,
    "5:45AM": 6,
    "6:00AM": 6,
    "7:00AM": 7,
    "8:00AM": 8,
    "8:45AM": 9,
    "9:00AM": 9,
    "10:00AM": 10,
    "11:00AM": 11,
    "11:45AM": 12,
    "12:00PM": 12,
    "1:00PM": 13,
    "2:00PM": 14,
    "2:45PM": 15,
    "3:00PM": 15,
    "4:00PM": 16,
    "5:00PM": 17,
    "5:45PM": 18,
    "6:00PM": 18,
    "7:00PM": 19,
    "8:00PM": 20,
    "8:45PM": 21,
    "9:00PM": 21,
    "10:00PM": 22,
    "11:00PM": 23,
    "12:00AM": 24,
    "1:00AM": 25,
    "2:00AM": 26,
}

def create_calendar_event(shift, daydict):
    event = Event()
    if "Evergreen" in shift[2]:
        event.add('summary', 'Evergreen Shift')
    elif "Special Shift" in shift[2]:
        event.add('summary', 'Special Shift @ DDFD')
    else:
        event.add('summary', 'DDFD Shift')

    start_time = datetime.strptime(daydict[shift[0]] + " " + shift[1].split('-')[0], '%m/%d/%y %I:%M%p')
    end_time = datetime.strptime(daydict[shift[0]] + " " + shift[1].split('-')[1], '%m/%d/%y %I:%M%p')

    if end_time < start_time and "Evergreen" in shift[2]:
        end_time += timedelta(days=1)
    elif end_time < start_time and "DDFD" in shift[2]:
        start_time -= timedelta(days=1)

    event.add('dtstart', start_time)
    event.add('dtend', end_time)
    event['location'] = vText('UCLA')

    return event

def special_schedule(df, worker, s_e):
    schedule = df.iloc[22: s_e, 0:8]
    shifts = []
    total_hours = 0
    worker_space = worker + " "

    for dayIX in range(1, 8):
        for timeIX in range(len(schedule.index)):
            shift = schedule.iloc[timeIX, dayIX]
            if shift == shift and (worker.lower() == shift.lower()
                                   or (worker_space.lower() in shift.lower()
                                       and ("(" in shift or "@" in shift))):

                day = days[dayIX - 1]
                # Find Time
                found = False
                IX = 1
                time = ""
                while found == False:
                    potential = schedule.iloc[timeIX - IX, dayIX]
                    if "AM".lower() in potential.lower() or "PM".lower() in potential.lower():
                        time = potential
                        found = True
                    IX += 1

                begin = ""
                end = ""
                if " - " in time:
                    begin = time.split(" - ", 1)[0]
                    begin = begin[:-2] + ":00" + begin[-2:].upper()
                    end = time.split(" - ", 1)[1]
                    end = end[:-2] + ":00" + end[-2:].upper()
                else:
                    begin = time.split("-", 1)[0]
                    begin = begin[:-2] + ":00" + begin[-2:].upper()
                    end = time.split("-", 1)[1]
                    end = end[:-2] + ":00" + end[-2:].upper()

                reason = ""
                if worker.lower() != shift.lower():
                    reason = shift.split(worker, 1)[1]
                    reason = "    |###| Please Note:" + reason

                time = begin + "-" + end

                shifts.append([day, time, " @ Special Shift", hours[begin], reason])
                total_hours += hours[end] - hours[begin]

    return shifts, total_hours


def evergreen_schedule(worker, schedule):
    shifts = []
    total_hours = 0
    worker_space = worker + " "

    for dayIX in range(1, 8):
        for timeIX in range(0, 19):
            shift = schedule.iloc[timeIX, dayIX]
            if shift == shift and (worker.lower() == shift.lower()
                                   or (worker_space.lower() in shift.lower()
                                       and ("(" in shift or "@" in shift))):
                day = days[dayIX - 1]
                time = schedule.iloc[timeIX, 0]
                begin = time.split(" - ", 1)[0]
                begin = begin[:-2] + ":00" + begin[-2:]
                end = time.split(" - ", 1)[1]
                end = end[:-2] + ":00" + end[-2:]

                reason = ""
                if worker.lower() != shift.lower():
                    reason = shift.split(worker, 1)[1]
                    reason = "    |###| Please Note:" + reason

                shifts.append([day, [begin, end], " @ Evergreen", hours[begin], reason])
                total_hours += hours[end] - hours[begin]

            elif shift == shift and ("/" in shift):
                if shift.split("/", 1)[0].lower() == worker.lower() or shift.split("/", 1)[1].lower() == worker.lower():
                    day = days[dayIX - 1]
                    time = schedule.iloc[timeIX, 0]
                    begin = time.split(" - ", 1)[0]
                    begin = begin[:-2] + ":00" + begin[-2:]
                    end = time.split(" - ", 1)[1]
                    end = end[:-2] + ":00" + end[-2:]

                    reason = ""

                    shifts.append([day, [begin, end], " @ Evergreen", hours[begin], reason])
                    total_hours += hours[end] - hours[begin]

    for dayIX in days:
        shiftIX = 0
        while shiftIX < (len(shifts) - 1):
            if dayIX.lower() == shifts[shiftIX][0].lower() and dayIX.lower() == shifts[shiftIX + 1][0].lower():
                if shifts[shiftIX][1][1] == shifts[shiftIX + 1][1][0]:
                    shifts[shiftIX][1][1] = shifts[shiftIX + 1][1][1]
                    del shifts[shiftIX + 1]
                    shiftIX -= 1
            shiftIX += 1

    # Reformat to strings
    for shiftIX in shifts:
        begin = shiftIX[1][0]
        end = shiftIX[1][1]
        shiftIX[1] = begin + "-" + end

    return shifts, total_hours


def list_schedule(worker, df, edf, s_e):
    worker_space = worker + " "

    schedule = df.iloc[1:22, 0:8]
    shifts = []
    total_hours = 0

    dates = (schedule.iloc[:,1:8]).columns.values.tolist()

    # Create Day -> Date Dict
    daydict = {}
    for dayIX in range(len(days)):
        daydict[days[dayIX]] = dates[dayIX]

    for dayIX in range(1, 8):
        for timeIX in range(0, 21):
            shift = schedule.iloc[timeIX, dayIX]
            if shift == shift and (worker.lower() == shift.lower()
                                   or (worker_space.lower() in shift.lower()
                                       and ("(" in shift or "@" in shift))):
                day = days[dayIX - 1]
                begin = None
                end = None
                if "BUCKET" in schedule.iloc[timeIX, 0]:
                    time = "6:00PM-9:00PM"
                    begin = "6:00PM"
                    end = "9:00PM"
                else:
                    time = schedule.iloc[timeIX, 0]
                    begin = time.split("-", 1)[0]
                    end = time.split("-", 1)[1]

                reason = ""
                if worker.lower() != shift.lower():
                    reason = shift.split(worker, 1)[1]
                    reason = "    |###| Please Note:" + reason

                shifts.append([day, time, " @ DDFD", hours[begin], reason])
                total_hours += hours[end] - hours[begin]

    # Get Evergreen Schedule
    eschedule = edf.iloc[1:20, 0:8]
    eshifts, ehours = evergreen_schedule(worker, eschedule)
    shifts += eshifts
    total_hours += ehours

    # Special Shifts
    sshifts, shours = special_schedule(df, worker, s_e)
    shifts += sshifts

    # Sort schedule to be chronological
    shifts.sort(key=lambda x: x[3], reverse=False)

    if not shifts:
        print("Not a valid name")
        raise Exception("PLEASE ENTER A VALID NAME")

    # Compile Message + Calendar
    message = ""
    cal = Calendar()

    message += "\n"
    message += str(df.columns.values[0] + "\n")
    message += "Total Main Hours: " + str(total_hours) + "\n"
    if shours != 0:
        message += "Special Shift Hours: " + str(shours) + "    |###| Please note this may be less\n"
    else:
        message += "Special Shift Hours: " + str(shours) + "\n"
    message += "\n"

    counter = 0
    for dayIX in days:
        message += dayIX + " " + dates[counter] + ":\n"

        working = False
        for shiftIX in shifts:
            if dayIX.lower() == shiftIX[0].lower():
                message += shiftIX[1] + shiftIX[2] + shiftIX[4] + "\n"
                cal.add_component(create_calendar_event(shiftIX, daydict))
                working = True
        if not working:
            message += "NO WORK :^)\n"

        message += "\n"
        counter += 1

    return message, cal


if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()  # we don't want a full GUI, so keep the root window from appearing
    file = askopenfilename()  # show an "Open" dialog box and return the path to the selected file
    file = pd.read_csv(file, skiprows=0)
    df = pd.DataFrame(file)

    file = askopenfilename()
    file = pd.read_csv(file, skiprows=0)
    edf = pd.DataFrame(file)

    first_column = df.iloc[:, 0]
    search_end = first_column[first_column == "SUPERVISORS"].index.tolist()[0]
    week = df.columns.values[0]

    config_object = ConfigParser()
    config_object.read("config/config.ini")
    deskers = config_object["deskers"]
    password = config_object["bot_info"]["password"]

    # Compile Messages
    port = 465

    end = """\
That's all! Please check the schedule still in case I made any errors. Have a great day!\n

Sincerely,
Glitch Bot

P.S.
I have included a .ics file that will import to any calendar! If you are on an iPhone, please open
this email in the Apple mail app to import the events.
------------------------------------------------
Beep-Boop. I am a bot created by Blake Gella. If you notice any errors, please contact Blake ASAP!"""

    s = smtplib.SMTP_SSL("smtp.gmail.com", port)
    s.login("glitchimmunitybot@gmail.com", password)
    for deskerIX in deskers:
        deskerIX = deskerIX.capitalize()
        start = f"""Good afternoon {deskerIX},

I am a bot created by Blake Gella. I am here to report on your correct schedule for the next week!\n"""
        print("Creating Message")
        message, cal = list_schedule(deskerIX, df, edf, search_end)
        print("Message Created. Creating Email")

        msg = MIMEMultipart()
        msg['Subject'] = f"Schedule Delivery for {week}!"
        msg['From'] = 'glitchimmunitybot@gmail.com'
        msg['To'] = deskers[deskerIX]

        message = start + message + end
        msg.attach(MIMEText(message, 'plain'))
        print("Email created. Creating ics file")

        # Create ICS
        # directory = str(Path(__file__).parent.parent) + "/"
        # print("Generating .ics for " + deskerIX + " at", directory)
        # path = os.path.join(directory, deskerIX + " " + week + '.ics')
        f = open(deskerIX + " " + week + '.ics', 'wb')
        f.write(cal.to_ical())
        f.close()

        filename = deskerIX + " " + week + '.ics'
        with open(filename, 'r') as f:
            part = MIMEApplication(f.read(), Name=basename(filename))

        part['Content-Disposition'] = 'attachment; filename="{}"'.format(basename(filename))
        msg.attach(part)
        print("ics file created. Sending Email")

        s.sendmail("glitchimmunitybot@gmail.com", deskers[deskerIX], msg.as_string())
        print("Email sent to " + deskerIX + " @ " + deskers[deskerIX])
        print()
    s.quit()