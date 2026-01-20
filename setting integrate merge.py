import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import calendar
from datetime import datetime
import json
import os

# ================= FILES =================

USERS_FILE = "users.json"
EVENTS_FILE = "events.json"

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# ================= USER AUTH =================

def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({"admin@gmail.com": "admin"}, f)
    with open(USERS_FILE, "r") as f:
        return json.load(f)

# ================= LOGIN WINDOW =================

class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Login")
        self.geometry("350x220")
        self.resizable(False, False)

        self.users = load_users()

        ttk.Label(self, text="User Login", font=("Arial", 16, "bold")).pack(pady=10)

        ttk.Label(self, text="Email").pack(anchor="w", padx=20)
        self.email_entry = ttk.Entry(self, width=30)
        self.email_entry.pack(padx=20, pady=5)

        ttk.Label(self, text="Password").pack(anchor="w", padx=20)
        self.password_entry = ttk.Entry(self, width=30, show="*")
        self.password_entry.pack(padx=20, pady=5)

        ttk.Button(self, text="Login", command=self.login).pack(pady=15)

    def login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if email in self.users and self.users[email] == password:
            messagebox.showinfo("Success", "Login Successful")
            self.destroy()
            CalendarApp(email)
        else:
            messagebox.showerror("Error", "Invalid Email or Password")

# ================= CALENDAR APP =================

class CalendarApp(tk.Tk):
    def __init__(self, user_email):
        super().__init__()

        self.user_email = user_email
        self.title(f"Calendar - {user_email}")
        self.geometry("980x580")
        self.resizable(False, False)

        self.today = datetime.now()
        self.current_year = self.today.year
        self.current_month = self.today.month
        self.selected_day = None

        self.events = {}
        self.load_events()

        self.time_text = tk.StringVar()
        self.status_text = tk.StringVar(value="Logged in")

        self.create_header()
        self.create_main_layout()
        self.create_status_bar()

        self.draw_calendar()
        self.update_time()
        self.check_reminders()

        self.mainloop()

    # ================= HEADER =================

    def create_header(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=5)

        ttk.Label(header, text=f"Welcome: {self.user_email}", font=("Arial", 12)).pack(side="left", padx=10)

        self.month_label = ttk.Label(header, font=("Arial", 18, "bold"))
        self.month_label.pack(side="left", padx=20)

        ttk.Label(header, textvariable=self.time_text, font=("Arial", 14), foreground="blue")\
            .pack(side="right", padx=15)

    # ================= MAIN =================

    def create_main_layout(self):
        main = ttk.Frame(self)
        main.pack(fill="both", expand=True, padx=10)

        self.calendar_frame = ttk.Frame(main)
        self.calendar_frame.pack(side="left", padx=10)

        for i, day in enumerate(DAY_NAMES):
            ttk.Label(self.calendar_frame, text=day, width=8).grid(row=0, column=i)

        self.buttons = []

    # ================= CALENDAR =================

    def draw_calendar(self):
        for btn in self.buttons:
            btn.destroy()
        self.buttons.clear()

        self.month_label.config(text=f"{calendar.month_name[self.current_month]} {self.current_year}")

        month_days = calendar.monthcalendar(self.current_year, self.current_month)

        row = 1
        for week in month_days:
            col = 0
            for day in week:
                if day == 0:
                    ttk.Label(self.calendar_frame, text="", width=8).grid(row=row, column=col)
                else:
                    b = tk.Button(
                        self.calendar_frame,
                        text=str(day),
                        width=6,
                        command=lambda d=day: self.select_day(d)
                    )
                    b.grid(row=row, column=col, padx=2, pady=2)
                    self.buttons.append(b)
                col += 1
            row += 1

    def select_day(self, day):
        self.selected_day = day
        self.status_text.set(f"Selected date: {day}")

    # ================= TIME =================

    def update_time(self):
        self.time_text.set(datetime.now().strftime("%I:%M:%S %p"))
        self.after(1000, self.update_time)

    # ================= REMINDER =================

    def check_reminders(self):
        self.after(1000, self.check_reminders)

    # ================= FILE =================

    def load_events(self):
        if os.path.exists(EVENTS_FILE):
            with open(EVENTS_FILE, "r") as f:
                self.events = json.load(f)

    def create_status_bar(self):
        ttk.Label(self, textvariable=self.status_text, relief="sunken", anchor="w")\
            .pack(fill="x", side="bottom")

# ================= START =================

if __name__ == "__main__":
    LoginWindow().mainloop()
