# How to Connect Pico 2 W as Bluetooth Keyboard

**Date:** 2026-02-27
**Status:** Code loaded — BLE advertising must be running before pairing

---

## Do You Press a Button?

**No button needed to connect via Bluetooth.**

The Pico advertises automatically when `code.py` runs.
You only use buttons for these specific situations:

| Button | When to press | Purpose |
|--------|---------------|---------|
| **RESET** (small button) | Code crashed / safe mode | Restart code.py |
| **BOOTSEL** (other button) | Re-flashing firmware only | Enter USB bootloader |
| **Nothing** | Normal BLE pairing | Pico advertises on its own |

---

## Normal Connection Flow

```
Power on Pico (USB to any power source)
        ↓
CircuitPython boots (~3 seconds)
        ↓
code.py runs automatically
        ↓
Pico starts BLE advertising as "Pico2W-Keyboard"
        ↓
Open Mac → System Settings → Bluetooth
        ↓
Click "Pico2W-Keyboard" → Connect
        ↓
Connected — Pico types "HI"
```

---

## Current Status — ISSUE: Safe Mode

> The Pico crashed on the last boot with a hard fault.
> BLE is NOT advertising right now until this is fixed.

**Symptoms:**
- `CIRCUITPY` drive unmounted unexpectedly
- Serial console showed:
  ```
  Running in safe mode! Not running saved code.
  Hard fault: memory access or instruction error.
  Press reset to exit safe mode.
  ```

**Fix needed before Bluetooth will work** — see section below.

---

## Step-by-Step: Connect after Fix

### 1. Power the Pico
Plug USB into any power source (Mac, charger, power bank).
No BOOTSEL needed — just plug in normally.

### 2. Wait 3–5 seconds
CircuitPython boots and code.py runs automatically.
The onboard LED may flash briefly.

### 3. Open Bluetooth on Mac
`System Settings → Bluetooth`

### 4. Look for "Pico2W-Keyboard"
It appears in the **"Other Devices"** or **"Nearby Devices"** section.
If it doesn't appear within 30 seconds → see troubleshooting below.

### 5. Click Connect
No PIN required (or try `0000` if asked).

### 6. Confirm
Pico sends keystrokes `H` then `I` once connected.

---

## Troubleshooting: Device Not Appearing

| Check | Action |
|-------|--------|
| Is code.py running? | Connect USB to Mac → open Thonny → check serial output |
| Is Pico in safe mode? | Press RESET button once → wait 5 sec → check Bluetooth again |
| Was it paired before and failed? | Mac: forget "Pico2W-Keyboard" in Bluetooth settings → retry |
| Still nothing? | Hold BOOTSEL + plug in → re-flash firmware → redo setup |

---

## How to Check if BLE is Advertising (Serial Monitor)

Connect USB to Mac, open terminal:

```bash
# Find the serial port
ls /dev/cu.usbmodem*

# Read serial output (replace port name)
screen /dev/cu.usbmodem21401 115200
```

You should see:
```
Advertising BLE HID Keyboard...
```

If you see `safe mode` or nothing → press RESET and check again.
Exit screen: `Ctrl+A` then `K` then `Y`

---

## Current Fix Required

The hard fault is likely caused by the `adafruit_ble` library
conflicting with CircuitPython 10.1.3 on Pico 2 W.

**Planned fix:** step-by-step diagnostic to isolate crash point,
then update code.py with working BLE initialization.

---

*Pico 2 W: RP2350 + CYW43439 | CircuitPython 10.1.3 | adafruit_ble bundle 20260226*
