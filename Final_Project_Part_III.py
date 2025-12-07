# analytics.py
"""
Study Companion - Productivity Analytics Dashboard (Part III)

Reads Pomodoro session logs from sessions.csv or uses demo data and reports:
  - Longest study streak (consecutive days with study)
  - Average work session duration
  - Time of day you usually start studying
  - Total focused time for today, this week, and all time
Also makes a couple of Matplotlib plots.
"""

from __future__ import annotations
import csv
import os
import random
from datetime import datetime, timedelta, date
from collections import defaultdict, Counter
from typing import List, Dict, Any, Tuple

import matplotlib.pyplot as plt

CSV_PATH = "sessions.csv"


# ---------- Loading real sessions ----------

def load_sessions(path: str = CSV_PATH) -> List[Dict[str, Any]]:
    """Load sessions.csv and return a list of session dicts."""
    if not os.path.exists(path):
        print("No sessions.csv found. Run a Pomodoro session first, or use demo mode.")
        return []

    sessions: List[Dict[str, Any]] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                sessions.append({
                    "date": datetime.fromisoformat(row["date"]).date(),
                    "task_name": row["task_name"],
                    "cycles_completed": int(row["cycles_completed"]),
                    "work_minutes": int(row["work_minutes"]),
                    "break_minutes": int(row["break_minutes"]),
                    "started_at": datetime.fromisoformat(row["started_at"]),
                    "finished_at": datetime.fromisoformat(row["finished_at"]),
                })
            except Exception as e:
                print(f"Skipping malformed row: {row} ({e})")
    return sessions


# ---------- Demo data generator ----------

def generate_demo_sessions(
    num_days: int = 10,
    max_sessions_per_day: int = 3,
) -> List[Dict[str, Any]]:
    """
    Make some fake session data so you can demo the analytics
    even if sessions.csv is empty.
    """
    today = date.today()
    sessions: List[Dict[str, Any]] = []

    for day_offset in range(num_days):
        day = today - timedelta(days=(num_days - 1 - day_offset))
        num_sessions = random.randint(0, max_sessions_per_day)

        for _ in range(num_sessions):
            # Random start time between 8:00 and 23:00
            hour = random.randint(8, 23)
            minute = random.choice([0, 15, 30, 45])

            start_dt = datetime.combine(day, datetime.min.time()).replace(
                hour=hour, minute=minute
            )

            work_minutes = random.randint(20, 60)
            break_minutes = random.choice([5, 10, 15])
            cycles = random.randint(1, 4)
            total_break = break_minutes * max(0, cycles - 1)
            finish_dt = start_dt + timedelta(
                minutes=(work_minutes * cycles + total_break)
            )

            task_name = random.choice([
                "Biochem review",
                "Chinese translation",
                "Alt. Energy reading",
                "Thesis writing",
                "Problem set",
            ])

            sessions.append({
                "date": day,
                "task_name": task_name,
                "cycles_completed": cycles,
                "work_minutes": work_minutes * cycles,
                "break_minutes": total_break,
                "started_at": start_dt,
                "finished_at": finish_dt,
            })

    print(f"Generated {len(sessions)} demo sessions "
          f"over the last {num_days} day(s).")
    return sessions


# ---------- a) Study streaks ----------

def calculate_study_streak(sessions: List[Dict[str, Any]]) -> int:
    """Return the longest run (days) of consecutive days with any study."""
    if not sessions:
        return 0

    unique_days = sorted({s["date"] for s in sessions})
    if not unique_days:
        return 0

    best_streak = 1
    current_streak = 1

    for i in range(1, len(unique_days)):
        if unique_days[i] == unique_days[i - 1] + timedelta(days=1):
            current_streak += 1
            if current_streak > best_streak:
                best_streak = current_streak
        else:
            current_streak = 1

    return best_streak


# ---------- b) Average work session duration ----------

def average_work_duration(sessions: List[Dict[str, Any]]) -> float:
    """Average focused work minutes per session."""
    if not sessions:
        return 0.0
    total = sum(s["work_minutes"] for s in sessions)
    return total / len(sessions)


# ---------- c) Time of day you study most frequently ----------

def most_common_study_hour(sessions: List[Dict[str, Any]]) -> int | None:
    """
    Return the hour (0–23) when sessions most often start,
    or None if there is no data.
    """
    if not sessions:
        return None
    hours = [s["started_at"].hour for s in sessions]
    counts = Counter(hours)
    return counts.most_common(1)[0][0]


# ---------- d) Total focused time over selectable ranges ----------

def total_focused_minutes_in_range(
    sessions: List[Dict[str, Any]],
    start_date: date,
    end_date: date,
) -> int:
    """Total focused minutes between start_date and end_date inclusive."""
    total = 0
    for s in sessions:
        if start_date <= s["date"] <= end_date:
            total += s["work_minutes"]
    return total


def get_date_ranges() -> Dict[str, Tuple[date, date]]:
    """
    Return simple date ranges based on today:
      - 'today'
      - 'this_week' (Mon–Sun)
    """
    today = date.today()
    weekday = today.isoweekday()  # Monday=1, Sunday=7
    week_start = today - timedelta(days=weekday - 1)
    week_end = week_start + timedelta(days=6)

    return {
        "today": (today, today),
        "this_week": (week_start, week_end),
    }


# ---------- e) Visualizations via Matplotlib ----------

def plot_daily_focus(
    sessions: List[Dict[str, Any]],
    filename: str = "analytics_daily_focus.png"
) -> None:
    """Bar chart of daily total focused minutes."""
    totals = defaultdict(int)
    for s in sessions:
        totals[s["date"]] += s["work_minutes"]

    if not totals:
        print("No data for daily focus plot.")
        return

    dates = sorted(totals.keys())
    values = [totals[d] for d in dates]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(dates, values)
    ax.set_title("Daily Total Focused Minutes")
    ax.set_xlabel("Date")
    ax.set_ylabel("Minutes of Focused Work")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(filename)
    plt.close(fig)
    print(f"Saved: {filename}")


def plot_time_of_day_histogram(
    sessions: List[Dict[str, Any]],
    filename: str = "analytics_time_of_day.png",
) -> None:
    """Histogram of session start times to show when you usually study."""
    if not sessions:
        print("No data for time-of-day plot.")
        return

    hours = [s["started_at"].hour for s in sessions]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(hours, bins=24, range=(0, 24), edgecolor="black")
    ax.set_title("Time of Day You Study Most Often")
    ax.set_xlabel("Hour of Day (0–23)")
    ax.set_ylabel("Number of Sessions")
    fig.tight_layout()
    fig.savefig(filename)
    plt.close(fig)
    print(f"Saved: {filename}")


# ---------- Main dashboard ----------

def run_analytics_dashboard(sessions: List[Dict[str, Any]], mode_label: str) -> None:
    """
    Print a small text summary and make plots
    for the given list of sessions.
    """
    if not sessions:
        print("No sessions to analyze.")
        return

    print("\n=== Study Companion - Productivity Analytics Dashboard ===")
    print(f"Mode: {mode_label}")

    # a) Study streaks
    streak = calculate_study_streak(sessions)

    # b) Average work session duration
    avg_work = average_work_duration(sessions)

    # c) Time of day you study most frequently
    common_hour = most_common_study_hour(sessions)

    # d) Total focused time over selectable ranges
    ranges = get_date_ranges()
    today_total = total_focused_minutes_in_range(sessions, *ranges["today"])
    week_total = total_focused_minutes_in_range(sessions, *ranges["this_week"])
    all_time_total = sum(s["work_minutes"] for s in sessions)

    # Text summary
    print("\n--- Text Summary ---")
    print(f"Study streak (longest consecutive days): {streak} day(s)")
    print(f"Average focused minutes per session:     {avg_work:.1f} min")

    if common_hour is not None:
        print(f"Most common study start hour:           {common_hour}:00")
    else:
        print("Most common study start hour:           N/A")

    print(f"\nTotal focused minutes (today):          {today_total} min")
    print(f"Total focused minutes (this week):      {week_total} min")
    print(f"Total focused minutes (all time):       {all_time_total} min")

    # e) Generate visualizations
    print("\nGenerating charts...")
    plot_daily_focus(sessions)
    plot_time_of_day_histogram(sessions)

    print("\nAnalytics complete. Open the PNG files to view the charts.")


# ---------- CLI entry point ----------

if __name__ == "__main__":
    print("Study Companion - Productivity Analytics (Part III)")
    print("1) Use REAL data from sessions.csv")
    print("2) Use DEMO data (fake sessions for demonstration)")
    choice = input("Choose 1 or 2 (default 1): ").strip()

    if choice == "2":
        demo_sessions = generate_demo_sessions()
        run_analytics_dashboard(demo_sessions, mode_label="DEMO DATA")
    else:
        real_sessions = load_sessions()
        if real_sessions:
            run_analytics_dashboard(real_sessions, mode_label="REAL DATA")
