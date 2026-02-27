# Flash CircuitPython to Pico 2 W — Step-by-Step Formula

**Date:** 2026-02-27
**CircuitPython version:** 10.1.3
**Library bundle:** 20260226 (10.x mpy)

---

## Downloads (Completed)

| File | Size | Location |
|------|------|----------|
| `adafruit-circuitpython-raspberry_pi_pico2_w-en_US-10.1.3.uf2` | 2.8 MB | `downloads/` |
| `adafruit-circuitpython-bundle-10.x-mpy-20260226.zip` | 16 MB | `downloads/` |

**Download log (2026-02-27):**
```
# Firmware
curl -L https://downloads.circuitpython.org/bin/raspberry_pi_pico2_w/en_US/adafruit-circuitpython-raspberry_pi_pico2_w-en_US-10.1.3.uf2
→ 100% 2.8MB — DONE

# Library bundle
curl -L https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/download/20260226/adafruit-circuitpython-bundle-10.x-mpy-20260226.zip
→ 100% 16MB — DONE
```

---

## Step 1 — Flash Firmware onto Pico 2 W

1. **Hold BOOTSEL** button on the Pico 2 W (small button near USB port)
2. **Plug USB** into MacBook while still holding BOOTSEL
3. Release BOOTSEL — a drive called **`RPI-RP2`** mounts on your Mac
4. Open Finder → go to `RPI-RP2`
5. **Drag and drop** the firmware file onto the drive:
   ```
   downloads/adafruit-circuitpython-raspberry_pi_pico2_w-en_US-10.1.3.uf2
   ```
6. Pico reboots automatically → drive changes from `RPI-RP2` to **`CIRCUITPY`**

> If `RPI-RP2` does not appear: unplug, hold BOOTSEL again, re-plug.

---

## Step 2 — Extract Libraries

```bash
cd /Users/rifaterdemsahin/projects/raspberry-pico-2-hid/downloads

unzip adafruit-circuitpython-bundle-10.x-mpy-20260226.zip -d bundle
```

The libraries you need are inside:
```
bundle/adafruit-circuitpython-bundle-10.x-mpy-20260226/lib/
  adafruit_ble/          ← BLE radio + HID service
  adafruit_hid/          ← Keyboard / Mouse keycodes
```

---

## Step 3 — Copy Libraries to Pico

```bash
# CIRCUITPY mounts at /Volumes/CIRCUITPY
mkdir -p /Volumes/CIRCUITPY/lib

cp -r bundle/adafruit-circuitpython-bundle-10.x-mpy-20260226/lib/adafruit_ble \
      /Volumes/CIRCUITPY/lib/

cp -r bundle/adafruit-circuitpython-bundle-10.x-mpy-20260226/lib/adafruit_hid \
      /Volumes/CIRCUITPY/lib/
```

Verify:
```bash
ls /Volumes/CIRCUITPY/lib/
# Expected: adafruit_ble   adafruit_hid
```

---

## Step 4 — Write code.py

```bash
cat > /Volumes/CIRCUITPY/code.py << 'EOF'
import time
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.hid import HIDService
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

ble = BLERadio()
ble.name = "Pico2W-Keyboard"

hid = HIDService()
advertisement = ProvideServicesAdvertisement(hid)
kbd = Keyboard(hid.devices)

print("Advertising BLE HID Keyboard...")
ble.start_advertising(advertisement)

while True:
    if ble.connected:
        print("Connected!")
        time.sleep(1)
        kbd.send(Keycode.H)
        kbd.send(Keycode.I)
        time.sleep(5)
    else:
        print("Waiting for connection...")
        time.sleep(0.5)
EOF
```

---

## Step 5 — Pair on MacBook

1. Unplug USB (or keep plugged for power only)
2. **System Settings → Bluetooth**
3. Look for **`Pico2W-Keyboard`** in the device list
4. Click **Connect**
5. If asked for PIN: type `0000` or `123456`
6. Pico will type `HI` once connected

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `RPI-RP2` not appearing | Hold BOOTSEL before plugging in, not after |
| `CIRCUITPY` not appearing after flash | Re-drag the `.uf2` file |
| `Pico2W-Keyboard` not visible in Bluetooth | Check `ble.start_advertising()` runs (open Thonny → Serial console) |
| Import error for `adafruit_ble` | Confirm folder copied to `CIRCUITPY/lib/`, not `CIRCUITPY/` root |
| Paired but no keystrokes | Verify `HIDService` is in the advertisement object |
| macOS says "Not Supported" | Forget device → reset Pico → re-pair |

---

## File Layout on CIRCUITPY When Done

```
CIRCUITPY/
├── code.py
└── lib/
    ├── adafruit_ble/
    └── adafruit_hid/
```

---

---

## Session Timeline — 2026-02-27

### 14:05 — Project start
- User connected Pico 2 W to MacBook Pro via USB
- Decided to use CircuitPython + BLE HID approach

### 14:06 — Install Thonny IDE
```
# Attempt 1 — via Claude Code (non-interactive shell) — FAILED
$ brew install --cask thonny
→ Downloaded thonny-4.1.7.pkg OK
→ FAILED: sudo requires interactive terminal

# Attempt 2 — user ran in own terminal, Ctrl+C at password prompt
$ brew install --cask thonny
Password: ^C ← cancelled

# Attempt 3 — user mistakenly prefixed sudo
$ sudo brew install --cask thonny
Error: Running Homebrew as root is extremely dangerous and no longer supported.

# Attempt 4 — correct command, password entered
$ brew install --cask thonny
Password: ****
→ SUCCESS — thonny v4.1.7 installed

# Attempt 5 — re-ran to confirm
$ brew install --cask thonny
Warning: Not upgrading thonny, the latest version is already installed
→ CONFIRMED installed
```

### 14:15 — Downloads
```
# Claude Code downloaded both files automatically:

curl -L https://downloads.circuitpython.org/bin/raspberry_pi_pico2_w/en_US/adafruit-circuitpython-raspberry_pi_pico2_w-en_US-10.1.3.uf2
→ 100% 2.8MB → saved to downloads/

curl -L https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/download/20260226/adafruit-circuitpython-bundle-10.x-mpy-20260226.zip
→ 100% 16MB → saved to downloads/
```

### 14:19 — Flash firmware (Step 1) — USER ACTION
```
1. User held BOOTSEL button on Pico 2 W
2. Plugged USB into MacBook while holding BOOTSEL
3. Released BOOTSEL → RPI-RP2 drive appeared in Finder
4. Dragged adafruit-circuitpython-raspberry_pi_pico2_w-en_US-10.1.3.uf2 onto RPI-RP2
5. Pico rebooted → drive changed to CIRCUITPY

Side effect: macOS detected Pico as USB HID keyboard
→ "Keyboard Setup Assistant" popup appeared (expected — dismiss it)
→ CIRCUITPY confirmed mounted at /Volumes/CIRCUITPY
```

### 14:20 — Extract libraries (Step 2) — Automated
```
unzip adafruit-circuitpython-bundle-10.x-mpy-20260226.zip -d bundle
→ Extracted to downloads/bundle/
→ adafruit_ble/ confirmed present
→ adafruit_hid/ confirmed present
```

### 14:26 — Copy libraries to Pico (Step 3) — Automated
```
mkdir -p /Volumes/CIRCUITPY/lib
cp -r .../lib/adafruit_ble  → /Volumes/CIRCUITPY/lib/adafruit_ble
cp -r .../lib/adafruit_hid  → /Volumes/CIRCUITPY/lib/adafruit_hid
→ Libraries copied OK
```

### 14:26 — Write code.py (Step 4) — Automated
```
cat > /Volumes/CIRCUITPY/code.py
→ 727B written to CIRCUITPY

Final CIRCUITPY layout:
CIRCUITPY/
├── boot_out.txt   (157B)
├── code.py        (727B)  ← BLE HID keyboard code
├── settings.toml  (0B)
├── sd/
└── lib/
    ├── adafruit_ble/
    └── adafruit_hid/
```

### Pending — Step 5 (Pair on Mac) — USER ACTION REQUIRED
```
1. Dismiss Keyboard Setup Assistant popup on Mac
2. System Settings → Bluetooth
3. Find "Pico2W-Keyboard" in device list
4. Click Connect
5. Pico will type "HI" once paired
```

---

*Status: Steps 1–4 complete. Awaiting Bluetooth pairing (Step 5).*
