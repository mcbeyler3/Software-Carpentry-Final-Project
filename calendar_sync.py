

from ics import Calendar
from datetime import datetime
from typing import List, Tuple

def get_busy_blocks_from_ics(file_path: str) -> List[Tuple[datetime, datetime]]:
    """
    Reads an .ics calendar file and returns a list of busy time blocks (start, end).
    """
    busy_blocks = []
    with open(file_path, "r", encoding="utf-8") as f:
        calendar = Calendar(f.read())

    for event in calendar.events:
        start = event.begin.datetime
        end = event.end.datetime
        if end > datetime.now():
            busy_blocks.append((start, end))

    return busy_blocks

