# Agent Rules — Logitext / Pico 2 W HID Project

## Project Identity
- **Name**: Logitext
- **Goal**: Raspberry Pi Pico 2 W as USB HID keyboard bridge over WiFi
- **Stack**: CircuitPython 10.1.3, Python 3, HTML/CSS/JS (GitHub Pages)

## AI Agent Guidelines

### What this project does
Sends keystrokes from a Mac to a Windows PC wirelessly using a Pico 2 W:
`Mac → HTTP POST (WiFi) → Pico 2 W → USB HID → Windows PC`

### Key constraints
- CircuitPython 10.1.3 only (not MicroPython — no USB HID module)
- WiFi is 2.4GHz only (CYW43439 chip limitation)
- BLE HID is broken in CircuitPython 10.x on Pico 2 W

### 7-Stage Framework
1. `1_Real_Unknown/` — Why: problems, OKRs, questions
2. `2_Environment/` — Context: hardware, firmware, network constraints
3. `3_Simulation/` — Vision: mockups, diagrams, photos
4. `4_Formula/` — Recipe: step-by-step guides
5. `5_Symbols/` — Reality: source code
6. `6_Semblance/` — Scars: errors, workarounds
7. `7_Testing_Known/` — Proof: checklists, OKR validation

### Code style
- CircuitPython code: keep minimal, no f-strings in hot loops
- Python scripts: stdlib only, no external deps except pyperclip for clipboard
- HTML/CSS/JS: vanilla only, no frameworks; shared via shared.css + shared.js
- Menus: read from menus.json — never hardcode nav links in HTML

### Security
- Never commit `.env` or `settings.toml` with real credentials
- WiFi password stays in `.env` on local machine only

### Git workflow
- Commit after every meaningful change
- Use emoji prefix in commit messages matching the stage
- Push immediately after commit
