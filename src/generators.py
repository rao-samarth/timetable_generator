import re
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from fpdf import FPDF
from ics import Calendar, Event

from .utils import *


class TimetablePDF(FPDF):
    def header(self):
        # Headers are handled manually in the generate function
        pass

    def footer(self):
        self.set_y(-10)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, "Generated via College Timetable Builder", 0, 0, "R")


def generate_pdf_bytes(selected_courses: list) -> bytes:
    # A4 Landscape: 297mm x 210mm
    pdf = TimetablePDF(orientation="L", unit="mm", format="A4")
    pdf.set_margins(10, 10, 10)
    pdf.set_auto_page_break(False)  # Force single page
    pdf.add_page()

    # --- Configuration ---
    # Colors (R, G, B)
    C_BG_HEADER = (245, 247, 250)  # Light Gray
    C_BG_LUNCH = (229, 231, 235)  # Darker Gray for Lunch
    C_TEXT_MAIN = (30, 30, 30)
    C_GRID_LINE = (200, 200, 200)

    # Card Colors
    C_CARD_FULL = (219, 234, 254)  # Blue-100
    C_CARD_H1 = (220, 252, 231)  # Green-100
    C_CARD_H2 = (243, 232, 255)  # Purple-100

    # Dimensions
    PAGE_W = 297
    PAGE_H = 210
    MARGIN = 10

    EFFECTIVE_W = PAGE_W - (2 * MARGIN)
    EFFECTIVE_H = PAGE_H - (2 * MARGIN)

    # Vertical Layout
    HEADER_H = 14
    TITLE_H = 16
    TABLE_H = EFFECTIVE_H - TITLE_H
    ROW_H = (TABLE_H - HEADER_H) / 6

    # Horizontal Layout
    # Ratios: Day=0.8, Slot=1.3, Lunch=0.3
    UNIT_W = EFFECTIVE_W / 8.9

    W_DAY = UNIT_W * 0.8
    W_SLOT = UNIT_W * 1.3
    W_LUNCH = UNIT_W * 0.3

    # Calculate X Positions
    X_OFFSETS = [MARGIN]
    current_x = MARGIN + W_DAY
    X_OFFSETS.append(current_x)  # Start of Slot 1

    for _ in range(3):
        current_x += W_SLOT
        X_OFFSETS.append(current_x)

    current_x += W_LUNCH
    X_OFFSETS.append(current_x)  # Start of Slot 4

    for _ in range(2):
        current_x += W_SLOT
        X_OFFSETS.append(current_x)

    # --- DRAW TITLE ---
    pdf.set_xy(MARGIN, MARGIN)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*C_TEXT_MAIN)
    pdf.cell(EFFECTIVE_W, 8, "Spring 2026 Class Timetable", 0, 1, "C")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(
        EFFECTIVE_W, 5, f"Generated on {date.today().strftime('%B %d, %Y')}", 0, 1, "C"
    )

    # --- DRAW HEADER ROW ---
    y_base = MARGIN + TITLE_H

    # 1. Day Header
    pdf.set_xy(MARGIN, y_base)
    pdf.set_fill_color(*C_BG_HEADER)
    pdf.set_draw_color(*C_GRID_LINE)
    pdf.set_text_color(*C_TEXT_MAIN)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(W_DAY, HEADER_H, "Day", 1, 0, "C", True)

    # 2. Slots 1-3
    for i in range(1, 4):
        s_time = TIME_SLOTS[i]
        label = f"{s_time[0].strftime('%H:%M')} - {s_time[1].strftime('%H:%M')}"
        x = X_OFFSETS[i]
        pdf.set_xy(x, y_base)
        pdf.cell(W_SLOT, HEADER_H, "", 1, 0, "C", True)
        pdf.set_xy(x, y_base + 3)
        pdf.multi_cell(W_SLOT, 4, label, 0, "C")

    # 3. Lunch Header
    x_lunch = X_OFFSETS[4]
    pdf.set_xy(x_lunch, y_base)
    pdf.set_fill_color(*C_BG_LUNCH)
    pdf.cell(W_LUNCH, TABLE_H, "", 1, 0, "C", True)

    center_x = x_lunch + (W_LUNCH / 2)
    center_y = y_base + (TABLE_H / 2)
    with pdf.rotation(90, center_x, center_y):
        pdf.set_xy(center_x - 30, center_y)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(60, 0, "LUNCH BREAK (13:05 - 14:00)", 0, 0, "C")
    pdf.set_text_color(*C_TEXT_MAIN)

    # 4. Slots 4-6
    for i in range(4, 7):
        idx = i + 1
        s_time = TIME_SLOTS[i]
        label = f"{s_time[0].strftime('%H:%M')} - {s_time[1].strftime('%H:%M')}"
        x = X_OFFSETS[idx]
        pdf.set_xy(x, y_base)
        pdf.set_fill_color(*C_BG_HEADER)
        pdf.cell(W_SLOT, HEADER_H, "", 1, 0, "C", True)
        pdf.set_xy(x, y_base + 3)
        pdf.multi_cell(W_SLOT, 4, label, 0, "C")

    # --- DRAW GRID ROWS & COURSES ---
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    for d_idx, day in enumerate(days):
        y_curr = y_base + HEADER_H + (d_idx * ROW_H)

        # Row Lines
        pdf.set_draw_color(*C_GRID_LINE)
        pdf.line(MARGIN, y_curr, MARGIN + EFFECTIVE_W, y_curr)
        pdf.line(MARGIN, y_curr + ROW_H, MARGIN + EFFECTIVE_W, y_curr + ROW_H)

        # Day Label
        pdf.set_xy(MARGIN, y_curr)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(*C_TEXT_MAIN)
        pdf.cell(W_DAY, ROW_H, day, 1, 0, "C")

        # Vertical Separators
        for x in X_OFFSETS[1:]:
            pdf.line(x, y_curr, x, y_curr + ROW_H)

        # Draw Courses as Cards
        for slot_num in range(1, 7):
            x_idx = slot_num if slot_num < 4 else slot_num + 1
            x_pos = X_OFFSETS[x_idx]

            courses = [
                c for c in selected_courses if c["day"] == day and c["slot"] == slot_num
            ]
            courses = sorted(courses, key=lambda x: x["half"])

            if not courses:
                continue

            # --- CARD STYLING ---
            margin_gap = 2.0  # External margin
            count = len(courses)

            available_h = ROW_H - (margin_gap * 2)
            card_gap = 1.0 if count > 1 else 0
            card_height = (available_h - (card_gap * (count - 1))) / count

            card_width = W_SLOT - (margin_gap * 2)

            # Auto Scale Font
            if count == 1:
                font_size = 9
                line_height = 4
            elif count == 2:
                font_size = 8
                line_height = 3.5
            else:
                font_size = 6
                line_height = 2.5

            for c_idx, course in enumerate(courses):
                c_y = y_curr + margin_gap + (c_idx * (card_height + card_gap))

                # Check for Tag
                has_tag = course["half"] != "BOTH"

                # Adjust line height slightly if we need space for a tag
                current_line_height = line_height
                if has_tag:
                    current_line_height -= 0.5

                # Colors
                if course["half"] == "H1":
                    bg_col = C_CARD_H1
                elif course["half"] == "H2":
                    bg_col = C_CARD_H2
                else:
                    bg_col = C_CARD_FULL

                pdf.set_fill_color(*bg_col)
                pdf.set_draw_color(160, 160, 160)

                # DRAW ROUNDED RECT
                pdf.rect(
                    x_pos + margin_gap,
                    c_y,
                    card_width,
                    card_height,
                    "DF",
                    round_corners=True,
                    corner_radius=2,
                )

                # TEXT PLACEMENT
                int_padding_x = 1.5
                int_padding_y = 1.5

                pdf.set_font("Helvetica", "B", font_size)
                pdf.set_text_color(0, 0, 0)

                # Clean Name
                display_name = course["name"]
                display_name = re.sub(
                    r"\s*\(\s*H[12]?\s*\)", "", display_name, flags=re.IGNORECASE
                ).strip()

                # Positioning for Name
                pdf.set_xy(x_pos + margin_gap + int_padding_x, c_y + int_padding_y)

                text_width = card_width - (int_padding_x * 2)
                pdf.multi_cell(text_width, current_line_height, display_name, 0, "C")

                # FORCE PRINT TAG (Bottom Center)
                if has_tag:
                    pdf.set_font("Helvetica", "I", font_size - 1)
                    pdf.set_text_color(80, 80, 80)

                    # Calculate absolute bottom position for the tag
                    tag_h = 3.0
                    tag_y = (
                        c_y + card_height - tag_h - 1.0
                    )  # 1.0 padding from bottom edge

                    pdf.set_xy(x_pos + margin_gap, tag_y)
                    pdf.cell(card_width, tag_h, course["half"], 0, 0, "C")

    # Outer Border
    pdf.set_draw_color(*C_GRID_LINE)
    pdf.rect(MARGIN, y_base, EFFECTIVE_W, TABLE_H, "D")

    return bytes(pdf.output())


# --- ICS GENERATION ---
def generate_ics_string(selected_courses: list) -> str:
    cal = Calendar()
    schedule_map = {}
    for c in selected_courses:
        key = (c["day"], c["slot"])
        if key not in schedule_map:
            schedule_map[key] = []
        schedule_map[key].append(c)

    current_date = SEM_START
    while current_date <= SEM_END:
        if is_blackout(current_date) or current_date in HOLIDAYS:
            current_date += timedelta(days=1)
            continue
        if current_date.weekday() == 6:
            current_date += timedelta(days=1)
            continue

        logic_day_str = DAYS_MAP[current_date.weekday()]
        if current_date == date(2026, 3, 20):
            logic_day_str = "Sat"

        cancelled_slots = []
        if current_date == date(2026, 2, 16):
            cancelled_slots = [1, 2, 3]

        extra_mappings = []
        if current_date == date(2026, 2, 21):
            extra_mappings = [(1, 4, "Mon"), (2, 5, "Mon"), (3, 6, "Mon")]

        for slot_num in range(1, 7):
            if slot_num in cancelled_slots:
                continue
            courses = schedule_map.get((logic_day_str, slot_num), [])
            for course in courses:
                _add_event_if_valid(cal, course, current_date, slot_num)

        for src_slot, target_slot, src_day in extra_mappings:
            courses = schedule_map.get((src_day, src_slot), [])
            for course in courses:
                _add_event_if_valid(cal, course, current_date, target_slot)

        current_date += timedelta(days=1)

    return cal.serialize()


def _add_event_if_valid(cal, course, date_obj, slot_num):
    c_half = course["half"]
    current_half = get_semester_half(date_obj)
    if current_half == "NONE":
        return
    if c_half == "H1" and current_half != "H1":
        return
    if c_half == "H2" and current_half != "H2":
        return

    start_time, end_time = TIME_SLOTS[slot_num]

    # Use Asia/Kolkata (GMT+05:30) explicitly
    ist_tz = ZoneInfo("Asia/Kolkata")

    # Combine Date + Time and attach Timezone
    dt_start = datetime.combine(date_obj, start_time).replace(tzinfo=ist_tz)
    dt_end = datetime.combine(date_obj, end_time).replace(tzinfo=ist_tz)

    e = Event()
    e.name = course["name"]
    e.begin = dt_start
    e.end = dt_end
    cal.events.add(e)
