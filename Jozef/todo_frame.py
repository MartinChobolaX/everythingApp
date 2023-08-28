import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DayLocator, DateFormatter
from matplotlib.ticker import MaxNLocator

class ToDoFrame(tk.Frame):
    def __init__(self, parent, task_list, finished_list):
        super().__init__(parent, width=1280, height=720)
        self.task_list = task_list
        self.finished_list = finished_list

        # super().menu_buttons(self.frm)

        self.move_button = tk.Button(self, text="-Finished->", command=self.move_to_finished)
        self.move_button.place(x=190, y=200)

        self.add_button = tk.Button(self, text="Add Task", command=self.add_window)
        self.add_button.place(x=100, y=200)
        self.add_window = None

        self.finished_tasks_canvas = tk.Canvas(self, background="#313131")
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
        tasks_tree = ttk.Treeview(super.self.frames['todo'], columns=[col[0] for col in columns], show="headings", height=20)
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
        finished_tasks = ttk.Treeview(super().frames['todo'], columns=[col[0] for col in finished_columns], show="headings", height=20)
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
