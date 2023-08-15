import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DayLocator, DateFormatter
import numpy as np

class ToDoListApp:
    def __init__(self):
        self.FILENAME = "tasks.txt"
        self.FINISHED_FILENAME = "finished_tasks.txt"
        self.task_list = []
        self.task_dict = {}
        self.finished_list = []
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

        self.init_calendar_frame()
        self.init_todo_frame()
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
        
        # Create Matplotlib figure and canvas
        self.finished_tasks_canvas = tk.Canvas(self.todo_frame, background="#313131")
        self.finished_tasks_canvas.place(x=800, y=25)
        self.finished_fig, self.finished_ax = plt.subplots(figsize=(5,2))
        self.finished_ax.tick_params(axis='both', colors='white')
        self.finished_fig.set_facecolor("#313131")
        self.finished_ax.set_facecolor("#313131")
        self.finished_plot_canvas = FigureCanvasTkAgg(self.finished_fig, master=self.finished_tasks_canvas)
        self.finished_plot_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.task_list = self.load_tasks()
        self.finished_list = self.load_finished_tasks()  # Load finished tasks
        self.update_finished_counts_plot()
        self.tasks_tree = self.init_treeview()
        self.finished_tasks = self.init_finished_tasks()
        
    def init_treeview(self):
        tasks_tree = ttk.Treeview(self.todo_frame, columns=("task", "importance", "added", "expected"), show="headings", height=20)
        tasks_tree.place(x=5, y=240)

        columns = [("task", "Task", 200), ("importance", "Importance", 80), ("added", "Added", 80), ("expected", "Expected Finish", 120)]
        for col, col_text, col_width in columns:
            tasks_tree.heading(col, text=col_text)
            tasks_tree.column(col, width=col_width)

        for task, task_date, expected_date, importance in reversed(self.task_list):
            tasks_tree.insert("", "0", values=(task, importance, task_date.strftime('%Y-%m-%d'), expected_date.strftime('%Y-%m-%d')))  # Include importance

        return tasks_tree

    def init_finished_tasks(self):
        finished_tasks = ttk.Treeview(self.todo_frame, columns=("task", "completion_date", "duration"), show="headings", height=20)
        finished_tasks.place(x=800, y=240)

        finished_columns = [("task", "Task", 200), ("completion_date", "Completion Date", 120), ("duration", "Duration (days)", 100)]
        for col, col_text, col_width in finished_columns:
            finished_tasks.heading(col, text=col_text)
            finished_tasks.column(col, width=col_width)

        for task, completion_date, completion_duration, expected_date, importance in reversed(self.finished_list):
            finished_tasks.insert("", "end", values=(task, completion_date.strftime('%Y-%m-%d'), completion_duration))

        return finished_tasks

    def add_task(self, task, task_date, expected_date_str, importance):
        task_date = datetime.now().date()
        expected_date = datetime.strptime(expected_date_str, "%m/%d/%y").date()
        self.task_list.insert(0, (task, task_date, expected_date, importance))
        self.tasks_tree.insert("", "0", values=(task, importance, task_date.strftime('%Y-%m-%d'), expected_date.strftime('%Y-%m-%d')))
        self.save_tasks()
        self.close_add_window()

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

        confirm_button = tk.Button(task_frame, text="Add", command=lambda: self.add_task(add_entry.get(), datetime.now().date(), calendar_widget.get_date(), importance_slider.get()))
        confirm_button.pack()

        self.add_window.protocol("WM_DELETE_WINDOW", self.close_add_window)

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
            task, task_date, expected_date, importance = self.task_list.pop(selected_index)  # Unpack importance value
            self.tasks_tree.delete(selected_task_index)
            completion_date = datetime.now().date()
            completion_duration = (completion_date - task_date).days
            finished_task = (task, completion_date, completion_duration, expected_date, importance)  # Include importance
            self.finished_list.append(finished_task)
            self.finished_tasks.insert("", "end", values=(task, completion_date, completion_duration))
            
            # Record the completion date for the finished task
            self.finished_counts[completion_date] = self.finished_counts.get(completion_date, 0) + 1
            
            self.save_tasks()
            self.save_finished_tasks()
            self.update_finished_counts_plot()

    def save_tasks(self):
        with open(self.FILENAME, "w") as file:
            for task, date, expected_date, importance in self.task_list:  # Include importance in the loop
                file.write(f"{task}\t{date.strftime('%Y-%m-%d')}\t{expected_date.strftime('%m/%d/%y')}\t{importance}\n")

    def save_finished_tasks(self):
        self.update_finished_counts_plot()
        with open(self.FINISHED_FILENAME, "w") as file:
            for task, completion_date, completion_duration, expected_date, importance in self.finished_list:
                file.write(f"{task}\t{completion_date}\t{completion_duration}\t{expected_date}\t{importance}\n")

    def load_tasks(self):
        self.task_dict = {}
        try:
            with open(self.FILENAME, "r") as file:
                task_lines = file.readlines()
                tasks = [(line.split('\t')[0], datetime.strptime(line.split('\t')[1].strip(), "%Y-%m-%d").date(), datetime.strptime(line.split('\t')[2].strip(), "%m/%d/%y").date(), int(line.split('\t')[3])) for line in task_lines]  # Parse importance value
                for task, task_date, expected_date, importance in tasks:
                    if expected_date not in self.task_dict:
                        self.task_dict[expected_date] = []
                    self.task_dict[expected_date].append(task)
                return tasks
        except FileNotFoundError:
            return []

    def load_finished_tasks(self):
        self.update_finished_counts_plot()
        try:
            with open(self.FINISHED_FILENAME, "r") as file:
                finished_task_lines = file.readlines()
                return [(line.split('\t')[0], datetime.strptime(line.split('\t')[1], "%Y-%m-%d").date(), int(line.split('\t')[2]), datetime.strptime(line.split('\t')[3].strip(), "%Y-%m-%d").date()) for line in finished_task_lines]
        except FileNotFoundError:
            return []
    
    def update_finished_counts_plot(self):
        # Calculate date range (past week)
        today = datetime.now().date()
        week_ago = today - timedelta(days=6)
        dates = [week_ago + timedelta(days=i) for i in range(7)]

        # Calculate finished task counts for each day
        finished_counts = {date: 0 for date in dates}
        for task, completion_date, completion_duration, expected_date, importance in self.finished_list:
            if week_ago <= completion_date <= today:
                finished_counts[completion_date] += 1


        
        # Clear previous plot data
        self.finished_ax.clear()
        
        # Create the plot
        self.finished_ax.xaxis.set_major_locator(DayLocator(interval=1))  # Show every day
        self.finished_ax.xaxis.set_major_formatter(DateFormatter('%d'))  # Format day as number
        self.finished_ax.plot(dates, finished_counts.values(), marker='o',color="#217346")
        self.finished_ax.set_xlabel('Date')
        self.finished_ax.xaxis.label.set_color('white') 
        self.finished_ax.set_ylabel('Finished Tasks Count')
        self.finished_ax.yaxis.label.set_color('white')
        self.finished_ax.set_title('Finished Tasks Over Time',color='white')

        # Draw the plot
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
        

        self.selected_tasks_text = tk.Label(self.calendar_frame, wrap=True, width=35, height=10)
        self.selected_tasks_text.place(x=400, y=50)

        self.calendar.bind("<<CalendarSelected>>", self.update_task_for_day)
        
        self.update_task_for_day()

    def update_task_for_day(self, event=None):
        selected_date_str = self.calendar.get_date()
        selected_date = datetime.strptime(selected_date_str, "%m/%d/%y").date()
        tasks = self.task_dict.get(selected_date, [])
        
        label_text = "Tasks:\n" + "\n".join(tasks)
        self.selected_tasks_text.config(text=label_text,  wraplength=300)



    
        

    # habit frame
    
    def init_habit_frame(self):
        self.habit_frame = tk.Frame(self.frm, width=1280, height=720)
        self.habit_frame.pack_propagate(False)
        
        self.menu_buttons(self.habit_frame)
        
        self.load_habits()
        
        
        self.enter_habit_button = tk.Button(self.habit_frame, text="Add habit", command=self.add_habit_window)
        self.enter_habit_button.place(x=100,y=200)
        self.add_habit_window = None
        
        
        for i, habit in enumerate(self.habits):
            habit_label = tk.Label(self.habit_frame, text=habit["name"])
            habit_label.grid(row=i, column=0, padx=10, pady=5)

            streak_label = tk.Label(self.habit_frame, text=f"Streak: {habit['streak']}")
            streak_label.grid(row=i, column=1, padx=10, pady=5)

            habit["completed_today"] = tk.BooleanVar(value=False)
            check_button = tk.Checkbutton(self.habit_frame, variable=habit["completed_today"])
            check_button.grid(row=i, column=2, padx=10, pady=5)

            duration_label = tk.Label(self.habit_frame, text=f"Duration: {habit['duration']}")
            duration_label.grid(row=i, column=3, padx=10, pady=5)

            # Bind the Checkbutton to the completion update function
            check_button.bind("<Button-1>", lambda event, h=habit: self.update_completion(h))

    
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
        
        add_habit_entry = tk.Entry(habit_frame)
        add_habit_entry.pack()
        
        
    
    def add_habit(self):
        habit = self.habit_entry.get()
        if habit:
            self.habits_listbox.insert(tk.END, habit)
            self.habit_entry.delete(0, tk.END)

    def load_habits(self):
        try:
            with open("habits.txt", "r") as file:
                lines = file.readlines()

            self.habits = []
            for line in lines:
                habit_data = line.strip().split(",")
                name, streak, completed_today, duration = habit_data
                self.habits.append({
                    "name": name,
                    "streak": int(streak),
                    "completed_today": completed_today.lower() == "true",
                    "duration": duration
                })
        except FileNotFoundError:
            self.habits = []  # Default empty list if the file doesn't exist








if __name__ == "__main__":
    app = ToDoListApp()
