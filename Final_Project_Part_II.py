# pomodoro.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import time
import csv
import os

import matplotlib.pyplot as plt


# ---------- Data model ----------

@dataclass
class PomodoroConfig:
    """
    Settings for a Pomodoro session.

    task_name    what you are working on
    work_minutes length of each work interval
    break_minutes length of each break interval
    cycles       number of work/break cycles
    demo_mode    if True, runs in accelerated (fake-time) mode
    """
    task_name: str
    work_minutes: int = 25
    break_minutes: int = 5
    cycles: int = 4
    demo_mode: bool = False


@dataclass
class PomodoroResult:
    """Summary of a completed (or partially completed) Pomodoro run."""
    task_name: str
    cycles_completed: int
    total_work_seconds: int
    total_break_seconds: int
    started_at: datetime
    finished_at: datetime


# ---------- Core timer logic ----------

def _sleep_unit(seconds: int, demo_mode: bool) -> None:
    """Sleep helper. In demo_mode, sleep is capped so it runs fast."""
    if demo_mode:
        time.sleep(min(seconds, 1))
    else:
        time.sleep(seconds)


def _run_interval(label: str, minutes: int, demo_mode: bool) -> int:
    """
    Run a single interval (work or break) with coarse countdown prints.

    Returns the *logical* duration in seconds (minutes * 60),
    not the real wall-clock time.
    """
    if minutes <= 0:
        return 0

    total_seconds = minutes * 60
    remaining = total_seconds

    print(f"\n--- {label} for {minutes} minute(s) ---")

    # Print a few updates instead of every second
    step = max(total_seconds // 5, 1)
    last_print = total_seconds

    while remaining > 0:
        _sleep_unit(step, demo_mode)
        remaining -= step
        if remaining < 0:
            remaining = 0

        minutes_left = remaining // 60
        if remaining != last_print:
            print(f"{label} time remaining: ~{minutes_left} min")
            last_print = remaining

    print(f"*** {label} interval finished! ***")
    return total_seconds


def run_pomodoro(config: PomodoroConfig) -> PomodoroResult:
    """
    Run a Pomodoro session based on the given configuration.
    """
    print("\nStarting Pomodoro Session")
    print("-------------------------")
    print(f"Task:        {config.task_name}")
    print(f"Work:        {config.work_minutes} min")
    print(f"Break:       {config.break_minutes} min")
    print(f"Cycles:      {config.cycles}")
    print(f"Demo mode:   {'ON' if config.demo_mode else 'OFF'}")

    if config.demo_mode:
        print("\n⚠️  NOTE: Demo mode is enabled.")
        print("   The Pomodoro timer is running in accelerated mode.")
        print("   Logical time (minutes) is correct, but real time is sped up.")

    started_at = datetime.now()
    total_work = 0
    total_break = 0
    cycles_completed = 0

    try:
        for i in range(1, config.cycles + 1):
            print(f"\n=== Cycle {i}/{config.cycles} ===")

            total_work += _run_interval("Work", config.work_minutes, config.demo_mode)

            if i < config.cycles and config.break_minutes > 0:
                total_break += _run_interval("Break", config.break_minutes, config.demo_mode)

            cycles_completed += 1

    except KeyboardInterrupt:
        print("\nPomodoro interrupted by user.")

    finished_at = datetime.now()

    result = PomodoroResult(
        task_name=config.task_name,
        cycles_completed=cycles_completed,
        total_work_seconds=total_work,
        total_break_seconds=total_break,
        started_at=started_at,
        finished_at=finished_at,
    )

    print_session_summary(result)
    append_to_log(result, "sessions.csv")
    plot_session_pie(result, "session_summary.png")

    return result


# ---------- Summary & logging ----------

def print_session_summary(result: PomodoroResult) -> None:
    """Print a short summary of the Pomodoro session."""
    work_min = result.total_work_seconds // 60
    break_min = result.total_break_seconds // 60
    total_min = work_min + break_min

    print("\nPomodoro Summary")
    print("----------------")
    print(f"Task:                {result.task_name}")
    print(f"Cycles completed:    {result.cycles_completed}")
    print(f"Focused work time:   {work_min} min")
    print(f"Break time:          {break_min} min")
    print(f"Total session time:  {total_min} min")
    print(f"Started at:          {result.started_at:%Y-%m-%d %H:%M}")
    print(f"Finished at:         {result.finished_at:%Y-%m-%d %H:%M}")


def append_to_log(result: PomodoroResult, path: str) -> None:
    """
    Append this session to a CSV log file.

    Columns:
    date, task_name, cycles_completed, work_minutes,
    break_minutes, started_at, finished_at
    """
    file_exists = os.path.exists(path)
    work_min = result.total_work_seconds // 60
    break_min = result.total_break_seconds // 60

    with open(path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "date",
                "task_name",
                "cycles_completed",
                "work_minutes",
                "break_minutes",
                "started_at",
                "finished_at",
            ])
        writer.writerow([
            result.started_at.date().isoformat(),
            result.task_name,
            result.cycles_completed,
            work_min,
            break_min,
            result.started_at.isoformat(timespec="seconds"),
            result.finished_at.isoformat(timespec="seconds"),
        ])

    print(f"\nSession logged to: {path}")


# ---------- Visualization ----------

def plot_session_pie(result: PomodoroResult, filename: str = "session_summary.png") -> None:
    """
    Create a simple pie chart of work vs break time for this session
    and save it as an image file.
    """
    work_min = result.total_work_seconds / 60.0
    break_min = result.total_break_seconds / 60.0

    if work_min <= 0 and break_min <= 0:
        print("No work or break time recorded; skipping pie chart.")
        return

    labels = []
    sizes = []

    if work_min > 0:
        labels.append("Work")
        sizes.append(work_min)
    if break_min > 0:
        labels.append("Break")
        sizes.append(break_min)

    fig, ax = plt.subplots()
    ax.set_title(f"Pomodoro Session: {result.task_name}")
    ax.pie(sizes, labels=labels, autopct="%1.1f%%")
    ax.axis("equal")

    fig.tight_layout()
    fig.savefig(filename)
    plt.close(fig)

    print(f"Session summary pie chart saved to: {filename}")


# ---------- Example + interactive CLI ----------

def run_example() -> None:
    """
    Run a short demo Pomodoro so it's easy to see how this works.
    Uses demo_mode so it doesn't take long.
    """
    config = PomodoroConfig(
        task_name="Example: Biochem exam review",
        work_minutes=2,     # 2 logical minutes
        break_minutes=1,    # 1 logical minute
        cycles=2,
        demo_mode=True,     # runs very fast
    )
    run_pomodoro(config)


def run_interactive() -> None:
    """
    Let the user configure a Pomodoro session in the terminal.
    """
    print("\nLet's configure your Pomodoro session.")

    task = input("Task name (e.g., 'Problem set 3'): ").strip()
    if not task:
        task = "Unnamed task"

    def get_int(prompt: str, default: int) -> int:
        text = input(f"{prompt} (default {default}): ").strip()
        if not text:
            return default
        try:
            return int(text)
        except ValueError:
            print(f"Invalid number, using default {default}.")
            return default

    work_minutes = get_int("Work minutes", 25)
    break_minutes = get_int("Break minutes", 5)
    cycles = get_int("Number of cycles", 4)

    demo_text = input("Demo mode (accelerated)? (y/N): ").strip().lower()
    demo_mode = demo_text == "y"

    config = PomodoroConfig(
        task_name=task,
        work_minutes=work_minutes,
        break_minutes=break_minutes,
        cycles=cycles,
        demo_mode=demo_mode,
    )

    run_pomodoro(config)


if __name__ == "__main__":
    print("Study Companion - Pomodoro Timer (Part II + visualization)")
    print("1) Run quick example")
    print("2) Configure my own session")
    choice = input("Choose 1 or 2 (default 1): ").strip()

    if choice == "2":
        run_interactive()
    else:
        run_example()
