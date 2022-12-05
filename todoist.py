import logging
import time
from todoist_api_python.api import TodoistAPI
import datetime
from PIL import ImageFont

logger = logging.getLogger(__name__)

global refresh_time; refresh_time = 900
global line_start; line_start = 48

global font_tasks_list_title; font_tasks_list_title = ImageFont.truetype('fonts/Roboto-Light.ttf', 30)
global font_tasks_list; font_tasks_list = ImageFont.truetype('fonts/tahoma.ttf', 14)
global font_tasks_due_date; font_tasks_due_date = ImageFont.truetype('fonts/tahoma.ttf', 13)
global font_tasks_priority; font_tasks_priority = ImageFont.truetype('fonts/tahoma.ttf', 11)

class TodoistClient:
    def __init__(self, api_token) -> None:
        self.api_token = api_token

    def query_todo_list(self):
        global todo_response
        global do_screen_update
        logger.info('-= Ping ToDo API =-')
        while True:
            try:
                api = TodoistAPI(self.api_token)
                new_todo_response = api.get_tasks(filter = "#ToDo List")
                new_todo_response.sort(key=lambda x: x.order)
                return new_todo_response
            except Exception as error:
                logger.error('-= ToDo API Error - Will Try Again =-')
                logger.error(error)
                time.sleep(refresh_time)


def render_todo_list(todo_response, draw_black, line_location):
    for my_task in todo_response[0:10]:
        item = str(my_task.content)
        priority = str(my_task.priority)

        if (len(item) > 55):
            item = item[0:55] + '...'

        current_date = int(datetime.date.today().strftime('%j')) + (int(time.strftime("%Y")) * 365)
        if my_task.due != None:
            due_date = int(datetime.date(int(str(my_task.due.date).split('-')[0]), int(str(my_task.due.date).split('-')[1]), int(str(my_task.due.date).split('-')[2])).strftime('%j')) + (int(str(my_task.due.date).split('-')[0]) * 365)
            if (due_date < current_date and due_date > 0):
                task_due_date = "OVERDUE"
            else:
                task_due_date = "DUE: " + str(my_task.due.string)

        draw_black.text((20, line_start + line_location), item, font = font_tasks_list, fill = 0) # Print task strings
        draw_black.chord((3.5, line_start + 2 + line_location, 15.5, line_start + 14 + line_location), 0, 360, fill = 0) # Draw circle for task priority
        draw_black.text((7,line_start + 2 + line_location), priority, font = font_tasks_priority, fill = 255) # Print task priority string
        draw_black.line((3,line_start + 20 + line_location, 474, line_start + 20 + line_location), fill = 0) # Draw the line below the task
        if my_task.due != None:
            draw_black.rectangle((380,line_start + line_location, 474, line_start + 19 + line_location), fill = 0) # Draw rectangle for the due date
            draw_black.text((383, line_start + 2 + line_location), task_due_date, font = font_tasks_due_date, fill = 255) # Print the due date of task

        line_location += 26