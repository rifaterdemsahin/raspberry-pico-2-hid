# Why We Switched from Bluetooth to WiFi
## Pico 2 W Keyboard Bridge — Architecture Decision Log

**Date:** 2026-02-27
**Board:** Raspberry Pi Pico 2 W (RP2350 + CYW43439)
**Final architecture:** Mac → WiFi (HTTP) → Pico → USB HID → Windows

---

## The Goal

Build a keyboard bridge:
- Pico 2 W plugged into **Windows** via USB — appears as a keyboard
- **Mac** sends text remotely — Pico types it on Windows

---

## Why Bluetooth Didn't Work

### Attempt 1 — BLE HID to Windows directly
Pico advertised as a BLE HID keyboard (`adafruit_ble` + CircuitPython).
Windows saw "Logitext" but kept saying **"Try connecting your device again"**.

**Root cause:** Windows BLE HID requires:
- Protocol Mode characteristic (0x2A4E)
- Report Reference descriptor (0x2908)
- Bonding/security (encrypted connection)
- All of these are complex to implement in CircuitPython

**Result:** Connection always failed on Windows side.

---

### Attempt 2 — BLE from Mac → Pico, Pico USB HID → Windows
New architecture: Mac (BLE central) → Pico (BLE peripheral + USB HID) → Windows

**Problem 1: CircuitPython — BLE broken**
CircuitPython 10.1.3 on Pico 2 W: `_bleio.adapter` is `None` at boot.
The CYW43439 BLE adapter is never initialized. All workarounds failed:
- Manual `_bleio.Adapter(uart=...)` → `Timeout waiting for HCI response`
- `boot.py` early init → still `None`
- No BT UART pins exposed in `board` module for Pico 2 W

**Problem 2: MicroPython — no USB HID**
MicroPython 1.27.0 on Pico 2 W: `no module named 'usb'`
The standard firmware build doesn't include `usb.device.hid`.
BLE worked perfectly in MicroPython, but USB HID was unavailable.

**The fundamental conflict:**

| Firmware | BLE (Mac→Pico) | USB HID (Pico→Windows) |
|----------|---------------|------------------------|
| CircuitPython 10.1.3 | ❌ Broken | ✅ Built-in |
| MicroPython 1.27.0 | ✅ Works | ❌ No module |

No single firmware supports both at the same time on Pico 2 W.

---

## Why WiFi Works

### The Solution
Switch from Bluetooth to **WiFi** for the Mac → Pico link:

```
Mac → HTTP POST (WiFi) → Pico → USB HID → Windows
```

**Why this works:**
- CircuitPython has `usb_hid` (USB keyboard to Windows) ✅
- CircuitPython has `wifi` + `socketpool` (HTTP server) ✅
- Mac uses standard `urllib` — no special libraries needed ✅
- No pairing, no bonding, no BLE adapter issues ✅
- Works from anywhere on the same WiFi network ✅

### Comparison

| | Bluetooth | WiFi |
|--|-----------|------|
| Mac → Pico | BLE (bleak) | HTTP POST (urllib) |
| Pairing needed | Yes (complex on Windows) | No |
| Library on Mac | bleak (BLE) | built-in urllib |
| Pico firmware | MicroPython (BLE ✅, USB ❌) | CircuitPython (USB ✅, WiFi ✅) |
| Reliability | Flaky (adapter/bonding issues) | Solid |
| Range | ~10m BLE | WiFi network range |
| Setup complexity | High | Low |

---

## Final Setup

### Firmware
**CircuitPython 10.1.3** on Pico 2 W
- File: `adafruit-circuitpython-raspberry_pi_pico2_w-en_US-10.1.3.uf2`

### Files on Pico (CIRCUITPY)

| File | Purpose |
|------|---------|
| `settings.toml` | WiFi SSID + password |
| `boot.py` | Enable USB HID keyboard |
| `code.py` | WiFi HTTP server + USB HID typing |
| `lib/adafruit_hid/` | Keyboard keycodes |

### Files on Mac

| File | Purpose |
|------|---------|
| `send_wifi.py` | `python3 send_wifi.py "erdem"` |
| `.env` | WiFi credentials (gitignored) |
| `.pico_ip` | Cached Pico IP address |

### Usage

```bash
# Type text on Windows from Mac
python3 send_wifi.py "erdem"
python3 send_wifi.py "hello world"
python3 send_wifi.py "1 2 3 4 5"
```

---

## How to Find Pico IP (First Time)

```bash
# Method 1: read from serial after boot
picocom -b 115200 /dev/cu.usbmodem21401
# Look for: Connected! IP: 192.168.x.x

# Method 2: check router DHCP table
# Look for device named "Pico" or MAC 2C:CF:67:xx:xx:xx

# Method 3: scan network
for ip in $(seq 1 254); do
  curl -s --connect-timeout 0.3 "http://192.168.3.$ip/type" -o /dev/null \
    -w "%{http_code}" | grep -q "200\|400" && echo "Found: 192.168.3.$ip"
done
```

---

## Timeline of Architecture Changes

| Time | Decision |
|------|----------|
| 14:05 | Started with CircuitPython USB HID keyboard |
| 14:30 | CircuitPython BLE broken — can't do BLE HID |
| 15:07 | Switched to MicroPython — BLE works |
| 15:12 | MicroPython BLE to Windows — Windows rejects pairing |
| 15:30 | Changed goal: Pico USB→Windows, Mac→Pico via BLE |
| 15:45 | MicroPython: no `usb` module — USB HID impossible |
| 15:50 | **Decision: use WiFi instead of Bluetooth** |
| 15:52 | Switched back to CircuitPython + WiFi HTTP server |
| 17:10 | WiFi setup in progress |

---

*Pico 2 W | CircuitPython 10.1.3 | USB HID + WiFi HTTP | device: Logitext*
