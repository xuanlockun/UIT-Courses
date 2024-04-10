import sys
import requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup
import ics
import os

session =None

def dl():
    with open("account.txt", "r") as f:
        lines = f.readlines()
    if not lines:
        username = input("Tai khoan: ")
        password = input("Mat khau: ")
        with open("account.txt", "w") as f:
            f.write(f"{username}\n{password}")
    else:
        username, password = lines[0].strip(), lines[1].strip()
    url = "https://courses.uit.edu.vn/login/index.php"
    global session
    session = requests.session()
    response = session.get(url)

    soup = BeautifulSoup(response.content, "html.parser")
    logintoken = soup.find("input", attrs={"name": "logintoken"}).get("value")
    payload = {
        "anchor": "",
        "logintoken": logintoken,
        "username": username,
        "password": password
    }

    response = session.post(url, data=payload)

    cookies = session.cookies
    login_response_soup = BeautifulSoup(response.content, "html.parser")
    login_info = login_response_soup.find("div", class_="logininfo")
    sesskey = login_info.find("a", href=lambda href: href and "logout" in href)["href"].split("=")[-1]
    moodle_session = cookies.get("MoodleSession")
    moodle_id = cookies.get("MOODLEID1_")

    url1 = "https://courses.uit.edu.vn/calendar/export.php?"
    data1 = {
        "sesskey": sesskey,
        "_qf__core_calendar_export_form": "1",
        "events[exportevents]": "all",
        "period[timeperiod]": "recentupcoming",
        "generateurl": "Lấy địa chỉ mạng của lịch"
    }
    headers1 = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"MoodleSession={moodle_session}; MOODLEID1_={moodle_id}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.112 Safari/537.36",
        "Referer": "https://courses.uit.edu.vn/calendar/export.php?"
    }
    response1 = session.post(url1, data=data1, headers=headers1)
    soup = BeautifulSoup(response1.text, "html.parser")
    export_url = soup.find("input", {"id": "calendarexporturl"}).get("value")
    ics_file=requests.get(export_url)
    # print(ics_file.text)

    calendar = ics.Calendar(ics_file.text)
    for event in calendar.events:
        summary = event.name
        print(f"-------------------------------")
        print(f"Nội dung: {summary}")
        due_date = event.end
        utc_now = datetime.now(timezone.utc)
        time_left = due_date - utc_now
        if time_left.total_seconds() >= 0:
            days = time_left.days
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            print(f"Còn lại: {days} ngày, {hours} giờ, {minutes} phút, {seconds} giây")
    print(f"-------------------------------")
    

def help():
    print(f"dl : In ra deadline")
    print(f"Rawr nè :>")

def version():
    print(f"1.0")    

def logout():
    with open("account.txt", "w") as f:
        f.write("")

def hello():
    print(f"_______________________________________")
    print(f"|                                     |")
    print(f"_______________________________________")
    

def main():
    if (sys.argv[1]=="dl"):
        dl()
    elif (sys.argv[1]=="help"):
        help()
    elif (sys.argv[1]=="logout"):
        logout()
    else:
        print(f"Sai lệnh rồi bro")

if __name__ == "__main__":
    main()
