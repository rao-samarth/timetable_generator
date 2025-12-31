from typing import Dict, List, Set, Tuple


class Scheduler:
    def __init__(self, courses_data: List[Dict]):
        # courses_data is now a list of UNIQUE course objects
        # [ {id, name, half, sessions: []}, ... ]
        self.all_courses = {c["id"]: c for c in courses_data} 
        # Structure: {course_id: {person_name: {half: ..., sessions: ...}}}
        self.selected_courses: Dict[str, Dict[str, Dict]] = {}

    def toggle_course(self, course_id: str, person_name: str = ""):
        if not person_name:
            person_name = "default"
        
        if course_id not in self.selected_courses:
            self.selected_courses[course_id] = {}
        
        if person_name in self.selected_courses[course_id]:
            del self.selected_courses[course_id][person_name]
            # Clean up empty course entries
            if not self.selected_courses[course_id]:
                del self.selected_courses[course_id]
        else:
            course = self.all_courses.get(course_id)
            if course:
                self.selected_courses[course_id][person_name] = {
                    "half": course["half"],
                    "sessions": course["sessions"]
                }

    def is_selected(self, course_id: str, person_name: str = "") -> bool:
        if not person_name:
            person_name = "default"
        return course_id in self.selected_courses and person_name in self.selected_courses[course_id]

    def get_selected_ids(self) -> Set[str]:
        """Get all selected course IDs"""
        return set(self.selected_courses.keys())

    def get_selected_courses_flat(self) -> List[Dict]:
        """
        Flattens the selected courses into individual session dictionaries
        required by the PDF/ICS generators and the Grid UI.
        Groups people who share the same course and half.
        Output: [ {'name':..., 'day':..., 'slot':..., 'half':...}, ... ]
        """
        flat_list = []
        
        # Build a map of (course_id, day, slot, half) -> [person names]
        course_sessions_map: Dict[Tuple[str, str, int, str], List[str]] = {}
        
        for course_id, people_dict in self.selected_courses.items():
            course = self.all_courses.get(course_id)
            if not course:
                continue
            
            for person_name, person_data in people_dict.items():
                half = person_data["half"]
                sessions = person_data["sessions"]
                
                for session in sessions:
                    key = (course_id, session["day"], session["slot"], half)
                    if key not in course_sessions_map:
                        course_sessions_map[key] = []
                    course_sessions_map[key].append(person_name)
        
        # Convert to flat list with merged names
        for (course_id, day, slot, half), people_names in course_sessions_map.items():
            course = self.all_courses.get(course_id)
            # Sort names for consistent ordering
            sorted_names = sorted(
                [n for n in people_names if n != "default"],
                key=lambda x: (x != "default", x)  # "default" goes to the end if mixed
            )
            # Display format: "CourseName (Alice/Bob)" or just "CourseName" if default
            if sorted_names:
                display_name = f"{course['name']} ({'/'.join(sorted_names)})"
            else:
                display_name = course["name"]
            
            flat_list.append(
                {
                    "name": display_name,
                    "half": half,
                    "day": day,
                    "slot": slot,
                    "course_id": course_id,  # Track original course for reference
                    "classroom": course.get("classroom", "TBD"),  # Include classroom
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

    def get_conflicting_ids(self, person_name: str = "") -> Set[str]:
        """
        Identifies unselected courses that conflict with the current selection for a specific person.
        This iterates through all unselected courses -> all their sessions
        and compares against all selected sessions for that person.
        """
        if not person_name:
            person_name = "default"
        
        conflicts = set()

        # 1. Gather all occupied time slots from selected courses for this person
        # Structure: List of (session_obj, half_str)
        occupied_slots = []
        for course_id, people_dict in self.selected_courses.items():
            if person_name not in people_dict:
                continue
            
            person_data = people_dict[person_name]
            half = person_data["half"]
            sessions = person_data["sessions"]
            
            for sess in sessions:
                occupied_slots.append((sess, half))

        if not occupied_slots:
            return conflicts

        # 2. Check every unselected course
        for cid, course in self.all_courses.items():
            if cid in self.selected_courses and person_name in self.selected_courses[cid]:
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
