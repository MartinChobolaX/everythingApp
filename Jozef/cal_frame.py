import tkinter as tk
from tkcalendar import Calendar
from datetime import datetime

class CalendarFrame(tk.Frame):
    def __init__(self, parent, task_list, finished_list):
        super().__init__(parent, width=1280, height=720)
        self.task_list = task_list
        self.finished_list = finished_list
        # super().menu_buttons(self.frm)
        self.calendar = Calendar(
            self,
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day,
            font=("Helvetica", 16),
            background='green',
            foreground='black'
        )
        self.calendar.pack()
        self.calendar.place(x=10, y=50)

        self.tasks_text = tk.Label(self)
        self.tasks_text.place(x=370, y=50)
        self.tasks_text.config(text='Tasks:\n')

        self.selected_tasks_text = tk.Label(self, justify=tk.LEFT)
        self.selected_tasks_text.place(x=370, y=80)

        self.update_task_for_day()
        self.calendar.bind("<<CalendarSelected>>", self.update_task_for_day)

    def update_task_for_day(self, event=None):
        selected_date_str = self.calendar.get_date()
        selected_date = datetime.strptime(selected_date_str, "%m/%d/%y").date()

        tasks = [task_info[0] for task_info in self.task_list if task_info[2] == str(selected_date)]
        label_text = "\n".join(tasks)
        self.selected_tasks_text.config(text=label_text, wraplength=300)

        self.update_finished_counts_plot()  # Update the finished tasks plot
