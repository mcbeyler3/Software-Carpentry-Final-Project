# planner.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Tuple


# ---------- Data model ----------

@dataclass
class Task:
    """
    A study task with an estimate and priority.
    """
    name: str                 # e.g. "Biochem problem set"
    duration_min: int         # estimated time in minutes
    priority: int = 1         # larger = higher priority (5 is highest)
    deadline: Optional[datetime] = None  # optional tie-breaker


# (start, end, label)
Block = Tuple[datetime, datetime, str]


# ---------- Core scheduler ----------

def build_schedule(
    tasks: List[Task],
    start_time: datetime,
    total_minutes: int,
    work_block_max: int = 50,
    break_minutes: int = 10,
) -> List[Block]:
    """
    Make a schedule for one continuous study window.
    """
    if total_minutes <= 0 or not tasks:
        return []

    # Sort tasks by priority, then deadline, then name
    def sort_key(t: Task):
        deadline = t.deadline or datetime.max
        return (-t.priority, deadline, t.name)

    tasks_sorted = sorted(tasks, key=sort_key)

    window_end = start_time + timedelta(minutes=total_minutes)
    current_time = start_time
    schedule: List[Block] = []

    for task in tasks_sorted:
        remaining_for_task = task.duration_min

        while remaining_for_task > 0 and current_time < window_end:
            # Minutes left in the overall window
            rem_window = (window_end - current_time).total_seconds() / 60
            if rem_window <= 0.5:  # basically out of time
                return schedule

            # Length of this work block
            block_len = int(min(work_block_max, remaining_for_task, rem_window))
            if block_len <= 0:
                return schedule

            work_start = current_time
            work_end = current_time + timedelta(minutes=block_len)
            schedule.append((work_start, work_end, task.name))

            remaining_for_task -= block_len
            current_time = work_end

            # Insert a break if there is more of this task
            # and enough room for a break
            rem_window = (window_end - current_time).total_seconds() / 60
            if remaining_for_task > 0 and rem_window > break_minutes:
                break_start = current_time
                break_end = current_time + timedelta(minutes=break_minutes)
                schedule.append((break_start, break_end, "Break"))
                current_time = break_end

        if current_time >= window_end:
            break

    return schedule


# ---------- Pretty-print helper ----------

def print_schedule(schedule: List[Block]) -> None:
    """Print a schedule returned by build_schedule()."""
    if not schedule:
        print("No schedule could be generated.")
        return

    print("\nStudy Plan")
    print("-" * 40)
    for start, end, label in schedule:
        print(f"{start:%H:%M} – {end:%H:%M}  {label}")
    total = (schedule[-1][1] - schedule[0][0]).total_seconds() / 60
    print("-" * 40)
    print(f"Total window length: {int(total)} min\n")


# ---------- Built-in example scenario ----------

def run_example_scenario() -> None:
    """
    Example: study from 18:00–21:00 with three tasks.
    """
    today = datetime.now().date()
    study_start = datetime.combine(today, datetime.strptime("18:00", "%H:%M").time())

    tasks_for_tonight = [
        Task(name="Biochem exam review", duration_min=90, priority=5),
        Task(name="Chinese translation homework", duration_min=60, priority=3),
        Task(name="Alternative Energy reading", duration_min=45, priority=2),
    ]

    tonight_schedule = build_schedule(
        tasks=tasks_for_tonight,
        start_time=study_start,
        total_minutes=180,   # 3 hours
        work_block_max=50,
        break_minutes=10,
    )

    print("=== Built-in example: 18:00–21:00 ===")
    print_schedule(tonight_schedule)


# ---------- Interactive scenario ----------

def run_interactive_scenario() -> None:
    """
    Let the user type in their own study window and tasks.
    """
    print("\nLet's build a custom study plan!")

    # Study window start time
    today = datetime.now().date()
    default_start_str = "18:00"
    start_str = input(f"Enter start time (HH:MM, default {default_start_str}): ").strip()
    if not start_str:
        start_str = default_start_str
    try:
        start_time = datetime.strptime(start_str, "%H:%M").time()
    except ValueError:
        print("Invalid time format, using default 18:00.")
        start_time = datetime.strptime(default_start_str, "%H:%M").time()
    study_start = datetime.combine(today, start_time)

    # Total study minutes
    default_total = 180
    total_str = input(f"Total study minutes (default {default_total}): ").strip()
    if not total_str:
        total_minutes = default_total
    else:
        try:
            total_minutes = int(total_str)
        except ValueError:
            print("Invalid number, using default 180 minutes.")
            total_minutes = default_total

    # Task entry
    tasks: List[Task] = []
    print("\nEnter your tasks (leave name empty to stop):")
    while True:
        name = input("  Task name: ").strip()
        if not name:
            break
        dur_str = input("    Duration in minutes: ").strip()
        pri_str = input("    Priority (1–5, 5 = highest): ").strip()

        try:
            duration = int(dur_str)
        except ValueError:
            print("    Invalid duration, skipping this task.")
            continue

        try:
            priority = int(pri_str)
        except ValueError:
            priority = 3  # default
            print("    Invalid priority, using default 3.")

        tasks.append(Task(name=name, duration_min=duration, priority=priority))

    if not tasks:
        print("No tasks entered. Nothing to schedule.")
        return

    # Optional: adjust work/break pattern
    wb_str = input("\nMax work block length in minutes (default 50): ").strip()
    br_str = input("Break length in minutes (default 10): ").strip()
    try:
        work_block_max = int(wb_str) if wb_str else 50
    except ValueError:
        work_block_max = 50
        print("Invalid work block length, using 50.")
    try:
        break_minutes = int(br_str) if br_str else 10
    except ValueError:
        break_minutes = 10
        print("Invalid break length, using 10.")

    schedule = build_schedule(
        tasks=tasks,
        start_time=study_start,
        total_minutes=total_minutes,
        work_block_max=work_block_max,
        break_minutes=break_minutes,
    )

    print("\n=== Custom schedule ===")
    print_schedule(schedule)


# ---------- Main entry ----------

if __name__ == "__main__":
    print("Study Companion - Smart Study Planner (Part 1)")
    print("1) Run built-in example")
    print("2) Enter my own tasks")
    choice = input("Choose 1 or 2 (default 1): ").strip()

    if choice == "2":
        run_interactive_scenario()
    else:
        run_example_scenario()
