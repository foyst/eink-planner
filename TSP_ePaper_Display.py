# The Signal Path - DataPad ePaper Display
# Shahriar Shahramian / November 2018

# import epd7in5_V2
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import time
import requests
import json
import datetime
from todoist_api_python.api import TodoistAPI
import configparser

EPD_WIDTH       = 480
EPD_HEIGHT      = 800

config = configparser.ConfigParser()
config.read('conf.ini')
TODOIST_TOKEN = config['Todoist']['APIToken']
DEBUG_MODE = 1

def main():
        global Debug_Mode; Debug_Mode = 1
        global do_screen_update; do_screen_update = 1
        # global epd; epd = epd7in5_V2.EPD()
        if Debug_Mode == 0:
            epd.init()
        else:
            print('-= Debug Mode =-')
        global todo_response; todo_response = ''
        global cal_width; cal_width = 240
        global line_start; line_start = 48

        # All fonts used in frames
        global font_cal; font_cal = ImageFont.truetype('fonts/FreeMonoBold.ttf', 16)
        global font_day; font_day = ImageFont.truetype('fonts/Roboto-Black.ttf', 110)
        global font_weather; font_weather = ImageFont.truetype('fonts/Roboto-Black.ttf', 20)
        global font_day_str; font_day_str = ImageFont.truetype('fonts/Roboto-Light.ttf', 35)
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

        # while True:
        query_todo_list()
        if (do_screen_update == 1):
            do_screen_update = 0
            refresh_Screen()
            start_time = time.time() + refresh_time
        elif (time.time() - start_time) > 0:
            print('-= General Refresh =-')
            refresh_Screen()
            start_time = time.time() + refresh_time
            # time.sleep(todo_wait)

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

def refresh_Screen():
    global epd
    global todo_response
    global Debug_Mode
    global weather_response

    # Create clean black frames with any existing Bitmaps
    image_black = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 255)
    draw_black = ImageDraw.Draw(image_black)
    
    update_moment = time.strftime("%I") + ':' + time.strftime("%M") + ' ' + time.strftime("%p")
    draw_black.line((250,320,640,320), fill = 0) # Footer for additional items
    draw_black.text((585,370),update_moment,font = font_update_moment, fill = 255) # The update moment in Pooch

    line_location = 20
    for my_task in todo_response:
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

        temp_draw.text((2, line_start + line_location), item, font = font_tasks_list, fill = 0) # Print task strings
        temp_draw.chord((247.5, line_start + 2 + line_location, 257.5, line_start + 12 + line_location), 0, 360, fill = 0) # Draw circle for task priority
        temp_draw.text((250,line_start + 2 + line_location), priority, font = font_tasks_priority, fill = 255) # Print task priority string
        temp_draw.line((250,line_start + 18 + line_location, 640, line_start + 18 + line_location), fill = 0) # Draw the line below the task
        if my_task.due != None:
            temp_draw.rectangle((595,line_start + 2 + line_location, 640, line_start + 18 + line_location), fill = 0) # Draw rectangle for the due date
            temp_draw.text((602.5, line_start + 3.5 + line_location),str(my_task.due.string), font = font_tasks_due_date, fill = 255) # Print the due date of task

        if (due_date < current_date and due_date > 0):
            draw_red = temp_draw
        else:
            draw_black = temp_draw
        line_location += 26
        if (line_start + line_location + 28 >= 320):

            # The placement for extra tasks not shown
            notshown_tasks = '... & ' + str(len(todo_response) - 9) +  ' more ...'
            w_notshown_tasks,h_notshown_tasks = font_tasks_due_date.getsize(notshown_tasks)
            x_nowshown_tasks = 550 + ((640 - 550) / 2) - (w_notshown_tasks / 2)
            draw_black.text((x_nowshown_tasks, line_start + 3.5 + line_location), notshown_tasks,font = font_tasks_due_date, fill = 255) # Print identifier that there are tasks not shown
            break

    if Debug_Mode == 1:
        print('-= Viewing ePaper Frames... =-')
        image_black.save("Black_Frame.png")
        print('-= ...Done =-')
    else:
        print('-= Updating ePaper... =-')
        epd.display(epd.get_frame_buffer(image_black))
        print('-= ...Done =-')
if __name__ == '__main__':
    main()
