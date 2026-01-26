#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import calendar
import json
import os
from datetime import datetime

# --- CONFIGURATION ---
DATA_FILE = "linux_planner_data.json"
WINDOW_SIZE = "1000x650"
THEME_COLOR = "#2C3E50"  # Dark Slate (Linux-like)
ACCENT_COLOR = "#18BC9C" # Teal

class LinuxCalendarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Linux Pro Planner")
        self.root.geometry(WINDOW_SIZE)
        
        # Configure Styles (TTK)
        self.style = ttk.Style()
        self.style.theme_use('clam') # 'clam' looks best on most Linux distros
        
        # Custom Treeview colors
        self.style.configure("Treeview", 
                             background="white", 
                             foreground="black", 
                             rowheight=25, 
                             fieldbackground="white")
        self.style.map('Treeview', background=[('selected', ACCENT_COLOR)])

        # Data Management
        self.tasks = self.load_data()
        
        # Date State
        now = datetime.now()
        self.current_year = now.year
        self.current_month = now.month
        self.selected_date = f"{self.current_year}-{self.current_month}-{now.day}"

        # --- LAYOUT MANAGER ---
        # Main Container
        main_container = tk.Frame(root, bg="#ECF0F1")
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left Panel (Calendar)
        left_panel = tk.Frame(main_container, bg="white", width=300, relief=tk.RIDGE, borderwidth=1)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Right Panel (Tasks)
        right_panel = tk.Frame(main_container, bg="white", relief=tk.RIDGE, borderwidth=1)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- LEFT PANEL: CALENDAR ---
        # Header
        self.month_lbl = tk.Label(left_panel, text="January 2026", font=("Ubuntu", 16, "bold"), bg="white", fg=THEME_COLOR)
        self.month_lbl.pack(pady=15)

        # Nav Buttons
        btn_frame = tk.Frame(left_panel, bg="white")
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="<<", command=self.prev_month, relief=tk.FLAT, bg="#BDC3C7").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text=">>", command=self.next_month, relief=tk.FLAT, bg="#BDC3C7").pack(side=tk.LEFT, padx=5)

        # Calendar Grid
        self.cal_frame = tk.Frame(left_panel, bg="white")
        self.cal_frame.pack(pady=10, padx=10)
        
        # Stats Widget
        stats_frame = tk.LabelFrame(left_panel, text="Daily Stats", bg="white", fg="#7F8C8D")
        stats_frame.pack(fill=tk.X, padx=10, pady=20)
        self.lbl_total = tk.Label(stats_frame, text="Total: 0", bg="white", anchor="w")
        self.lbl_total.pack(fill=tk.X, padx=5, pady=2)
        self.lbl_done = tk.Label(stats_frame, text="Completed: 0", bg="white", anchor="w", fg=ACCENT_COLOR)
        self.lbl_done.pack(fill=tk.X, padx=5, pady=2)

        # --- RIGHT PANEL: TASKS ---
        # Header
        top_header = tk.Frame(right_panel, bg=THEME_COLOR, height=50)
        top_header.pack(fill=tk.X)
        self.date_header_lbl = tk.Label(top_header, text=f"Tasks for {self.selected_date}", font=("Ubuntu", 14, "bold"), bg=THEME_COLOR, fg="white")
        self.date_header_lbl.pack(side=tk.LEFT, padx=15, pady=10)

        # Toolbar
        toolbar = tk.Frame(right_panel, bg="#ECF0F1")
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(toolbar, text="Mark Done", command=self.mark_done, bg=ACCENT_COLOR, fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Delete Task", command=self.delete_task, bg="#E74C3C", fg="white").pack(side=tk.LEFT, padx=2)

        # Task Treeview (The main table)
        columns = ("time", "task", "category", "priority", "status")
        self.tree = ttk.Treeview(right_panel, columns=columns, show="headings", selectmode="browse")
        
        # Column Headers
        self.tree.heading("time", text="Time")
        self.tree.heading("task", text="Task Description")
        self.tree.heading("category", text="Category")
        self.tree.heading("priority", text="Priority")
        self.tree.heading("status", text="Status")
        
        # Column Widths
        self.tree.column("time", width=80, anchor="center")
        self.tree.column("task", width=300)
        self.tree.column("category", width=100, anchor="center")
        self.tree.column("priority", width=80, anchor="center")
        self.tree.column("status", width=80, anchor="center")
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- INPUT AREA (Bottom) ---
        input_frame = tk.LabelFrame(right_panel, text="Add New Task", bg="white", padx=10, pady=10)
        input_frame.pack(fill=tk.X, padx=5, pady=10)

        # Row 1
        tk.Label(input_frame, text="Task:", bg="white").grid(row=0, column=0, sticky="w")
        self.entry_task = tk.Entry(input_frame, width=40)
        self.entry_task.grid(row=0, column=1, columnspan=4, sticky="we", padx=5)

        # Row 2
        tk.Label(input_frame, text="Time:", bg="white").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_time = tk.Entry(input_frame, width=10)
        self.entry_time.insert(0, "09:00")
        self.entry_time.grid(row=1, column=1, sticky="w", padx=5)

        tk.Label(input_frame, text="Category:", bg="white").grid(row=1, column=2, sticky="e")
        self.combo_cat = ttk.Combobox(input_frame, values=["Work", "Study", "Personal", "Linux"], width=10, state="readonly")
        self.combo_cat.current(0)
        self.combo_cat.grid(row=1, column=3, sticky="w", padx=5)

        tk.Label(input_frame, text="Priority:", bg="white").grid(row=1, column=4, sticky="e")
        self.combo_prio = ttk.Combobox(input_frame, values=["High", "Normal", "Low"], width=8, state="readonly")
        self.combo_prio.current(1)
        self.combo_prio.grid(row=1, column=5, sticky="w", padx=5)

        tk.Button(input_frame, text="Add Task", command=self.add_task, bg=THEME_COLOR, fg="white").grid(row=1, column=6, padx=15)

        # Initialize
        self.draw_calendar()
        self.refresh_tree()

    # --- CORE LOGIC ---
    
    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.tasks, f, indent=4)

    def draw_calendar(self):
        # Clear
        for widget in self.cal_frame.winfo_children():
            widget.destroy()

        # Update Header
        self.month_lbl.config(text=f"{calendar.month_name[self.current_month]} {self.current_year}")

        # Weekday Headers
        days = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        for idx, day in enumerate(days):
            tk.Label(self.cal_frame, text=day, font=("Arial", 9, "bold"), bg="white", fg="#7F8C8D").grid(row=0, column=idx, padx=3, pady=5)

        # Days
        cal = calendar.monthcalendar(self.current_year, self.current_month)
        for r, week in enumerate(cal):
            for c, day in enumerate(week):
                if day != 0:
                    d_key = f"{self.current_year}-{self.current_month}-{day}"
                    
                    # Style Logic
                    bg_color = "#ECF0F1" # Default Gray
                    fg_color = "black"
                    
                    # Highlight if selected
                    if d_key == self.selected_date:
                        bg_color = THEME_COLOR
                        fg_color = "white"
                    # Highlight if has tasks (and not selected)
                    elif d_key in self.tasks and self.tasks[d_key]:
                        # Check priority
                        is_urgent = any(t['priority'] == "High" and t['status'] != "Done" for t in self.tasks[d_key])
                        if is_urgent:
                            bg_color = "#E74C3C" # Red
                            fg_color = "white"
                        else:
                            bg_color = "#3498DB" # Blue
                            fg_color = "white"

                    btn = tk.Button(self.cal_frame, text=str(day), width=4, pady=5, 
                                    bg=bg_color, fg=fg_color, relief=tk.FLAT,
                                    command=lambda d=day: self.select_date(d))
                    btn.grid(row=r+1, column=c, padx=2, pady=2)

    def select_date(self, day):
        self.selected_date = f"{self.current_year}-{self.current_month}-{day}"
        self.date_header_lbl.config(text=f"Tasks for {self.selected_date}")
        self.draw_calendar() # Redraw to update selection highlight
        self.refresh_tree()

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

    def refresh_tree(self):
        # Clear Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get tasks
        day_tasks = self.tasks.get(self.selected_date, [])
        
        # Sort: Pending first, then by Time
        # We give "Done" tasks a high sort index so they drop to bottom
        day_tasks.sort(key=lambda x: (x.get('status') == "Done", x.get('time', '00:00')))

        total = len(day_tasks)
        completed = 0

        for t in day_tasks:
            # Check schema compatibility (legacy data fix)
            if 'status' not in t: t['status'] = "Pending"
            if 'category' not in t: t['category'] = "General"

            if t['status'] == "Done":
                completed += 1

            self.tree.insert("", tk.END, values=(
                t.get('time'), 
                t.get('task'), 
                t.get('category'), 
                t.get('priority'),
                t.get('status')
            ))
        
        # Update Stats
        self.lbl_total.config(text=f"Total Tasks: {total}")
        self.lbl_done.config(text=f"Completed: {completed}")

    def add_task(self):
        task_txt = self.entry_task.get()
        if not task_txt:
            messagebox.showwarning("Input Error", "Please enter a task description.")
            return

        if self.selected_date not in self.tasks:
            self.tasks[self.selected_date] = []

        new_task = {
            "task": task_txt,
            "time": self.entry_time.get(),
            "category": self.combo_cat.get(),
            "priority": self.combo_prio.get(),
            "status": "Pending"
        }

        self.tasks[self.selected_date].append(new_task)
        self.save_data()
        
        # Reset UI
        self.entry_task.delete(0, tk.END)
        self.refresh_tree()
        self.draw_calendar()

    def delete_task(self):
        selected = self.tree.selection()
        if not selected: return
        
        # Map treeview index to list index (requires strict sync)
        # Note: This is simplified. In a 1000+ line app we uses unique IDs.
        # Here we rely on the sort order being rebuilt exactly same way.
        # Safer approach: Find item by content match.
        
        item_values = self.tree.item(selected[0], 'values')
        task_desc = item_values[1]
        
        # Find and remove
        day_tasks = self.tasks[self.selected_date]
        for i, t in enumerate(day_tasks):
            if t['task'] == task_desc:
                del day_tasks[i]
                break
        
        if not day_tasks:
            del self.tasks[self.selected_date]

        self.save_data()
        self.refresh_tree()
        self.draw_calendar()

    def mark_done(self):
        selected = self.tree.selection()
        if not selected: return
        
        item_values = self.tree.item(selected[0], 'values')
        task_desc = item_values[1]
        
        day_tasks = self.tasks[self.selected_date]
        for t in day_tasks:
            if t['task'] == task_desc:
                t['status'] = "Done" if t['status'] == "Pending" else "Pending"
                break
        
        self.save_data()
        self.refresh_tree() # Re-sorts automatically

if __name__ == "__main__":
    root = tk.Tk()
    app = LinuxCalendarApp(root)
    root.mainloop()
