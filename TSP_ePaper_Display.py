# The Signal Path - DataPad ePaper Display
# Shahriar Shahramian / November 2018

from logging.handlers import RotatingFileHandler
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
import logging

EPD_WIDTH       = 480
EPD_HEIGHT      = 800

config = configparser.ConfigParser()
config.read('conf.ini')
TODOIST_TOKEN = config['Todoist']['APIToken']

logging.basicConfig(level=logging.INFO)
handler = RotatingFileHandler("epaper-dashboard.log", maxBytes=104857600, backupCount=10)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logging.getLogger('').addHandler(handler)

logger = logging.getLogger(__name__)

def main():
        logger.info("epaper-dashboard starting up...")
        global Debug_Mode; Debug_Mode = int(config['General']['DebugMode'])
        global do_screen_update; do_screen_update = 1
        global epd
        if Debug_Mode == 0:
            import epd7in5_V2
            epd = epd7in5_V2.EPD()
        else:
            logger.info('-= Debug Mode =-')
        global todo_response; todo_response = ''
        global calendar_result; calendar_result = ''
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
        global font_tasks_list; font_tasks_list = ImageFont.truetype('fonts/tahoma.ttf', 14)
        global font_tasks_due_date; font_tasks_due_date = ImageFont.truetype('fonts/tahoma.ttf', 11)
        global font_tasks_priority; font_tasks_priority = ImageFont.truetype('fonts/tahoma.ttf', 11)
        global font_update_moment; font_update_moment = ImageFont.truetype('fonts/tahoma.ttf', 14)

        global font_calendar_time; font_calendar_time = ImageFont.truetype(font='fonts/tahoma.ttf', size=18)

        global todo_wait; todo_wait = 300
        global refresh_time; refresh_time = 900

        try:
            while True:
                query_todo_list()
                calendar_result = query_google_calendar()
                if (do_screen_update == 1):
                    do_screen_update = 0
                    refresh_screen(calendar_result)
                else:
                    logger.info('-= No changes detected, not refreshing screen =-')
                time.sleep(todo_wait)
        except KeyboardInterrupt:
            logger.info('-= Exiting... =-')
            if Debug_Mode == 0:
                epd.sleep()
        

def query_todo_list():
    global todo_response
    global do_screen_update
    logger.info('-= Ping ToDo API =-')
    while True:
        try:
            api = TodoistAPI(TODOIST_TOKEN)
            new_todo_response = api.get_tasks()
            break
        except Exception as error:
            logger.error('-= ToDo API Error - Will Try Again =-')
            logger.error(error)
            time.sleep(refresh_time)
    if ((new_todo_response) != (todo_response)):
        logger.info('-= Task List Change Detected =-')
        do_screen_update = 1
        todo_response = new_todo_response
        return True

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def query_google_calendar():
    global calendar_result
    global do_screen_update
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    
    try:
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

        events = service.events().list(calendarId='primary', timeMin=now, #timeMax=today_end,
                                            maxResults=10, singleEvents=True,
                                            orderBy='startTime', maxAttendees=1).execute()
    except BaseException as err:
        return ({}, err)
    
    if events != calendar_result:
        logger.info('-= Calendar Change Detected =-')
        do_screen_update = 1
        calendar_result = events
    return (events, '')

def refresh_screen(calendar_result):
    global epd
    global todo_response
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

    draw_black.rectangle((0,0,EPD_WIDTH, 70), fill = 0) # Calender area rectangle
    draw_black.text((90,5),day_str, font = font_day_str, fill = 255) # Day string calender text
    draw_black.text((text_left_indent,-5),day_number, font = font_day, fill = 255) # Day number string text
    draw_black.text((92,37),month_str, font = font_month_str, fill = 255) # Month string text
    
    update_moment = "Last updated: " + time.strftime("%I") + ':' + time.strftime("%M") + ' ' + time.strftime("%p")
    draw_black.text((325,5),update_moment,font = font_update_moment, fill = 255)

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
        temp_draw.chord((3.5, line_start + 2 + line_location, 15.5, line_start + 14 + line_location), 0, 360, fill = 0) # Draw circle for task priority
        temp_draw.text((7,line_start + 2 + line_location), priority, font = font_tasks_priority, fill = 255) # Print task priority string
        temp_draw.line((3,line_start + 20 + line_location, 474, line_start + 20 + line_location), fill = 0) # Draw the line below the task
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

    calendar_response, calendar_error = calendar_result

    if (calendar_error):
        logger.error(calendar_error)
        error_icon = Image.open('error_icon.png')
        image_black.paste(error_icon, (10, line_start + line_location))
        draw_black.text((100, line_start + line_location), "Error retrieving calendar: \n" + str(calendar_error), font = font_tasks_list, fill = 0) # Print event summary
    else:
        calendar_events = calendar_response.get('items', []) 
        if len(calendar_events) == 0:
            draw_black.text((70, line_start + line_location), "No more events today", font = font_tasks_list, fill = 0) # Print event summary
        else:
            for event in calendar_events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                start_time = parser.parse(start).time().strftime("%H:%M")
                summary = event['summary']

                draw_black.text((10, line_start + line_location), start_time, font = font_calendar_time, fill = 0) # Print event start date
                draw_black.text((70, line_start + line_location + 6), summary, font = font_tasks_list, fill = 0) # Print event summary
                line_location += 26
        

    if Debug_Mode == 1:
        logger.info('-= Viewing ePaper Frames... =-')
        image_black.save("Black_Frame.png")
        logger.info('-= ...Done =-')
    else:
        logger.info('-= Updating ePaper... =-')
        epd.init()
        epd.display(epd.getbuffer(image_black))
        epd.sleep()
        logger.info('-= ...Done =-')
if __name__ == '__main__':
    main()
