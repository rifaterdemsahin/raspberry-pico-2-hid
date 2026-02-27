# Pico 2 W BLE HID — Troubleshooting & Fix Log

**Date:** 2026-02-27
**Board:** Raspberry Pi Pico 2 W (RP2350 + CYW43439)
**Firmware:** CircuitPython 10.1.3
**Goal:** BLE HID Keyboard advertising to MacBook Pro

---

## Problem 1 — Hard Fault / Safe Mode

### Symptom
```
Running in safe mode! Not running saved code.
Hard fault: memory access or instruction error.
Press reset to exit safe mode.
```
- `CIRCUITPY` drive unmounted unexpectedly
- Bluetooth device `Pico2W-Keyboard` not visible on Mac
- Serial port disconnected

### Cause
Unknown at time — safe mode prevented any code from running.
Resolved by pressing RESET button and reconnecting USB.

---

## Problem 2 — `supervisor.disable_autoreload` missing

### Symptom
```
AttributeError: 'module' object has no attribute 'disable_autoreload'
  File "code.py", line 3, in <module>
```

### Cause
`supervisor.disable_autoreload()` was removed in CircuitPython 10.x.
The diagnostic code used an API that no longer exists.

### Fix
Removed the `supervisor` import and `disable_autoreload()` call entirely.
CircuitPython 10.x handles autoreload differently — not needed.

---

## Problem 3 — `Adapter not enabled` (ROOT CAUSE)

### Symptom
```
_bleio.BluetoothError: Adapter not enabled
  File "code.py", line 28, in <module>
  File "adafruit_ble/services/standard/hid.py", line 396, in __init__
  File "adafruit_ble/services/__init__.py", line 47, in __init__
```
Crash at step `[5] creating HIDService()`

### Cause
**Wrong initialization order.** `HIDService()` was created before `BLERadio()`.

On the Pico 2 W, the CYW43439 wireless chip is **off by default**.
`BLERadio()` is what powers up and enables the BLE adapter.
If `HIDService()` tries to register with the BLE stack before the adapter
is enabled, it throws `BluetoothError: Adapter not enabled`.

### Fix — Correct Initialization Order

**Wrong order (crashes):**
```python
hid = HIDService()     # ← adapter not on yet — CRASH
ble = BLERadio()
```

**Correct order (works):**
```python
ble = BLERadio()       # ← powers up CYW43439, enables BLE adapter FIRST
hid = HIDService()     # ← adapter is now on — OK
```

### Working code.py
```python
import time
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.hid import HIDService
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

# BLERadio MUST come first — enables the CYW43439 adapter
ble = BLERadio()
ble.name = "Pico2W-Keyboard"

hid = HIDService()
advertisement = ProvideServicesAdvertisement(hid)
kbd = Keyboard(hid.devices)

ble.start_advertising(advertisement)
print("Advertising as Pico2W-Keyboard")

while True:
    if ble.connected:
        print("Connected!")
        time.sleep(1)
        kbd.send(Keycode.H)
        kbd.send(Keycode.I)
        time.sleep(5)
    else:
        print("waiting...")
        time.sleep(1)
```

---

## Serial Terminal Issues

### Problem: `screen` intercepts Ctrl+D
`screen` uses Ctrl+D for its own window-split command.
Ctrl+D never reaches the Pico REPL — soft reset doesn't trigger.

### Fix: use `picocom` instead
```bash
brew install picocom
picocom -b 115200 /dev/cu.usbmodem21401
```
In picocom, Ctrl+D passes through correctly to CircuitPython.

### Problem: port busy after screen session
```
FATAL: cannot open /dev/cu.usbmodem21401: Resource busy
```
Even after `killall screen` reports no process, the port stays locked.

### Fix
```bash
# Find the PID holding the port
lsof /dev/cu.usbmodem21401

# Force kill it
kill -9 <PID>
```

---

## Timeline

| Time | Event |
|------|-------|
| 14:05 | Pico 2 W connected to Mac, project started |
| 14:06 | Thonny v4.1.7 installed via `brew install --cask thonny` (5 attempts) |
| 14:15 | Firmware + library bundle downloaded |
| 14:19 | Firmware flashed — CIRCUITPY mounted, Mac showed keyboard popup |
| 14:20 | Libraries extracted and copied to CIRCUITPY/lib/ |
| 14:26 | code.py written — BLE HID keyboard code |
| 14:30 | BLE pairing attempted — failed (Pico in safe mode) |
| 14:35 | CIRCUITPY unmounted — Pico lost USB |
| 14:40 | RESET button pressed — CIRCUITPY remounted |
| 14:45 | picocom installed, screen process force-killed |
| 14:50 | Diagnostic code revealed crash: `supervisor.disable_autoreload` missing |
| 14:52 | Fixed — removed supervisor call |
| 14:53 | Diagnostic revealed root cause: `Adapter not enabled` |
| 14:54 | **Fixed — BLERadio() moved before HIDService()** |

---

## Key Rule for Pico 2 W BLE

> Always create `BLERadio()` **first** before any BLE service.
> The CYW43439 chip is off until `BLERadio()` enables it.

---

## Problem 4 — `ConnectionError: No network with that ssid` (2.4GHz vs 5GHz)

**Date:** 2026-02-27

### Symptom
```
Connecting to WiFi...
Traceback (most recent call last):
  File "code.py", line 33, in <module>
ConnectionError: No network with that ssid
```

### Cause
`settings.toml` had the SSID set to `HUAWEI_H112_5E6B_5G_EXT` — the **5GHz** band of the router.

The CYW43439 chip on the Pico 2 W **only supports 2.4GHz WiFi**.
It cannot see 5GHz networks at all, so the SSID appears non-existent.

### Fix
Change `settings.toml` to the 2.4GHz SSID:

```toml
# Wrong — 5GHz, invisible to Pico 2 W
CIRCUITPY_WIFI_SSID = "HUAWEI_H112_5E6B_5G_EXT"

# Correct — 2.4GHz
CIRCUITPY_WIFI_SSID = "HUAWEI_H112_5E6B_EXT"
```

### Key Rule
> The Pico 2 W (CYW43439) is **2.4GHz only**.
> Always use the 2.4GHz SSID — never the `_5G` variant.

---

*Board: Pico 2 W | CircuitPython 10.1.3 | adafruit_ble bundle 20260226*
