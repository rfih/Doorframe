# Door Frame Material Calculator (桌框材料計算器)

A desktop app that calculates **frame material requirements** for door projects with **multilingual UI** and built-in data for multiple lock/closer types.

> Built with **Python + Tkinter** for factory use. Focused on speed, accuracy, and easy training for operators.

---

## ✨ Features

- **Material Calculations**
  - Vertical/horizontal members, tolerances, edge sealing, slats/gaps
  - Works with **simple** & **UB** door types
- **Components Database**
  - ~8 **匣式鎖** (box locks) types, 20+ **電子鎖** types
  - **隱藏弓器孔** (concealed door closer) handling via JSON
- **Multilingual UI**
  - English / Bahasa Indonesia / 中文 (Traditional)
- **Images & Aids**
  - Inline diagrams for door leaf/扇 orientation and hole references
- **Export & Reporting**
  - Summary panel for BOM-like output you can copy to sheets

---

## 🧱 Tech Stack

- **Python 3.10+**
- **Tkinter**
- Optional: `Pillow` (if you display images), `pandas` (if you export CSV)

---

## 🧮 Calculation Logic (high level)

- Inputs:

  - Door type (simple/UB), count, dimensions (H×W×T)
  - Piece widths (vertical/horizontal), tolerances, edge sealing options
  - Component toggles (box lock types, electronic locks, closer holes)

-Outputs:
  - Total lengths per material class, hole positions, per-door summary
  - BOM lines (copy-paste ready)

-Bug fix notes applied:
  - Initialize gap_width = 0 and slats_width = 0 in calculate_material() (not in *_requirements)
  - Concealed closer image path determined from JSON when concealed_door_closer present

---

👋 Author

Rizky Febri Ibra Habibie

Email: rizkyfebriibrahabibie@gmail.com

LinkedIn: [/in/rizkyfebriibrahabibie/](https://www.linkedin.com/in/rizkyfebriibrahabibie/)
