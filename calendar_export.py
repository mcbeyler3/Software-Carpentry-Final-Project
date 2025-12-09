# calendar_export.py

from ics import Calendar, Event
from datetime import datetime
from typing import List, Tuple
import os

Block = Tuple[datetime, datetime, str]

def export_schedule_to_ics(schedule: List[Block], filename="study_schedule.ics"):
    """
    Export study schedule to an .ics calendar file.
    """
    if not schedule:
        print("No schedule to export.")
        return

    calendar = Calendar()

    for start, end, label in schedule:
        event = Event()
        event.name = label
        event.begin = start
        event.end = end
        event.description = f"Study Task: {label}"
        calendar.events.add(event)

    # Write file safely
    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(calendar)

    abs_path = os.path.abspath(filename)
    print(f"\n📅 Schedule exported successfully!")
    print(f"Saved to: {abs_path}")
