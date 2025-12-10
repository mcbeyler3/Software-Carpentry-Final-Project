# planner.py
"""
Study Companion - Smart Study Planner

This module provides the functionality for creating and visualizing study plans.
It supports:
- Task scheduling based on priorities and optional calendar conflicts
- Exporting the schedule as .ics calendar file
- GUI for entering tasks and generating a schedule
- Built-in and interactive (custom) modes
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
import tkinter as tk
from tkinter import messagebox

from calendar_sync import get_busy_blocks_from_ics
from calendar_export import export_schedule_to_ics

# ---------- Data model ----------

@dataclass
class Task:
    """A study task with a name, estimated duration, optional priority and deadline."""
    name: str
    duration_min: int
    priority: int = 1
    deadline: Optional[datetime] = None

# A scheduled time block: (start_time, end_time, task_name or label)
Block = Tuple[datetime, datetime, str]

# ---------- Free time checker ----------

def is_free_time(start, end, busy_blocks):
    """Return True if the block does NOT overlap with calendar events."""
    for b_start, b_end in busy_blocks:
        if start < b_end and end > b_start:
            return False
    return True

# ---------- Scheduler ----------

def build_schedule(
    tasks: List[Task],
    start_time: datetime,
    total_minutes: int,
    work_block_max: int = 50,
    break_minutes: int = 10,
    busy_blocks: List[Tuple[datetime, datetime]] = None,
) -> List[Block]:
    """
    Generate a study schedule based on tasks, time constraints, and calendar events.
    Automatically includes breaks and avoids busy time blocks.
    """
    if busy_blocks is None:
        busy_blocks = []

    if total_minutes <= 0 or not tasks:
        return []

    def sort_key(task: Task):
        deadline = task.deadline or datetime.max
        return (-task.priority, deadline, task.name)

    tasks_sorted = sorted(tasks, key=sort_key)

    schedule: List[Block] = []
    current_time = start_time
    window_end = start_time + timedelta(minutes=total_minutes)

    for task in tasks_sorted:
        remaining = task.duration_min

        while remaining > 0 and current_time < window_end:
            remaining_window = (window_end - current_time).total_seconds() / 60
            if remaining_window <= 0:
                return schedule

            block_len = int(min(work_block_max, remaining, remaining_window))
            if block_len <= 0:
                return schedule

            work_start = current_time
            work_end = current_time + timedelta(minutes=block_len)

            if not is_free_time(work_start, work_end, busy_blocks):
                conflict = next(
                    (b_end for b_start, b_end in busy_blocks if b_start <= current_time < b_end),
                    None
                )
                if conflict:
                    current_time = conflict
                else:
                    current_time += timedelta(minutes=5)
                continue

            schedule.append((work_start, work_end, task.name))
            current_time = work_end
            remaining -= block_len

            remaining_window = (window_end - current_time).total_seconds() / 60
            if remaining > 0 and remaining_window > break_minutes:
                break_start = current_time
                break_end = current_time + timedelta(minutes=break_minutes)
                schedule.append((break_start, break_end, "Break"))
                current_time = break_end

    return schedule

# ---------- Example scenario ----------

def run_example_scenario():
    """Run a pre-filled example schedule using hardcoded tasks."""
    today = datetime.now().date()
    study_start = datetime.combine(today, datetime.strptime("18:00", "%H:%M").time())

    tasks = [
        Task("Biochem exam review", 90, priority=5),
        Task("Chinese translation homework", 60, priority=3),
        Task("Alternative Energy reading", 45, priority=2),
    ]

    schedule = build_schedule(tasks, study_start, 180)
    print("=== Built-in example ===")
    for start, end, label in schedule:
        print(f"{start:%H:%M} – {end:%H:%M}  {label}")
    export_schedule_to_ics(schedule)

# ---------- Interactive scenario ----------

def run_interactive_scenario(root_window=None, show_main_menu=None):
    """Run the GUI-based interactive planner for custom task entry."""
    run_planner_gui(root_window=root_window, show_main_menu=show_main_menu)

# ---------- GUI Version ----------

def run_planner_gui(root_window=None, show_main_menu=None):
    """
    Launch the GUI for creating a custom study plan.
    Includes task input, calendar support, and schedule export.
    """
    planner_win = tk.Toplevel(root_window)
    planner_win.title("\U0001F4C6 Study Planner")
    planner_win.geometry("600x600")

    tasks = []

    input_frame = tk.Frame(planner_win)
    input_frame.pack(pady=10)

    tk.Label(input_frame, text="Start Time (HH:MM):").grid(row=0, column=0, sticky="e")
    start_entry = tk.Entry(input_frame)
    start_entry.insert(0, "18:00")
    start_entry.grid(row=0, column=1)

    tk.Label(input_frame, text="Total Study Minutes:").grid(row=1, column=0, sticky="e")
    total_entry = tk.Entry(input_frame)
    total_entry.insert(0, "180")
    total_entry.grid(row=1, column=1)

    tk.Label(input_frame, text="Max Work Block Length:").grid(row=2, column=0, sticky="e")
    work_entry = tk.Entry(input_frame)
    work_entry.insert(0, "50")
    work_entry.grid(row=2, column=1)

    tk.Label(input_frame, text="Break Length:").grid(row=3, column=0, sticky="e")
    break_entry = tk.Entry(input_frame)
    break_entry.insert(0, "10")
    break_entry.grid(row=3, column=1)

    tk.Label(input_frame, text="Optional: .ics Calendar File:").grid(row=4, column=0, sticky="e")
    ics_entry = tk.Entry(input_frame)
    ics_entry.grid(row=4, column=1)

    tk.Label(planner_win, text="Enter Tasks:").pack()

    task_frame = tk.Frame(planner_win)
    task_frame.pack(pady=5)

    task_name = tk.Entry(task_frame, width=20)
    task_name.grid(row=0, column=0)
    task_dur = tk.Entry(task_frame, width=10)
    task_dur.grid(row=0, column=1)
    task_pri = tk.Entry(task_frame, width=10)
    task_pri.grid(row=0, column=2)

    task_name.insert(0, "Task Name")
    task_dur.insert(0, "Duration")
    task_pri.insert(0, "Priority")

    def add_task():
        """Add a task from the GUI entry fields to the schedule list."""
        name = task_name.get()
        try:
            dur = int(task_dur.get())
        except:
            messagebox.showerror("Error", "Invalid duration.")
            return
        try:
            pri = int(task_pri.get())
        except:
            pri = 3

        tasks.append(Task(name, dur, pri))
        task_list.insert(tk.END, f"{name} ({dur} min, P{pri})")
        task_name.delete(0, tk.END)
        task_dur.delete(0, tk.END)
        task_pri.delete(0, tk.END)

    tk.Button(task_frame, text="Add Task", command=add_task).grid(row=0, column=3, padx=5)

    task_list = tk.Listbox(planner_win, width=50)
    task_list.pack(pady=5)

    output = tk.Text(planner_win, height=10, width=60)
    output.pack(pady=10)

    def build_plan():
        """Create a study plan using GUI inputs and display it."""
        try:
            total_min = int(total_entry.get())
            work_max = int(work_entry.get())
            break_len = int(break_entry.get())
        except:
            messagebox.showerror("Error", "Invalid numbers.")
            return

        start_str = start_entry.get()
        try:
            start_time = datetime.strptime(start_str, "%H:%M").time()
        except:
            messagebox.showerror("Error", "Invalid time format.")
            return

        study_start = datetime.combine(datetime.now().date(), start_time)

        busy_blocks = []
        ics_path = ics_entry.get().strip()
        if ics_path:
            try:
                busy_blocks = get_busy_blocks_from_ics(ics_path)
            except Exception as e:
                messagebox.showerror("Calendar Error", str(e))
                return

        schedule = build_schedule(
            tasks=tasks,
            start_time=study_start,
            total_minutes=total_min,
            work_block_max=work_max,
            break_minutes=break_len,
            busy_blocks=busy_blocks
        )

        if not schedule:
            messagebox.showinfo("Planner", "No schedule could be generated.")
            return

        output.delete("1.0", tk.END)
        output.insert(tk.END, "Study Schedule:\n")
        output.insert(tk.END, "-" * 50 + "\n")
        for start, end, label in schedule:
            output.insert(tk.END, f"{start:%H:%M} – {end:%H:%M}  {label}\n")

        export_schedule_to_ics(schedule)
        output.insert(tk.END, "\n\U0001F4C6 Exported to study_schedule.ics")

    btn_frame = tk.Frame(planner_win)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Generate Schedule", command=build_plan).pack(side="left", padx=10)

    def return_to_main():
        """Close planner window and return to main menu if available."""
        planner_win.destroy()
        if show_main_menu:
            show_main_menu()
            
       

    tk.Button(btn_frame, text="Return to Main Menu", command=return_to_main).pack(side="right", padx=10)

# ---------- Main entry ----------

if __name__ == "__main__":
    print("Study Companion - Smart Study Planner")
    print("1) Built-in example")
    print("2) Enter my own tasks")
    choice = input("Choose 1 or 2: ").strip()

    if choice == "2":
        run_interactive_scenario()
    else:
        run_example_scenario()
