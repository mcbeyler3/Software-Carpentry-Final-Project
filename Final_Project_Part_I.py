# planner.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from calendar_sync import get_busy_blocks_from_ics
from calendar_export import export_schedule_to_ics


# ---------- Data model ----------

@dataclass
class Task:
    name: str
    duration_min: int
    priority: int = 1
    deadline: Optional[datetime] = None


# (start, end, label)
Block = Tuple[datetime, datetime, str]


# ---------- Free time checker ----------

def is_free_time(start, end, busy_blocks):
    """Return True if the block does NOT overlap with calendar events."""
    for b_start, b_end in busy_blocks:
        if start < b_end and end > b_start:
            return False
    return True


# ---------- Cleaned-up scheduler ----------

def build_schedule(
    tasks: List[Task],
    start_time: datetime,
    total_minutes: int,
    work_block_max: int = 50,
    break_minutes: int = 10,
    busy_blocks: List[Tuple[datetime, datetime]] = None,
) -> List[Block]:

    if busy_blocks is None:
        busy_blocks = []

    if total_minutes <= 0 or not tasks:
        return []

    # Sort by priority, then deadline, then name
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

            # Minutes left in the study window
            remaining_window = (window_end - current_time).total_seconds() / 60
            if remaining_window <= 0:
                return schedule

            block_len = int(min(work_block_max, remaining, remaining_window))
            if block_len <= 0:
                return schedule

            work_start = current_time
            work_end = current_time + timedelta(minutes=block_len)

            # If block overlaps with calendar → skip ahead
            if not is_free_time(work_start, work_end, busy_blocks):
                # Find next calendar free time
                conflict = next(
                    (b_end for b_start, b_end in busy_blocks if b_start <= current_time < b_end),
                    None
                )
                if conflict:
                    current_time = conflict
                else:
                    current_time += timedelta(minutes=5)
                continue

            # Add valid block
            schedule.append((work_start, work_end, task.name))
            current_time = work_end
            remaining -= block_len

            # Add break if needed and allowed
            remaining_window = (window_end - current_time).total_seconds() / 60
            if remaining > 0 and remaining_window > break_minutes:
                break_start = current_time
                break_end = current_time + timedelta(minutes=break_minutes)
                schedule.append((break_start, break_end, "Break"))
                current_time = break_end

    return schedule


# ---------- Pretty-print helper ----------

def print_schedule(schedule: List[Block]) -> None:
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


# ---------- Built-in example ----------

def run_example_scenario():
    today = datetime.now().date()
    study_start = datetime.combine(today, datetime.strptime("18:00", "%H:%M").time())

    tasks = [
        Task("Biochem exam review", 90, priority=5),
        Task("Chinese translation homework", 60, priority=3),
        Task("Alternative Energy reading", 45, priority=2),
    ]

    schedule = build_schedule(tasks, study_start, 180)
    print("=== Built-in example ===")
    print_schedule(schedule)
    export_schedule_to_ics(schedule)


# ---------- Interactive mode ----------

def run_interactive_scenario():
    print("\nLet's build a custom study plan!")

    # Ask for .ics file
    ics_path = input("Enter path to .ics calendar (or press Enter to skip): ").strip()
    busy_blocks = []
    if ics_path:
        try:
            busy_blocks = get_busy_blocks_from_ics(ics_path)
            print(f"Loaded {len(busy_blocks)} busy time blocks.")
        except Exception as e:
            print("Calendar load failed:", e)

    # Ask for start time
    today = datetime.now().date()
    start_str = input("Enter start time (HH:MM, default 18:00): ").strip() or "18:00"
    try:
        start_time = datetime.strptime(start_str, "%H:%M").time()
    except:
        print("Invalid time, using default 18:00")
        start_time = datetime.strptime("18:00", "%H:%M").time()
    study_start = datetime.combine(today, start_time)

    # Study window duration
    total_str = input("Total study minutes (default 180): ").strip()
    total_minutes = int(total_str) if total_str.isdigit() else 180

    # Tasks
    tasks = []
    print("\nEnter tasks (empty name to finish):")
    while True:
        name = input("  Task name: ").strip()
        if not name:
            break
        dur = input("    Duration minutes: ").strip()
        pri = input("    Priority 1–5: ").strip()

        try:
            duration = int(dur)
        except:
            print("Invalid duration, skipping.")
            continue

        priority = int(pri) if pri.isdigit() else 3
        tasks.append(Task(name, duration, priority))

    if not tasks:
        print("No tasks entered.")
        return

    # Optional settings
    wb = input("Max work block length (default 50): ").strip()
    br = input("Break length (default 10): ").strip()

    work_block_max = int(wb) if wb.isdigit() else 50
    break_minutes = int(br) if br.isdigit() else 10

    schedule = build_schedule(
        tasks,
        study_start,
        total_minutes,
        work_block_max,
        break_minutes,
        busy_blocks
    )

    print("\n=== Custom Schedule ===")
    print_schedule(schedule)

    export_schedule_to_ics(schedule)


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
