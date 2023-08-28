import tkinter as tk
from tkinter import ttk
from datetime import datetime, date
import os
import json
from cal_frame import *
from todo_frame import *
from habit_frame import *


class ToDoListApp:
    def __init__(self):
        self.FILENAME = "Jozef/tasks.json"
        self.FINISHED_FILENAME = "Jozef/finished_tasks.json"
        self.HABIT_FILENAME = "Jozef/habits.json"

        self.load_data()

        self.root = tk.Tk()
        self.root.title("To-Do List App")
        self.root.resizable(width=False, height=False)

        self.frm = tk.Frame(self.root, width=1280, height=720)
        self.frm.pack_propagate(False)
        self.frm.pack()

        self.frames = {}
        self.init_frames()
        self.current_frame = None
        self.menu_buttons(self.frm)
        

        self.root.tk.call('source', 'Jozef/forest-dark.tcl')
        ttk.Style().theme_use('forest-dark')       

        self.root.mainloop()

    def init_frames(self):
        self.frames['todo'] = ToDoFrame(self.frm, self.task_list, self.finished_list)
        self.frames['calendar'] = CalendarFrame(self.frm, self.task_list, self.finished_list)
        self.frames['habit'] = HabitFrame(self.frm, self.habits)
        # self.show_frame('todo')

    def show_frame(self, frame_name):
        if self.current_frame:
            self.current_frame.pack_forget()
        self.frames[frame_name].pack()
        self.current_frame = self.frames[frame_name]
        
    def menu_buttons(self,frame):
        todo_button_habit = tk.Button(frame, text="ToDo List", command=self.show_frame("todo"),width=10)
        todo_button_habit.place(x=10, y=10)

        calendar_button_habit = tk.Button(frame, text="Calendar", command=self.show_frame("calendar"),width=10)
        calendar_button_habit.place(x=100, y=10)
        
        calendar_button_habit = tk.Button(frame, text="Habits", command=self.show_frame("habit"),width=10)
        calendar_button_habit.place(x=190, y=10)
    
    def save_data(self):
        self.save_json_file(self.FILENAME, self.task_list)
        self.save_json_file(self.FINISHED_FILENAME, self.finished_list)
        self.save_json_file(self.HABIT_FILENAME, self.habits)

    def load_data(self):
        self.task_list = self.load_json_file(self.FILENAME)
        self.finished_list = self.load_json_file(self.FINISHED_FILENAME)
        self.habits = self.load_json_file(self.HABIT_FILENAME)
        
        if not os.path.exists(self.FILENAME):
            self.save_data()

        if not os.path.exists(self.FINISHED_FILENAME):
            self.save_data()

        if not os.path.exists(self.HABIT_FILENAME):
            self.save_data()
    
    def save_json_file(self, filename, data):
        with open(filename, "w") as file:
            json.dump(data, file, default=self.json_default)
            
    def load_json_file(self, filename):
        if os.path.exists(filename):
            with open(filename, "r") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    data = []
        else:
            data = []
        return data

    def json_default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif type(obj) is date:
            return obj.strftime('%Y-%m-%d')
        raise TypeError("Object of type {} is not JSON serializable".format(type(obj)))




# FILENAME = "Jozef/tasks.json"
# FINISHED_FILENAME = "Jozef/finished_tasks.json"
# HABIT_FILENAME = "Jozef/habits.json"

if __name__ == "__main__":
    app = ToDoListApp()
