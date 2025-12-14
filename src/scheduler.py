from typing import Dict, List, Set


class Scheduler:
    def __init__(self, courses_data: List[Dict]):
        # courses_data is now a list of UNIQUE course objects
        # [ {id, name, half, sessions: []}, ... ]
        self.all_courses = {c["id"]: c for c in courses_data}
        self.selected_ids: Set[str] = set()

    def toggle_course(self, course_id: str):
        if course_id in self.selected_ids:
            self.selected_ids.remove(course_id)
        else:
            self.selected_ids.add(course_id)

    def is_selected(self, course_id: str) -> bool:
        return course_id in self.selected_ids

    def get_selected_courses_flat(self) -> List[Dict]:
        """
        Flattens the selected courses into individual session dictionaries
        required by the PDF/ICS generators and the Grid UI.
        Output: [ {'name':..., 'day':..., 'slot':..., 'half':...}, ... ]
        """
        flat_list = []
        for cid in self.selected_ids:
            course = self.all_courses.get(cid)
            if not course:
                continue

            for session in course["sessions"]:
                flat_list.append(
                    {
                        "name": course["name"],
                        "half": course["half"],
                        "day": session["day"],
                        "slot": session["slot"],
                    }
                )
        return flat_list

    def _check_session_conflict(
        self, sess_a: Dict, half_a: str, sess_b: Dict, half_b: str
    ) -> bool:
        """Helper to check if two specific sessions conflict."""
        if sess_a["day"] != sess_b["day"]:
            return False
        if sess_a["slot"] != sess_b["slot"]:
            return False

        # H1 vs H2 is NOT a conflict
        if (half_a == "H1" and half_b == "H2") or (half_a == "H2" and half_b == "H1"):
            return False

        return True

    def get_conflicting_ids(self) -> Set[str]:
        """
        Identifies unselected courses that conflict with the current selection.
        This iterates through all unselected courses -> all their sessions
        and compares against all selected sessions.
        """
        conflicts = set()

        # 1. Gather all occupied time slots from selected courses
        # Structure: List of (session_obj, half_str)
        occupied_slots = []
        for sid in self.selected_ids:
            c = self.all_courses[sid]
            for sess in c["sessions"]:
                occupied_slots.append((sess, c["half"]))

        if not occupied_slots:
            return conflicts

        # 2. Check every unselected course
        for cid, course in self.all_courses.items():
            if cid in self.selected_ids:
                continue

            # Check if ANY session of this course conflicts with ANY occupied slot
            is_conflict = False
            for cand_sess in course["sessions"]:
                for occ_sess, occ_half in occupied_slots:
                    if self._check_session_conflict(
                        cand_sess, course["half"], occ_sess, occ_half
                    ):
                        conflicts.add(cid)
                        is_conflict = True
                        break
                if is_conflict:
                    break

        return conflicts
