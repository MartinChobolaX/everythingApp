import tkinter as tk
from totododoappa import *

def menu_buttons(self,frame):
        todo_button_habit = tk.Button(frame, text="ToDo List", command=self.show_frame("todo"),width=10)
        todo_button_habit.place(x=10, y=10)

        calendar_button_habit = tk.Button(frame, text="Calendar", command=self.show_frame("calendar"),width=10)
        calendar_button_habit.place(x=100, y=10)
        
        calendar_button_habit = tk.Button(frame, text="Habits", command=self.show_frame("habit"),width=10)
        calendar_button_habit.place(x=190, y=10)