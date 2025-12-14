from datetime import date, time

# --- Time Slots ---
# Maps Slot Index (1-6) to (Start Time, End Time)
TIME_SLOTS = {
    1: (time(8, 30), time(9, 55)),
    2: (time(10, 5), time(11, 30)),
    3: (time(11, 40), time(13, 5)),
    # Lunch Break 13:05 - 14:00
    4: (time(14, 0), time(15, 25)),
    5: (time(15, 35), time(17, 0)),
    6: (time(17, 10), time(18, 40)),
}


def get_slot_time_str(slot_idx: int) -> str:
    """Returns formatted string like '08:30-09:55'"""
    if slot_idx not in TIME_SLOTS:
        return "Unknown"
    start, end = TIME_SLOTS[slot_idx]
    return f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}"


DAYS_MAP = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}

# --- Semester Dates (Spring 2026) ---
SEM_START = date(2026, 1, 2)
SEM_END = date(2026, 4, 25)

# Half Semester Ranges
H1_START = date(2026, 1, 2)
H1_END = date(2026, 2, 25)
H2_START = date(2026, 3, 3)
H2_END = date(2026, 4, 25)

# --- Exceptions ---
HOLIDAYS = {
    date(2026, 1, 13),
    date(2026, 1, 14),
    date(2026, 1, 26),
    date(2026, 3, 14),
    date(2026, 3, 19),
    date(2026, 3, 21),
    date(2026, 4, 3),
}

BLACKOUT_RANGES = [
    (date(2026, 2, 13), date(2026, 2, 15)),  # Feb Blackout
    (date(2026, 2, 26), date(2026, 3, 2)),  # Mid-sems
    (date(2026, 3, 14), date(2026, 3, 15)),  # March Blackout
    (date(2026, 4, 26), date(2026, 12, 31)),  # Post Sem
]


def is_blackout(d: date) -> bool:
    for start, end in BLACKOUT_RANGES:
        if start <= d <= end:
            return True
    return False


def get_semester_half(d: date) -> str:
    """Returns 'H1', 'H2', or 'BOTH' depending on the date."""
    if H1_START <= d <= H1_END:
        return "H1"
    elif H2_START <= d <= H2_END:
        return "H2"
    return "NONE"
