# The Signal Path - DataPad ePaper Display
# Shahriar Shahramian / November 2018

from logging.handlers import RotatingFileHandler
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import time
import configparser
import logging

from google_calendar import query_google_calendar, render_calendar
from quotes import render_quotes
from todoist import TodoistClient, render_todo_list
from todoist_daily import TodoistDailyClient, render_daily_habits

EPD_WIDTH       = 480
EPD_HEIGHT      = 800

global config; config = configparser.ConfigParser()
config.read('conf.ini')

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
        global daily_response; daily_response = ''
        global cal_width; cal_width = 240
        global line_start; line_start = 48

        todoist_client = TodoistClient(config['Todoist']['APIToken'])
        todoist_daily_client = TodoistDailyClient(config['Todoist']['APIToken'])

        # All fonts used in frames
        global font_cal; font_cal = ImageFont.truetype('fonts/FreeMonoBold.ttf', 16)
        global font_day; font_day = ImageFont.truetype('fonts/Roboto-Black.ttf', 72)
        global font_section_header; font_section_header = ImageFont.truetype('fonts/Roboto-Black.ttf', 20)
        global font_day_str; font_day_str = ImageFont.truetype('fonts/Roboto-Light.ttf', 25)
        global font_month_str; font_month_str = ImageFont.truetype('fonts/Roboto-Light.ttf', 25)
        global font_tasks_list; font_tasks_list = ImageFont.truetype('fonts/tahoma.ttf', 14)
        global font_update_moment; font_update_moment = ImageFont.truetype('fonts/tahoma.ttf', 14)

        global todo_wait; todo_wait = 300

        try:
            while True:
                new_todo_response = todoist_client.query_todo_list()
                new_calendar_result = query_google_calendar()
                new_daily_response = todoist_daily_client.query_daily_habits()
                if ((new_todo_response) != (todo_response)):
                    logger.info('-= Task List Change Detected =-')
                    do_screen_update = 1
                    todo_response = new_todo_response
                if new_calendar_result != calendar_result:
                    logger.info('-= Calendar Change Detected =-')
                    do_screen_update = 1
                    calendar_result = new_calendar_result
                if new_daily_response != daily_response:
                    logger.info('-= Daily Habits Change Detected =-')
                    do_screen_update = 1
                    daily_response = new_daily_response
                
                if (do_screen_update == 1):
                    do_screen_update = 0
                    refresh_screen(calendar_result, todo_response, daily_response)
                else:
                    logger.info('-= No changes detected, not refreshing screen =-')
                time.sleep(todo_wait)
        except KeyboardInterrupt:
            logger.info('-= Exiting... =-')
            if Debug_Mode == 0:
                epd.sleep()

def refresh_screen(calendar_result, todo_response, daily_response):
    global epd
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

    section_y_position = 70

    draw_black.rectangle((0,section_y_position,EPD_WIDTH, section_y_position + 30), fill = 0) # Todo list header rectangle
    draw_black.text((text_left_indent, section_y_position + 4), "Daily Habits", font = font_section_header, fill = 255)

    # Daily Habits
    section_y_position = render_daily_habits(daily_response, draw_black, section_y_position + 40)  

    # section_y_position = 200

    draw_black.rectangle((0,section_y_position,EPD_WIDTH, section_y_position + 30), fill = 0) # Todo list header rectangle
    draw_black.text((text_left_indent, section_y_position + 4), "Prioritised Tasks", font = font_section_header, fill = 255)

    render_todo_list(todo_response, draw_black, section_y_position - 10)

    section_y_position = section_y_position + 300

    draw_black.rectangle((0,section_y_position,EPD_WIDTH, section_y_position + 30), fill = 0) # Calender header rectangle
    draw_black.text((text_left_indent, section_y_position + 4), "Today's Calendar", font = font_section_header, fill = 255)

    render_calendar(calendar_result, draw_black, image_black, section_y_position)
                
    render_quotes(draw_black)

    if Debug_Mode == 1:
        logger.info('-= Viewing ePaper Frames... =-')
        image_black.save("Black_Frame.png")
        logger.info('-= ...Done =-')
        exit()
    else:
        logger.info('-= Updating ePaper... =-')
        epd.init()
        epd.display(epd.getbuffer(image_black))
        epd.sleep()
        logger.info('-= ...Done =-')
if __name__ == '__main__':
    main()
