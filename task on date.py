import tkinter as tk
from tkinter import ttk
import calendar
from datetime import datetime


class CalendarGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Calendar GUI - Tkinter")
        self.geometry("500x420")
        self.resizable(False, False)

        self.today = datetime.today()
        self.current_year = self.today.year
        self.current_month = self.today.month

        self.selected_date = None

        self.create_header()
        self.create_calendar_frame()
        self.create_status_bar()

        self.draw_calendar()

    def create_header(self):
        header = ttk.Frame(self)
        header.pack(pady=10)

        self.month_label = ttk.Label(
            header,
            font=("Arial", 16, "bold")
        )
        self.month_label.grid(row=0, column=1, padx=20)

        ttk.Button(header, text="◀", command=self.prev_month).grid(row=0, column=0)
        ttk.Button(header, text="▶", command=self.next_month).grid(row=0, column=2)

    def create_calendar_frame(self):
        self.cal_frame = ttk.Frame(self)
        self.cal_frame.pack(padx=10, pady=10)

        self.day_labels = []
        for i, day in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            lbl = ttk.Label(self.cal_frame, text=day, width=6, anchor="center")
            lbl.grid(row=0, column=i)
            self.day_labels.append(lbl)

        self.date_buttons = []

    def create_status_bar(self):
        self.status = tk.StringVar(value="Ready")

        status_bar = ttk.Label(
            self,
            textvariable=self.status,
            relief="sunken",
            anchor="w"
        )
        status_bar.pack(fill="x", side="bottom")

    def draw_calendar(self):
        for btn in self.date_buttons:
            btn.destroy()

        self.date_buttons.clear()

        self.month_label.config(
            text=f"{calendar.month_name[self.current_month]} {self.current_year}"
        )

        month_days = calendar.monthcalendar(self.current_year, self.current_month)

        row = 1
        for week in month_days:
            col = 0
            for day in week:
                if day == 0:
                    lbl = ttk.Label(self.cal_frame, text="", width=6)
                    lbl.grid(row=row, column=col)
                    self.date_buttons.append(lbl)
                else:
                    btn = tk.Button(
                        self.cal_frame,
                        text=str(day),
                        width=4,
                        command=lambda d=day: self.select_date(d)
                    )

                    if (
                        day == self.today.day and
                        self.current_month == self.today.month and
                        self.current_year == self.today.year
                    ):
                        btn.config(bg="lightblue")

                    btn.grid(row=row, column=col, padx=1, pady=1)
                    self.date_buttons.append(btn)

                col += 1
            row += 1

    def select_date(self, day):
        self.selected_date = f"{self.current_year}-{self.current_month:02d}-{day:02d}"
        self.status.set(f"Selected date: {self.selected_date}")

    def prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1

        self.draw_calendar()
        self.status.set("Moved to previous month")

    def next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1

        self.draw_calendar()
        self.status.set("Moved to next month")


if __name__ == "__main__":
    app = CalendarGUI()
    app.mainloop()
