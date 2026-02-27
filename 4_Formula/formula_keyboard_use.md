# Logitext — How to Type Text via BLE Keyboard

**Date:** 2026-02-27
**Device:** Pico 2 W running as "Logitext" BLE HID keyboard
**Firmware:** MicroPython v1.27.0

---

## How It Works

```
Mac terminal                   Pico 2 W                  Target Mac
──────────────                 ────────                  ──────────
python3 send.py "erdem"
    │
    │  USB serial
    └─────────────────────────► main.py reads text
                                    │
                                    │  BLE HID keystrokes
                                    └──────────────────────► types "erdem"
                                                             in focused window
```

---

## Files

| File | Location | Purpose |
|------|----------|---------|
| `main.py` | Pico 2 W internal storage | BLE HID keyboard + serial listener |
| `send.py` | Mac — project folder | Sends text to Pico over USB serial |

---

## Usage

### Basic — type a word
```bash
cd /Users/rifaterdemsahin/projects/raspberry-pico-2-hid
python3 send.py "erdem"
```

### Type a sentence
```bash
python3 send.py "hello world"
```

### Type numbers
```bash
python3 send.py "12345"
```

### Type with punctuation
```bash
python3 send.py "hello. my name is erdem"
```

### Supported characters
```
a-z    letters (always lowercase)
0-9    digits
       space
.      period
,      comma
-      hyphen
\n     enter key (newline)
```

---

## Setup Requirements

### Pico must be:
- [ ] Plugged into Mac via USB (data cable, not charge-only)
- [ ] Running `main.py` (MicroPython auto-runs it on boot)
- [ ] Paired with target device via Bluetooth as **Logitext**

### Mac must have:
- [ ] `pyserial` installed: `pip3 install pyserial --break-system-packages`
- [ ] Pico USB port visible: `ls /dev/cu.usbmodem*`

---

## Step-by-Step First Use

### 1. Plug Pico into Mac via USB
```bash
ls /dev/cu.usbmodem*
# Should show: /dev/cu.usbmodem21401
```

### 2. Pair Logitext via Bluetooth on target device
- System Settings → Bluetooth → find **Logitext** → Connect
- Only needed once — it remembers the pairing

### 3. Click where you want text to appear
- Open Notes, TextEdit, browser, terminal — anywhere with a text cursor

### 4. Run send.py
```bash
python3 send.py "erdem"
```

### 5. Text appears in the focused window

---

## Upload / Update main.py on Pico

If you need to re-upload (after re-flash or update):

```bash
# Install mpremote if not already installed
pip3 install mpremote --break-system-packages

# Copy and reset
mpremote connect /dev/cu.usbmodem21401 cp main.py :main.py
mpremote connect /dev/cu.usbmodem21401 reset
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Pico not found` in send.py | Plug USB cable into Mac, check it's a data cable |
| Port busy error | `lsof /dev/cu.usbmodem21401` → `kill -9 <PID>` |
| Logitext not in Bluetooth list | Press RESET on Pico, wait 5s, check again |
| Text not appearing | Click into a text field first, then run send.py |
| Wrong characters | Only lowercase supported — uppercase coming soon |
| Nothing happens after connect | Disconnect + reconnect Bluetooth on target device |

---

## Project File Structure

```
raspberry-pico-2-hid/
├── send.py                    ← Run this on Mac to type text
├── formula_keyboard_use.md    ← This file
├── semblance.md               ← CircuitPython debugging log
├── semblance_uf2.md           ← Why we switched to MicroPython
├── BLUETOOTH_HID_FORMULA.md   ← Full BLE HID setup guide
├── BLUETOOTH_CONNECT_GUIDE.md ← How to pair/connect
├── FLASH_FORMULA.md           ← Firmware flash steps + timeline
└── downloads/
    ├── RPI_PICO2_W-20251209-v1.27.0.uf2         ← MicroPython firmware
    └── adafruit-circuitpython-*.uf2              ← CircuitPython (not used)
```

---

*Pico 2 W | MicroPython 1.27.0 | aioble | BLE HID keyboard | device name: Logitext*
