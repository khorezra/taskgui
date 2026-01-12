import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import calendar
from datetime import datetime
import json
import os


# ==========================
# Constants
# ==========================

DATA_FILE = "events.json"
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 550
DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


# ==========================
# Calendar Application Class
# ==========================

class CalendarApp(tk.Tk):

    def __init__(self):
        super().__init__()

        # Window setup
        self.title("Advanced Calendar GUI")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)

        # Date tracking
        self.today = datetime.today()
        self.current_year = self.today.year
        self.current_month = self.today.month
        self.selected_day = None

        # Event storage
        self.events = {}
        self.load_events()

        # UI Variables
        self.status_text = tk.StringVar(value="Ready")

        # Build UI
        self.create_menu()
        self.create_header()
        self.create_main_layout()
        self.create_status_bar()

        # Initial draw
        self.draw_calendar()


    # ==========================
    # Menu
    # ==========================

    def create_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Save", command=self.save_events)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)

        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menubar)


    # ==========================
    # Header (Month Navigation)
    # ==========================

    def create_header(self):
        header = ttk.Frame(self)
        header.pack(pady=10)

        ttk.Button(header, text="◀ Previous", command=self.prev_month).grid(row=0, column=0, padx=10)

        self.month_label = ttk.Label(
            header,
            text="",
            font=("Arial", 18, "bold")
        )
        self.month_label.grid(row=0, column=1, padx=20)

        ttk.Button(header, text="Next ▶", command=self.next_month).grid(row=0, column=2, padx=10)


    # ==========================
    # Main Layout
    # ==========================

    def create_main_layout(self):
        main = ttk.Frame(self)
        main.pack(fill="both", expand=True, padx=10)

        # Calendar frame
        self.calendar_frame = ttk.Frame(main)
        self.calendar_frame.pack(side="left", padx=10)

        self.create_calendar_grid()

        # Event panel
        self.event_frame = ttk.Frame(main)
        self.event_frame.pack(side="right", fill="y", padx=10)

        self.create_event_panel()


    # ==========================
    # Calendar Grid
    # ==========================

    def create_calendar_grid(self):
        # Day headers
        for col, day in enumerate(DAY_NAMES):
            lbl = ttk.Label(self.calendar_frame, text=day, width=8, anchor="center")
            lbl.grid(row=0, column=col, pady=5)

        self.day_buttons = []


    def draw_calendar(self):
        # Clear old buttons
        for widget in self.day_buttons:
            widget.destroy()
        self.day_buttons.clear()

        # Update month label
        self.month_label.config(
            text=f"{calendar.month_name[self.current_month]} {self.current_year}"
        )

        # Get month layout
        month_days = calendar.monthcalendar(self.current_year, self.current_month)

        row = 1
        for week in month_days:
            col = 0
            for day in week:
                if day == 0:
                    lbl = ttk.Label(self.calendar_frame, text="", width=8)
                    lbl.grid(row=row, column=col)
                    self.day_buttons.append(lbl)
                else:
                    btn = tk.Button(
                        self.calendar_frame,
                        text=str(day),
                        width=6,
                        command=lambda d=day: self.select_day(d)
                    )

                    # Highlight today
                    if (
                        day == self.today.day and
                        self.current_month == self.today.month and
                        self.current_year == self.today.year
                    ):
                        btn.config(bg="lightblue")

                    # Highlight event days
                    date_key = self.format_date(day)
                    if date_key in self.events:
                        btn.config(bg=self.events[date_key]["color"])

                    btn.grid(row=row, column=col, padx=2, pady=2)
                    self.day_buttons.append(btn)

                col += 1
            row += 1


    # ==========================
    # Event Panel
    # ==========================

    def create_event_panel(self):
        ttk.Label(
            self.event_frame,
            text="Event Details",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", pady=5)

        self.date_label = ttk.Label(self.event_frame, text="No date selected")
        self.date_label.pack(anchor="w", pady=5)

        ttk.Label(self.event_frame, text="Description:").pack(anchor="w")

        self.event_text = tk.Text(self.event_frame, width=30, height=8)
        self.event_text.pack(pady=5)

        ttk.Label(self.event_frame, text="Event Color:").pack(anchor="w")

        self.color_button = ttk.Button(
            self.event_frame,
            text="Choose Color",
            command=self.choose_color
        )
        self.color_button.pack(pady=5)

        self.selected_color = "#90caf9"

        ttk.Button(
            self.event_frame,
            text="Save Event",
            command=self.save_event
        ).pack(pady=5)

        ttk.Button(
            self.event_frame,
            text="Delete Event",
            command=self.delete_event
        ).pack(pady=5)


    # ==========================
    # Event Logic
    # ==========================

    def select_day(self, day):
        self.selected_day = day
        date_key = self.format_date(day)

        self.date_label.config(text=f"Selected: {date_key}")
        self.event_text.delete("1.0", tk.END)

        if date_key in self.events:
            self.event_text.insert(tk.END, self.events[date_key]["text"])
            self.selected_color = self.events[date_key]["color"]

        self.status_text.set(f"Selected date {date_key}")


    def save_event(self):
        if not self.selected_day:
            messagebox.showwarning("Warning", "Select a date first")
            return

        text = self.event_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Event description is empty")
            return

        date_key = self.format_date(self.selected_day)

        self.events[date_key] = {
            "text": text,
            "color": self.selected_color
        }

        self.save_events()
        self.draw_calendar()
        self.status_text.set("Event saved")


    def delete_event(self):
        if not self.selected_day:
            return

        date_key = self.format_date(self.selected_day)

        if date_key in self.events:
            del self.events[date_key]
            self.event_text.delete("1.0", tk.END)
            self.save_events()
            self.draw_calendar()
            self.status_text.set("Event deleted")


    def choose_color(self):
        color = colorchooser.askcolor(title="Choose Event Color")
        if color[1]:
            self.selected_color = color[1]


    # ==========================
    # Month Navigation
    # ==========================

    def prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1

        self.draw_calendar()
        self.status_text.set("Moved to previous month")


    def next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1

        self.draw_calendar()
        self.status_text.set("Moved to next month")


    # ==========================
    # Utilities
    # ==========================

    def format_date(self, day):
        return f"{self.current_year}-{self.current_month:02d}-{day:02d}"


    def load_events(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as file:
                self.events = json.load(file)


    def save_events(self):
        with open(DATA_FILE, "w") as file:
            json.dump(self.events, file, indent=4)


    def show_about(self):
        messagebox.showinfo(
            "About",
            "Advanced Calendar GUI\n\nBuilt with Python & Tkinter\n300+ lines project"
        )


    # ==========================
    # Status Bar
    # ==========================

    def create_status_bar(self):
        status = ttk.Label(
            self,
            textvariable=self.status_text,
            relief="sunken",
            anchor="w"
        )
        status.pack(fill="x", side="bottom")


# ==========================
# Run Application
# ==========================

if __name__ == "__main__":
    app = CalendarApp()
    app.mainloop()
