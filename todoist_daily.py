import logging
import math
import time
from todoist_api_python.api import TodoistAPI
import datetime
from PIL import ImageFont

logger = logging.getLogger(__name__)
EPD_WIDTH       = 480

global refresh_time; refresh_time = 900
global line_start; line_start = 30

global font_tasks_list_title; font_tasks_list_title = ImageFont.truetype('fonts/Roboto-Light.ttf', 30)
global font_tasks_list; font_tasks_list = ImageFont.truetype('fonts/tahoma.ttf', 14)
global font_tasks_due_date; font_tasks_due_date = ImageFont.truetype('fonts/tahoma.ttf', 13)
global font_tasks_priority; font_tasks_priority = ImageFont.truetype('fonts/tahoma.ttf', 11)

class TodoistDailyClient:
    def __init__(self, api_token) -> None:
        self.api_token = api_token

    def query_daily_habits(self):
        global todo_response
        global do_screen_update
        logger.info('-= Ping Daily Habits API =-')
        while True:
            try:
                api = TodoistAPI(self.api_token)
                new_todo_response = api.get_tasks(filter = "#Daily Habits & (overdue | today)")
                new_todo_response.sort(key=lambda x: x.order)
                return new_todo_response
            except Exception as error:
                logger.error('-= Daily Habits API Error - Will Try Again =-')
                logger.error(error)
                time.sleep(refresh_time)


def render_daily_habits(todo_response, draw_black, line_location):
    row_number = 1
    for ordinal, my_task in enumerate(todo_response[0:10]):
        item = str(my_task.content)

        row_number = math.floor(ordinal / 2)
        line_y_position = (line_start * row_number) + line_location
        if (ordinal % 2 == 0):
            draw_black.text((20, line_y_position), item, font = font_tasks_list, fill = 0) # Print task strings
        else:
            draw_black.text((EPD_WIDTH / 2, line_y_position), item, font = font_tasks_list, fill = 0) # Print task strings

    return (line_start * (row_number + 1)) + line_location