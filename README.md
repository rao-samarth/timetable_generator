---
title: Timetable Generator
emoji: 📅
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
app_port: 7860
---

# IIIT-H Timetable Generator (Spring 2026 Version)

A modern, responsive web tool to help students plan their semester schedule. It automatically parses official college PDF timetables to detect conflicts and visualize weekly schedules.

![Timetable Preview](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![NiceGUI](https://img.shields.io/badge/Built%20with-NiceGUI-orange)

## 🚀 Live Deployment

**[Click here to open the Timetable Generator](https://pranshuul-iiit-timetable.hf.space)**

---

## ✨ Features

- **Smart Parsing:** Automatically extracts course data and slots from `timetable.pdf` and `courses.pdf`.
- **Conflict Detection:** Instantly highlights overlapping courses in red and prevents invalid selections.
- **Visual Grid:** A clear, weekly grid view of your schedule (Mobile Responsive).
- **Export Options:**
  - **PDF:** Download a clean, printable version of your timetable.
  - **ICS:** Export to Google Calendar / Apple Calendar (Smart handling of holidays & schedule swaps).
- **Mobile Friendly:** Collapsible menus and responsive tables for easy use on phones.
- **Manual Overrides:** Support for custom course additions via `courses_manual.json` to handle typos in official docs.

---
