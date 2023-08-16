import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from datetime import datetime, date, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DayLocator, DateFormatter
from matplotlib.ticker import MaxNLocator
import numpy as np
import os
import json 


class ToDoListApp:
    def __init__(self):
        self.FILENAME = "tasks.json"
        self.FINISHED_FILENAME = "finished_tasks.json"
        self.HABIT_FILENAME = "habits.json"
        self.load_data()
        self.finished_counts = {}
        

        self.root = tk.Tk()
        self.root.title("To-Do List App")
        self.root.resizable(width=False, height=False)

        self.frm = tk.Frame(self.root, width=1280, height=720)
        self.frm.pack_propagate(False)
        self.frm.pack()

        self.root.tk.call('source', 'forest-dark.tcl')
        ttk.Style().theme_use('forest-dark')
        
        self.menu_buttons(self.frm)

        self.current_frame = None  # Initialize current_frame attribute
        self.init_todo_frame()
        self.init_calendar_frame()
        self.init_habit_frame()

        self.root.mainloop()
        
    def show_todo_frame(self):
        self.show_frame(self.todo_frame)
        
    def show_calendar_frame(self):
        self.show_frame(self.calendar_frame)
        self.update_task_for_day()
        
    def show_habit_frame(self):
        self.show_frame(self.habit_frame)

    def show_frame(self, frame):
        if self.current_frame:
            self.current_frame.pack_forget()
        frame.pack()
        self.current_frame = frame
        
    def menu_buttons(self, frame):
        todo_button_habit = tk.Button(frame, text="ToDo List", command=self.show_todo_frame,width=10)
        todo_button_habit.place(x=10, y=10)

        calendar_button_habit = tk.Button(frame, text="Calendar", command=self.show_calendar_frame,width=10)
        calendar_button_habit.place(x=100, y=10)
        
        calendar_button_habit = tk.Button(frame, text="Habits", command=self.show_habit_frame,width=10)
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


    
    # ToDoList frame        
            
    def init_todo_frame(self):
        self.todo_frame = tk.Frame(self.frm, width=1280, height=720)
        self.todo_frame.pack_propagate(False)

        self.menu_buttons(self.todo_frame)

        self.move_button = tk.Button(self.todo_frame, text="-Finished->", command=self.move_to_finished)
        self.move_button.place(x=190, y=200)

        self.add_button = tk.Button(self.todo_frame, text="Add Task", command=self.add_window)
        self.add_button.place(x=100, y=200)
        self.add_window = None

        self.finished_tasks_canvas = tk.Canvas(self.todo_frame, background="#313131")
        self.finished_tasks_canvas.place(x=800, y=25)

        self.finished_fig, self.finished_ax = plt.subplots(figsize=(5, 2))
        self.finished_ax.tick_params(axis='both', colors='white')
        self.finished_fig.set_facecolor("#313131")
        self.finished_ax.set_facecolor("#313131")

        self.finished_plot_canvas = FigureCanvasTkAgg(self.finished_fig, master=self.finished_tasks_canvas)
        self.finished_plot_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.tasks_tree = self.init_treeview()
        self.finished_tasks = self.init_finished_tasks()
 
    def init_treeview(self):
        columns = [("task", "Task", 200), ("importance", "Importance", 80), ("added", "Added", 80), ("expected", "Expected Finish", 120)]
        tasks_tree = ttk.Treeview(self.todo_frame, columns=[col[0] for col in columns], show="headings", height=20)
        tasks_tree.place(x=5, y=240)

        for col, col_text, col_width in columns:
            tasks_tree.heading(col, text=col_text)
            tasks_tree.column(col, width=col_width)

        for task_info in reversed(self.task_list):
            task, task_date_str, expected_date_str, importance = task_info
            task_date = datetime.strptime(task_date_str, '%Y-%m-%d').date()  # Convert to datetime.date
            expected_date = datetime.strptime(expected_date_str, '%Y-%m-%d').date()  # Convert to datetime.date
            tasks_tree.insert("", "0", values=(task, importance, task_date, expected_date))

        return tasks_tree

    def init_finished_tasks(self):
        finished_columns = [("task", "Task", 200), ("completion_date", "Completion Date", 120), ("duration", "Duration (days)", 100)]
        finished_tasks = ttk.Treeview(self.todo_frame, columns=[col[0] for col in finished_columns], show="headings", height=20)
        finished_tasks.place(x=800, y=240)

        for col, col_text, col_width in finished_columns:
            finished_tasks.heading(col, text=col_text)
            finished_tasks.column(col, width=col_width)

        for finished_task_info in reversed(self.finished_list):
            task, completion_date_str, completion_duration, expected_date_str, importance = finished_task_info
            completion_date = datetime.strptime(completion_date_str, '%Y-%m-%d').date()  # Convert to datetime.date
            expected_date = datetime.strptime(expected_date_str, '%Y-%m-%d').date()  # Convert to datetime.date
            completion_duration = (completion_date - expected_date).days
            finished_tasks.insert("", "end", values=(task, completion_date_str, completion_duration))

        return finished_tasks

    def add_window(self):
        if self.add_window is not None:
            return

        self.add_window = tk.Toplevel()
        self.add_window.title("Add Task")
        self.add_window.resizable(width=False, height=False)

        task_frame = tk.Frame(self.add_window, width=400, height=300)
        task_frame.pack_propagate(False)
        task_frame.pack()

        add_entry = tk.Entry(task_frame)
        add_entry.pack()

        date_label = tk.Label(task_frame, text="Expected Finish Date:")
        date_label.pack()

        calendar_widget = Calendar(task_frame, selectmode="day", year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)
        calendar_widget.pack()

        importance_label = tk.Label(task_frame, text="Importance:")
        importance_label.pack()

        importance_slider = tk.Scale(task_frame, from_=1, to=5, orient=tk.HORIZONTAL)
        importance_slider.pack()

        confirm_button = tk.Button(task_frame, text="Add", command=lambda: self.add_task(add_entry.get(), calendar_widget.get_date(), importance_slider.get()))
        confirm_button.pack()

        self.add_window.protocol("WM_DELETE_WINDOW", self.close_add_window)

    def add_task(self, task, expected_date_str, importance):
        task_date = datetime.now().date()  # Use current date
        expected_date = datetime.strptime(expected_date_str, "%m/%d/%y").date()
        self.task_list.insert(0, (task, task_date.strftime('%Y-%m-%d'), expected_date.strftime('%Y-%m-%d'), importance))
        self.tasks_tree.insert("", "0", values=(task, importance, task_date.strftime('%Y-%m-%d'), expected_date.strftime('%Y-%m-%d')))
        self.save_data()
        self.close_add_window()

    def close_add_window(self):
        if self.add_window is not None:
            self.add_window.destroy()
            self.add_window = None

    def move_to_finished(self):
        selected_task_index = self.tasks_tree.selection()
        if selected_task_index and self.task_list:
            selected_item = self.tasks_tree.item(selected_task_index)
            task = selected_item["values"][0]
            selected_index = self.tasks_tree.index(selected_task_index[0])
            task_info = self.task_list.pop(selected_index)
            self.tasks_tree.delete(selected_task_index)

            completion_date = datetime.now().date()
            completion_date_str = completion_date.strftime('%Y-%m-%d')
            task_date = datetime.strptime(task_info[1], '%Y-%m-%d').date()  # Convert to datetime.date
            completion_duration = (completion_date - task_date).days  # Perform subtraction on datetime.date objects

            finished_task_info = (task, completion_date_str, completion_duration, task_info[2], task_info[3])

            self.finished_list.append(finished_task_info)
            self.finished_tasks.insert("", "end", values=(task, completion_date_str, completion_duration))
            self.update_finished_counts_plot()
            self.save_data()

    def update_finished_counts_plot(self):
        today = datetime.now().date()
        week_ago = today - timedelta(days=6)
        dates = [week_ago + timedelta(days=i) for i in range(7)]

        finished_counts = {date: 0 for date in dates}
        for finished_task_info in self.finished_list:
            completion_date_str = finished_task_info[1]  # Extract completion date as string
            completion_date = datetime.strptime(completion_date_str, '%Y-%m-%d').date()  # Convert to datetime.date
            if week_ago <= completion_date <= today:
                finished_counts[completion_date] += 1

        self.finished_ax.clear()
        self.finished_ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        self.finished_ax.xaxis.set_major_locator(DayLocator(interval=1))
        self.finished_ax.xaxis.set_major_formatter(DateFormatter('%d'))
        self.finished_ax.plot(dates, finished_counts.values(), marker='o', color="#217346")
        self.finished_ax.set_xlabel('Date')
        self.finished_ax.xaxis.label.set_color('white')
        self.finished_ax.set_ylabel('Finished Tasks Count')
        self.finished_ax.yaxis.label.set_color('white')
        self.finished_ax.set_title('Finished Tasks Over Time', color='white')

        self.finished_plot_canvas.draw()


    
    # calendar frame
    
    def init_calendar_frame(self):
        self.calendar_frame = tk.Frame(self.frm, width=1280, height=720)
        self.calendar_frame.pack_propagate(False)

        self.menu_buttons(self.calendar_frame)

        self.calendar = Calendar(self.calendar_frame,
                                 year=datetime.now().year,
                                 month=datetime.now().month,
                                 day=datetime.now().day,
                                 font=("Helvetica", 16),
                                 background='green',
                                 foreground='black')
        self.calendar.pack()
        self.calendar.place(x=10, y=50)
        

        self.tasks_text = tk.Label(self.calendar_frame)
        self.tasks_text.place(x=370, y=50)
        self.tasks_text.config(text='Tasks:\n')
        #self.tasks_text.pack()
        self.selected_tasks_text = tk.Label(self.calendar_frame, justify=tk.LEFT)
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


    # habit frame
    
    def init_habit_frame(self):
        self.habit_frame = tk.Frame(self.frm, width=1280, height=720)
        self.habit_frame.pack_propagate(False)
        
        self.menu_buttons(self.habit_frame)
        
        self.load_data()
        
        
        self.enter_habit_button = tk.Button(self.habit_frame, text="Add habit", command=self.add_habit_window)
        self.enter_habit_button.place(x=100,y=200)
        self.add_habit_window = None
        
        
        for i, habit in enumerate(self.habits):
            habit_label = tk.Label(self.habit_frame, text=habit["name"])
            habit_label.grid(row=i, column=0, padx=10, pady=5)

            streak_label = tk.Label(self.habit_frame, text=f"Streak: {habit['streak']}")
            streak_label.grid(row=i, column=1, padx=10, pady=5)

            habit["completed_today"] = tk.BooleanVar(value=False)
            check_button = tk.Checkbutton(self.habit_frame, variable=habit["completed_today"], command=lambda h=habit: self.update_completion(h))
            check_button.grid(row=i, column=2, padx=10, pady=5)

            duration_label = tk.Label(self.habit_frame, text=f"Duration: {habit['duration']}")
            duration_label.grid(row=i, column=3, padx=10, pady=5)

    def update_completion(self, habit):
        habit["completed_today"] = not habit["completed_today"]

        if habit["completed_today"]:
            habit["streak"] += 1
        else:
            habit["streak"] = 0

        self.refresh_habit_display()
    
    def refresh_habit_display(self):
        for i, habit in enumerate(self.habits):
            streak_label = tk.Label(self.habit_frame, text=f"Streak: {habit['streak']}")
            streak_label.grid(row=i, column=1)
    
    def add_habit_window(self):
        if self.add_habit_window is not None:
            return

        self.add_habit_window = tk.Toplevel()
        self.add_habit_window.title("Add habit")
        self.add_habit_window.resizable(width=False, height=False)

        habit_frame = tk.Frame(self.add_habit_window, width=400, height=300)
        habit_frame.pack_propagate(False)
        habit_frame.pack()

        habit_name_label = tk.Label(habit_frame, text="Habit Name:")
        habit_name_label.pack()
        self.add_habit_entry = tk.Entry(habit_frame)
        self.add_habit_entry.pack()

        # Habit Type (Binary/Completion or Quantity/Progress)
        self.habit_type_var = tk.StringVar()
        self.habit_type_var.set("binary")
        self.habit_type_label = tk.Label(habit_frame, text="Habit Type:")
        self.habit_type_label.pack()

        binary_checkbutton = tk.Checkbutton(
            habit_frame, text="Binary", variable=self.habit_type_var, onvalue="binary", offvalue=""
        )
        binary_checkbutton.pack()

        quantity_checkbutton = tk.Checkbutton(
            habit_frame, text="Quantity", variable=self.habit_type_var, onvalue="quantity", offvalue=""
        )
        quantity_checkbutton.pack()

        # Bind the Checkbuttons to update the UI based on the selected habit type
        binary_checkbutton.bind("<<CheckbuttonSelected>>", self.update_habit_type_ui)
        quantity_checkbutton.bind("<<CheckbuttonSelected>>", self.update_habit_type_ui)

        self.habit_type_ui_frame = tk.Frame(habit_frame)
        self.habit_type_ui_frame.pack()

        # Habit Frequency (Daily, Weekly, etc.)
        self.habit_frequency_var = tk.StringVar()
        self.habit_frequency_label = tk.Label(
            self.habit_type_ui_frame, text="Habit Frequency:"
        )
        self.habit_frequency_label.pack()
        self.habit_frequency_menu = tk.OptionMenu(
            self.habit_type_ui_frame, self.habit_frequency_var, "Daily", "Weekly"
        )
        self.habit_frequency_menu.pack()

        # Habit Quantity (only for Quantity/Progress habits)
        self.habit_quantity_label = tk.Label(
            self.habit_type_ui_frame, text="Habit Quantity:"
        )
        self.habit_quantity_label.pack()
        self.habit_quantity_entry = tk.Entry(self.habit_type_ui_frame)
        self.habit_quantity_entry.pack()

        # Bind the Checkbutton to the completion update function
        add_habit_button = tk.Button(
            habit_frame, text="Add", command=self.add_habit
        )
        add_habit_button.pack()

    # Rest of your code...

    def update_habit_type_ui(self, event):
        habit_type = self.habit_type_var.get()

        if habit_type == "binary":
            self.habit_frequency_label.pack(in_=self.habit_type_ui_frame)
            self.habit_frequency_menu.pack(in_=self.habit_type_ui_frame)
            self.habit_quantity_label.pack_forget()
            self.habit_quantity_entry.pack_forget()
        elif habit_type == "quantity":
            self.habit_frequency_label.pack_forget()
            self.habit_frequency_menu.pack_forget()
            self.habit_quantity_label.pack(in_=self.habit_type_ui_frame)
            self.habit_quantity_entry.pack(in_=self.habit_type_ui_frame)

        
        
        
        
        
    def add_habit(self):
        habit_name = self.add_habit_entry.get()
        habit_option = self.option_var
        
        






if __name__ == "__main__":
    app = ToDoListApp()
