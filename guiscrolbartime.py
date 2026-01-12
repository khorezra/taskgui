import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import calendar
from datetime import datetime
import json
import os

# Try Windows sound, else fallback
try:
    import winsound
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False


DATA_FILE = "events.json"
DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


class CalendarApp(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("Calendar with Sound Alarm & Time")
        self.geometry("980x580")
        self.resizable(False, False)

        self.today = datetime.now()
        self.current_year = self.today.year
        self.current_month = self.today.month
        self.selected_day = None

        self.events = {}
        self.load_events()

        self.status_text = tk.StringVar(value="Ready")
        self.time_text = tk.StringVar()

        self.create_header()
        self.create_main_layout()
        self.create_status_bar()

        self.draw_calendar()
        self.update_current_time()   # ⏰ live clock
        self.check_reminders()       # 🔔 alarm loop

    # ================= HEADER =================

    def create_header(self):
        header = ttk.Frame(self)
        header.pack(pady=5, fill="x")

        ttk.Button(header, text="◀", command=self.prev_month).pack(side="left", padx=10)

        self.month_label = ttk.Label(header, font=("Arial", 18, "bold"))
        self.month_label.pack(side="left", padx=20)

        ttk.Button(header, text="▶", command=self.next_month).pack(side="left")

        # ---- LIVE TIME DISPLAY ----
        ttk.Label(
            header,
            textvariable=self.time_text,
            font=("Arial", 14),
            foreground="blue"
        ).pack(side="right", padx=15)

    # ================= MAIN LAYOUT =================

    def create_main_layout(self):
        main = ttk.Frame(self)
        main.pack(fill="both", expand=True, padx=10)

        self.calendar_frame = ttk.Frame(main)
        self.calendar_frame.pack(side="left", padx=10)

        self.create_calendar_grid()

        self.event_frame = ttk.Frame(main)
        self.event_frame.pack(side="right", fill="y", padx=20)

        self.create_event_panel()

    # ================= CALENDAR =================

    def create_calendar_grid(self):
        for col, day in enumerate(DAY_NAMES):
            ttk.Label(self.calendar_frame, text=day, width=8).grid(row=0, column=col)

        self.day_buttons = []

    def draw_calendar(self):
        for widget in self.day_buttons:
            widget.destroy()
        self.day_buttons.clear()

        self.month_label.config(
            text=f"{calendar.month_name[self.current_month]} {self.current_year}"
        )

        month_days = calendar.monthcalendar(self.current_year, self.current_month)

        row = 1
        for week in month_days:
            col = 0
            for day in week:
                if day == 0:
                    ttk.Label(self.calendar_frame, text="", width=8).grid(row=row, column=col)
                else:
                    btn = tk.Button(
                        self.calendar_frame,
                        text=str(day),
                        width=6,
                        command=lambda d=day: self.select_day(d)
                    )

                    if (
                        day == self.today.day and
                        self.current_month == self.today.month and
                        self.current_year == self.today.year
                    ):
                        btn.config(bg="lightblue")

                    btn.grid(row=row, column=col, padx=2, pady=2)
                    self.day_buttons.append(btn)

                col += 1
            row += 1

    # ================= EVENT PANEL =================

    def create_event_panel(self):
        ttk.Label(self.event_frame, text="Event Details", font=("Arial", 14, "bold")).pack(anchor="w")

        self.date_label = ttk.Label(self.event_frame, text="No date selected")
        self.date_label.pack(anchor="w", pady=5)

        # ---- TIME INPUT (12-HOUR FORMAT) ----
        time_frame = ttk.Frame(self.event_frame)
        time_frame.pack(anchor="w", pady=5)

        ttk.Label(time_frame, text="Hour").grid(row=0, column=0)
        self.hour_spin = tk.Spinbox(time_frame, from_=1, to=12, width=5)
        self.hour_spin.grid(row=0, column=1, padx=5)

        ttk.Label(time_frame, text="Minute").grid(row=0, column=2)
        self.minute_spin = tk.Spinbox(time_frame, from_=0, to=59, width=5, format="%02.0f")
        self.minute_spin.grid(row=0, column=3, padx=5)

        ttk.Label(time_frame, text="AM/PM").grid(row=0, column=4)
        self.ampm_box = ttk.Combobox(time_frame, values=["AM", "PM"], width=5, state="readonly")
        self.ampm_box.set("AM")
        self.ampm_box.grid(row=0, column=5, padx=5)

        ttk.Label(self.event_frame, text="Description").pack(anchor="w")
        self.event_text = tk.Text(self.event_frame, width=35, height=6)
        self.event_text.pack(pady=5)

        ttk.Button(self.event_frame, text="Choose Color", command=self.choose_color).pack(pady=5)
        self.selected_color = "#90caf9"

        ttk.Button(self.event_frame, text="Save Event", command=self.save_event).pack(pady=5)
        ttk.Button(self.event_frame, text="Delete Event", command=self.delete_event).pack(pady=5)

    # ================= EVENT LOGIC =================

    def select_day(self, day):
        self.selected_day = day
        date = f"{self.current_year}-{self.current_month:02d}-{day:02d}"
        self.date_label.config(text=f"Selected: {date}")
        self.event_text.delete("1.0", tk.END)

    def save_event(self):
        if not self.selected_day:
            messagebox.showwarning("Warning", "Select a date first")
            return

        hour = self.hour_spin.get()
        minute = self.minute_spin.get()
        ampm = self.ampm_box.get()
        text = self.event_text.get("1.0", tk.END).strip()

        if not text:
            messagebox.showwarning("Warning", "Event text is empty")
            return

        key = f"{self.current_year}-{self.current_month:02d}-{self.selected_day:02d} {hour}:{minute} {ampm}"

        self.events[key] = {
            "text": text,
            "color": self.selected_color,
            "alerted": False
        }

        self.save_events()
        self.status_text.set("Event saved with alarm")

    def delete_event(self):
        hour = self.hour_spin.get()
        minute = self.minute_spin.get()
        ampm = self.ampm_box.get()

        key = f"{self.current_year}-{self.current_month:02d}-{self.selected_day:02d} {hour}:{minute} {ampm}"

        if key in self.events:
            del self.events[key]
            self.save_events()
            self.event_text.delete("1.0", tk.END)

    # ================= REMINDER + SOUND =================

    def check_reminders(self):
        now = datetime.now().strftime("%Y-%m-%d %I:%M %p")

        for key, event in self.events.items():
            if key == now and not event["alerted"]:
                self.play_alarm_sound()
                messagebox.showinfo("Reminder", event["text"])
                event["alerted"] = True
                self.save_events()

        self.after(1000, self.check_reminders)

    def play_alarm_sound(self):
        if SOUND_AVAILABLE:
            for _ in range(3):
                winsound.Beep(1000, 300)
        else:
            self.bell()

    # ================= UTILITIES =================

    def update_current_time(self):
        self.time_text.set(datetime.now().strftime("%I:%M:%S %p"))
        self.after(1000, self.update_current_time)

    def choose_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.selected_color = color

    def prev_month(self):
        self.current_month -= 1
        if self.current_month == 0:
            self.current_month = 12
            self.current_year -= 1
        self.draw_calendar()

    def next_month(self):
        self.current_month += 1
        if self.current_month == 13:
            self.current_month = 1
            self.current_year += 1
        self.draw_calendar()

    def load_events(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                self.events = json.load(f)

    def save_events(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.events, f, indent=4)

    def create_status_bar(self):
        ttk.Label(self, textvariable=self.status_text, relief="sunken", anchor="w")\
            .pack(fill="x", side="bottom")


if __name__ == "__main__":
    app = CalendarApp()
    app.mainloop()
