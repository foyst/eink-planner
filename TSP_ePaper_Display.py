# The Signal Path - DataPad ePaper Display
# Shahriar Shahramian / November 2018

import epd7in5_V2
import os
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import time
from httplib2 import Credentials
import requests
import json
import datetime
from todoist_api_python.api import TodoistAPI
import configparser
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dateutil import parser

EPD_WIDTH       = 480
EPD_HEIGHT      = 800

config = configparser.ConfigParser()
config.read('conf.ini')
TODOIST_TOKEN = config['Todoist']['APIToken']

def main():
        global Debug_Mode; Debug_Mode = 0
        global do_screen_update; do_screen_update = 1
        global epd; epd = epd7in5_V2.EPD()
        if Debug_Mode == 0:
            epd.init()
        else:
            print('-= Debug Mode =-')
        global todo_response; todo_response = ''
        global calendar_response; calendar_response = ''
        global cal_width; cal_width = 240
        global line_start; line_start = 48

        # All fonts used in frames
        global font_cal; font_cal = ImageFont.truetype('fonts/FreeMonoBold.ttf', 16)
        global font_day; font_day = ImageFont.truetype('fonts/Roboto-Black.ttf', 72)
        global font_section_header; font_section_header = ImageFont.truetype('fonts/Roboto-Black.ttf', 20)
        global font_day_str; font_day_str = ImageFont.truetype('fonts/Roboto-Light.ttf', 25)
        global font_month_str; font_month_str = ImageFont.truetype('fonts/Roboto-Light.ttf', 25)
        global font_weather_icons; font_weather_icons = ImageFont.truetype('fonts/meteocons-webfont.ttf', 45)
        global font_tasks_list_title; font_tasks_list_title = ImageFont.truetype('fonts/Roboto-Light.ttf', 30)
        global font_tasks_list; font_tasks_list = ImageFont.truetype('fonts/tahoma.ttf', 12)
        global font_tasks_due_date; font_tasks_due_date = ImageFont.truetype('fonts/tahoma.ttf', 11)
        global font_tasks_priority; font_tasks_priority = ImageFont.truetype('fonts/tahoma.ttf', 9)
        global font_update_moment; font_update_moment = ImageFont.truetype('fonts/tahoma.ttf', 9)

        global todo_wait; todo_wait = 300
        global refresh_time; refresh_time = 900
        start_time = time.time() + refresh_time

        try:
            while True:
                query_todo_list()
                query_google_calendar()
                if (do_screen_update == 1):
                    do_screen_update = 0
                    refresh_Screen()
                    start_time = time.time() + refresh_time
                elif (time.time() - start_time) > 0:
                    print('-= General Refresh =-')
                    refresh_Screen()
                    start_time = time.time() + refresh_time
                else:
                    print('-= No changes detected, not refreshing screen =-')
                time.sleep(todo_wait)
        except KeyboardInterrupt:
            print('-= Exiting... =-')
            if Debug_Mode == 0:
                epd.sleep()
        

def query_todo_list():
    global todo_response
    global do_screen_update
    print('-= Ping ToDo API =-')
    while True:
        try:
            api = TodoistAPI(TODOIST_TOKEN)
            new_todo_response = api.get_tasks()
            break
        except Exception as error:
            print('-= ToDo API Error - Will Try Again =-')
            print(error)
            time.sleep(refresh_time)
    if ((new_todo_response) != (todo_response)):
        print('-= Task List Change Detected =-')
        do_screen_update = 1
        todo_response = new_todo_response
        return True

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def query_google_calendar():
    global calendar_response
    global do_screen_update
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0, open_browser=False)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build("calendar", "v3", credentials=creds)

    now = datetime.datetime.utcnow().isoformat() + 'Z'
    today_end = datetime.datetime.combine(datetime.datetime.utcnow().date() + datetime.timedelta(1), datetime.datetime.min.time()).isoformat() + 'Z'

    events = service.events().list(calendarId='primary', timeMin=now, timeMax=today_end,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime', maxAttendees=1).execute()
    
    if events != calendar_response:
        print('-= Calendar Change Detected =-')
        do_screen_update = 1
        calendar_response = events
    return True

def refresh_Screen():
    global epd
    global todo_response
    global calendar_response
    global Debug_Mode

    text_left_indent = 3

    # Create clean black frames with any existing Bitmaps
    image_black = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 255)
    draw_black = ImageDraw.Draw(image_black)

    # Calendar strings to be displayed
    day_str = time.strftime("%A")
    day_number = time.strftime("%d")
    month_str = time.strftime("%B") + ' ' + time.strftime("%Y")
    update_moment = time.strftime("%I") + ':' + time.strftime("%M") + ' ' + time.strftime("%p")

    # This section is to center the calendar text in the middle
    w_day_str,h_day_str = font_day_str.getsize(day_str)
    x_day_str = (cal_width / 2) - (w_day_str / 2)

    # The settings for the Calenday today number in the middle
    w_day_num,h_day_num = font_day.getsize(day_number)
    x_day_num = (cal_width / 2) - (w_day_num / 2)

    # The settings for the month string in the middle
    w_month_str,h_month_str = font_month_str.getsize(month_str)
    x_month_str = (cal_width / 2) - (w_month_str / 2)

    draw_black.rectangle((0,0,EPD_WIDTH, 70), fill = 0) # Calender area rectangle
    draw_black.text((90,5),day_str, font = font_day_str, fill = 255) # Day string calender text
    draw_black.text((text_left_indent,-5),day_number, font = font_day, fill = 255) # Day number string text
    draw_black.text((92,37),month_str, font = font_month_str, fill = 255) # Month string text
    
    update_moment = time.strftime("%I") + ':' + time.strftime("%M") + ' ' + time.strftime("%p")
    draw_black.text((585,370),update_moment,font = font_update_moment, fill = 255) # The update moment in Pooch

    draw_black.rectangle((0,70,EPD_WIDTH, 100), fill = 0) # Calender header rectangle
    draw_black.text((text_left_indent, 74), "Prioritised Tasks", font = font_section_header, fill = 255)

    line_location = 70
    for my_task in todo_response[0:10]:
        item = str(my_task.content)
        priority = str(my_task.priority)

        if (len(item) > 55):
            item = item[0:55] + '...'

        current_date = int(datetime.date.today().strftime('%j')) + (int(time.strftime("%Y")) * 365)
        if my_task.due != None:
            due_date = int(datetime.date(int(str(my_task.due.date).split('-')[0]), int(str(my_task.due.date).split('-')[1]), int(str(my_task.due.date).split('-')[2])).strftime('%j')) + (int(str(my_task.due.date).split('-')[0]) * 365)
        else:
            due_date = -1

        if (due_date < current_date and due_date > 0):
            temp_draw = draw_red
        else:
            temp_draw = draw_black

        temp_draw.text((20, line_start + line_location), item, font = font_tasks_list, fill = 0) # Print task strings
        temp_draw.chord((3.5, line_start + 2 + line_location, 13.5, line_start + 12 + line_location), 0, 360, fill = 0) # Draw circle for task priority
        temp_draw.text((6,line_start + 2 + line_location), priority, font = font_tasks_priority, fill = 255) # Print task priority string
        temp_draw.line((3,line_start + 18 + line_location, 474, line_start + 18 + line_location), fill = 0) # Draw the line below the task
        if my_task.due != None:
            temp_draw.rectangle((595,line_start + 2 + line_location, 640, line_start + 18 + line_location), fill = 0) # Draw rectangle for the due date
            temp_draw.text((602.5, line_start + 3.5 + line_location),str(my_task.due.string), font = font_tasks_due_date, fill = 255) # Print the due date of task

        if (due_date < current_date and due_date > 0):
            draw_red = temp_draw
        else:
            draw_black = temp_draw
        line_location += 26
    
    draw_black.rectangle((0,400,EPD_WIDTH, 430), fill = 0) # Calender header rectangle
    draw_black.text((text_left_indent, 404), "Today's Calendar", font = font_section_header, fill = 255)
    line_location = 400
    calendar_events = calendar_response.get('items', []) 
    if len(calendar_events) == 0:
        draw_black.text((70, line_start + line_location), "No more events today", font = font_tasks_list, fill = 0) # Print event summary
    else:
        for event in calendar_events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            start_time = parser.parse(start).time().strftime("%H:%M")
            summary = event['summary']

            draw_black.text((70, line_start + line_location), summary, font = font_tasks_list, fill = 0) # Print event summary
            draw_black.text((20, line_start + line_location), start_time, font = font_tasks_list, fill = 0) # Print event start date
            line_location += 26
        

    if Debug_Mode == 1:
        print('-= Viewing ePaper Frames... =-')
        image_black.save("Black_Frame.png")
        print('-= ...Done =-')
    else:
        print('-= Updating ePaper... =-')
        epd.display(epd.getbuffer(image_black))
        epd.sleep()
        print('-= ...Done =-')
if __name__ == '__main__':
    main()
