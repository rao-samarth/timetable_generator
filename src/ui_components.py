from nicegui import ui

from .utils import get_slot_time_str


class TimetableGrid:
    def __init__(self):
        self.cells = {}  # Map (Day, Slot) -> ui.element

    def render(self):
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

        # Grid Definition
        grid_style = "grid-template-columns: 70px repeat(3, 1fr) 60px repeat(3, 1fr);"

        with (
            ui.element("div")
            .classes("grid w-full gap-0 border border-gray-300")
            .style(grid_style)
        ):
            # --- HEADER ROW ---
            ui.label("Day").classes(
                "font-bold p-2 border border-gray-200 bg-gray-100 flex items-center justify-center text-xs"
            )

            for i in range(1, 4):
                time_str = get_slot_time_str(i)
                ui.label(time_str).classes(
                    "font-bold p-1 border border-gray-200 bg-gray-100 text-center text-xs flex items-center justify-center"
                )

            with ui.column().classes(
                "border border-gray-200 bg-gray-100 items-center justify-center overflow-hidden"
            ):
                ui.label("LUNCH").classes(
                    "text-[9px] font-bold whitespace-nowrap tracking-widest  text-gray-500"
                )

            for i in range(4, 7):
                time_str = get_slot_time_str(i)
                ui.label(time_str).classes(
                    "font-bold p-1 border border-gray-200 bg-gray-100 text-center text-xs flex items-center justify-center"
                )

            # --- DATA ROWS ---
            for day in days:
                ui.label(day).classes(
                    "font-bold p-2 border border-gray-200 bg-gray-50 flex items-center justify-center"
                )

                for slot in range(1, 4):
                    with ui.column().classes(
                        "p-1 border border-gray-200 min-h-[80px] text-xs relative group"
                    ) as cell:
                        self.cells[(day, slot)] = cell

                ui.element("div").classes("border border-gray-200 bg-gray-100")

                for slot in range(4, 7):
                    with ui.column().classes(
                        "p-1 border border-gray-200 min-h-[80px] text-xs relative group"
                    ) as cell:
                        self.cells[(day, slot)] = cell

    def update(self, selected_courses):
        for cell in self.cells.values():
            cell.clear()

        for course in selected_courses:
            day, slot = course["day"], course["slot"]

            if (day, slot) in self.cells:
                with self.cells[(day, slot)]:
                    color = (
                        "bg-blue-100"
                        if course["half"] == "BOTH"
                        else (
                            "bg-green-100"
                            if course["half"] == "H1"
                            else "bg-purple-100"
                        )
                    )

                    with ui.card().classes(f"w-full p-1 {color} shadow-sm mb-1"):
                        ui.label(course["name"]).classes("font-medium leading-tight")
                        if course["half"] != "BOTH":
                            ui.label(course["half"]).classes(
                                "text-[10px] text-gray-500"
                            )
