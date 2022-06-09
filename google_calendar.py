import os
from httplib2 import Credentials
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import logging
from PIL import Image
from PIL import ImageFont
from dateutil import parser

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

global line_start; line_start = 48

global font_tasks_list; font_tasks_list = ImageFont.truetype('fonts/tahoma.ttf', 14)
global font_update_moment; font_update_moment = ImageFont.truetype('fonts/tahoma.ttf', 14)
global font_quote_text; font_quote_text = ImageFont.truetype('fonts/tahoma.ttf', 18)
global font_calendar_time; font_calendar_time = ImageFont.truetype(font='fonts/tahoma.ttf', size=18)

logger = logging.getLogger(__name__)
EPD_WIDTH       = 480

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

        events = list(map(lambda event: { "summary": event['summary'], "start": event['start'] },
            service.events().list(calendarId='primary', timeMin=now, timeMax=today_end,
                                            maxResults=10, singleEvents=True,
                                            orderBy='startTime', maxAttendees=1).execute().get('items', [])))
    except BaseException as err:
        return ({}, err)
    
    return (events, '')


def render_calendar(calendar_result, draw_black, image_black):
    calendar_response, calendar_error = calendar_result

    line_location = 390
    if (calendar_error):
        logger.error(calendar_error)
        error_icon = Image.open('error_icon.png')
        image_black.paste(error_icon, (190, line_start + line_location))
        draw_black.text((10, 530), "Error retrieving calendar: \n" + str(calendar_error), font = font_tasks_list, fill = 0) # Print event summary
    else:
        calendar_events = calendar_response
        if len(calendar_events) == 0:
            empty_calendar_text = "No more events today"
            w, h = draw_black.textsize(empty_calendar_text, font=font_quote_text)
            draw_black.text(((EPD_WIDTH-w)/2, 450), empty_calendar_text, font = font_quote_text, fill = 0)
        else:
            for event in calendar_events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                start_time = parser.parse(start).time().strftime("%H:%M")
                summary = event['summary']

                draw_black.text((10, line_start + line_location), start_time, font = font_calendar_time, fill = 0) # Print event start date
                draw_black.text((70, line_start + line_location + 6), summary, font = font_tasks_list, fill = 0) # Print event summary
                line_location += 26