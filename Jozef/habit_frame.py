import tkinter as tk

class HabitFrame(tk.Frame):
    def __init__(self, parent, habits):
        super().__init__(parent, width=1280, height=720)
        self.habits = habits

        # super().menu_buttons(self.frm)

        self.load_data()  # You might want to load data here if needed

        self.enter_habit_button = tk.Button(self, text="Add habit", command=self.add_habit_window)
        self.enter_habit_button.place(x=100, y=200)
        self.add_habit_window = None

        for i, habit in enumerate(self.habits):
            habit_label = tk.Label(self, text=habit["name"])
            habit_label.grid(row=i, column=0, padx=10, pady=5)

            streak_label = tk.Label(self, text=f"Streak: {habit['streak']}")
            streak_label.grid(row=i, column=1, padx=10, pady=5)

            habit["completed_today"] = tk.BooleanVar(value=False)
            check_button = tk.Checkbutton(self, variable=habit["completed_today"], command=lambda h=habit: self.update_completion(h))
            check_button.grid(row=i, column=2, padx=10, pady=5)

            duration_label = tk.Label(self, text=f"Duration: {habit['duration']}")
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
            streak_label = tk.Label(self.frames['habit'], text=f"Streak: {habit['streak']}")
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