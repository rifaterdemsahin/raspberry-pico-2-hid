# Why We Switched from CircuitPython to MicroPython
## Pico 2 W BLE HID — Firmware Change Log

**Date:** 2026-02-27
**Board:** Raspberry Pi Pico 2 W (RP2350 + CYW43439)
**Original firmware:** CircuitPython 10.1.3
**Final firmware:** MicroPython v1.27.0
**Goal:** BLE HID Keyboard named "Logitext" visible and connectable on MacBook Pro

---

## The Short Answer

CircuitPython 10.1.3 does not auto-initialize the BLE adapter on Pico 2 W.
The `_bleio.adapter` is `None` at boot and cannot be reliably set up from user code.
MicroPython v1.27.0 has a fully working built-in `bluetooth` module for Pico 2 W
with native CYW43439 BLE support.

---

## What We Tried with CircuitPython First

### Stage 1 — Standard adafruit_ble approach
Used `adafruit_ble` + `HIDService` — the standard CircuitPython BLE HID method.

**Error:**
```
_bleio.BluetoothError: Adapter not enabled
```

**Why:** `HIDService()` was created before `BLERadio()`. On Pico 2 W the
CYW43439 chip is off until `BLERadio()` powers it up.

**Fix attempted:** Moved `BLERadio()` before `HIDService()`.

---

### Stage 2 — BLERadio() first, still fails
Even with correct order, `BLERadio()` itself failed:

```
RuntimeError: No adapter available
  File "adafruit_ble/__init__.py", line 163, in __init__
```

**Why:** `_bleio.adapter` was `None`. CircuitPython 10.1.3 never initialized
the BLE adapter for Pico 2 W at boot. The board is relatively new (RP2350)
and BLE auto-init is not yet implemented in this CircuitPython version.

---

### Stage 3 — Diagnostic: checked _bleio module directly

```python
import _bleio
print(_bleio.adapter)   # → None
print(dir(_bleio))
```

**Output:**
```
None
['Adapter', 'Address', 'BluetoothError', 'Connection', ..., 'adapter', 'set_adapter']
```

Key finding: `_bleio.adapter` is `None` but `_bleio.Adapter` class exists,
meaning we could manually create the adapter if we had the right arguments.

---

### Stage 4 — Attempted manual BLE adapter init via UART HCI

`_bleio.Adapter()` requires a `uart` argument — the BLE stack on Pico 2 W
communicates with the CYW43439 chip via UART HCI (Host Controller Interface).

**Board pins checked:**
```python
import board
print(dir(board))
# No BT pins exposed — only GP0-GP28, LED, CYW0/1/2
```

No `board.BT_TX`, `board.BT_RX` etc. — unlike the original Pico W which
exposed these. The Pico 2 W board definition in CircuitPython 10.1.3 does
not expose the internal BT UART pins.

---

### Stage 5 — Found internal pins via microcontroller.pin

```python
import microcontroller
print(dir(microcontroller.pin))
# ['CYW0', 'CYW1', 'CYW2', 'GPIO0' ... 'GPIO8', 'GPIO9', ...]
```

GPIO8/9/10/11 exist. On the original Pico W these were the BT HCI UART pins.
Attempted to use them:

```python
uart = busio.UART(microcontroller.pin.GPIO8, microcontroller.pin.GPIO9, ...)
rts = digitalio.DigitalInOut(microcontroller.pin.GPIO11)
cts = digitalio.DigitalInOut(microcontroller.pin.GPIO10)
a = _bleio.Adapter(uart=uart, rts=rts, cts=cts)
a.enabled = True
_bleio.set_adapter(a)
```

**Error:**
```
_bleio.BluetoothError: Timeout waiting for HCI response
```

**Why:** The UART opened successfully on GPIO8/9 but the CYW43439 never
responded to the HCI init command. Either the pins are wrong for Pico 2 W,
the baudrate is wrong, or the chip needs a different init sequence that
CircuitPython 10.1.3 doesn't handle for this board.

---

### Stage 6 — Tried boot.py approach

Moved the BLE adapter init to `boot.py` (runs before `code.py` and before
WiFi initializes) hoping to catch the chip before WiFi claims it.

**Result:** `_bleio.adapter` still `None` in `code.py`.

**Why:** `boot.py` output is never seen in serial (runs before USB serial
connects), but the effect (or failure) carries over. The HCI timeout still
occurred silently in `boot.py`.

---

### Conclusion: CircuitPython 10.1.3 BLE on Pico 2 W is broken

| Check | Result |
|-------|--------|
| `_bleio.adapter` at boot | `None` — never auto-initialized |
| Manual `_bleio.Adapter(uart=...)` | HCI timeout — CYW43439 not responding |
| `boot.py` init | No effect — same result |
| BT UART pins in `board` module | Not exposed |
| BLE support maturity | Incomplete for RP2350 in this version |

CircuitPython support for Pico 2 W (RP2350) is newer than for Pico W (RP2040).
BLE via `adafruit_ble` is not functional in CircuitPython 10.1.3 on this board.

---

## The Switch: CircuitPython → MicroPython

### Why MicroPython works

MicroPython v1.27.0 for Pico 2 W has a fully integrated `bluetooth` module
backed by BTstack. The CYW43439 BLE adapter is initialized automatically at
firmware level — no manual UART/HCI setup needed from user code.

### What was flashed

| | CircuitPython | MicroPython |
|--|--|--|
| File | `adafruit-circuitpython-raspberry_pi_pico2_w-en_US-10.1.3.uf2` | `RPI_PICO2_W-20251209-v1.27.0.uf2` |
| Size | 2.8 MB | 1.6 MB |
| Source | circuitpython.org | micropython.org |
| BLE adapter | Not initialized | Auto-initialized |

### How it was flashed

```
1. Hold BOOTSEL button on Pico 2 W
2. Plug USB into Mac while holding BOOTSEL
3. Release BOOTSEL
4. RPI-RP2 drive appeared in Finder
5. Dragged RPI_PICO2_W-20251209-v1.27.0.uf2 onto drive
6. Pico rebooted into MicroPython (no CIRCUITPY drive — that is normal)
```

> Note: MicroPython does NOT mount as a drive like CircuitPython.
> Files are managed via `mpremote` tool.

---

## Setting Up MicroPython BLE HID

### Tools installed

```bash
pip3 install mpremote --break-system-packages
# mpremote 1.27.0 installed
```

### aioble library installed on Pico

```bash
mpremote connect /dev/cu.usbmodem21401 mip install aioble
```

**Output:**
```
Install aioble
Installing: /lib/aioble/__init__.mpy
Installing: /lib/aioble/core.mpy
Installing: /lib/aioble/device.mpy
Installing: /lib/aioble/peripheral.mpy
Installing: /lib/aioble/server.mpy
...
Done
```

### Working main.py

```python
import asyncio
import aioble
import bluetooth
import struct

_HID_UUID        = bluetooth.UUID(0x1812)
_REPORT_MAP_UUID = bluetooth.UUID(0x2A4B)
_HID_INFO_UUID   = bluetooth.UUID(0x2A4A)
_CTRL_POINT_UUID = bluetooth.UUID(0x2A4C)
_REPORT_UUID     = bluetooth.UUID(0x2A4D)

REPORT_MAP = bytes([
    0x05, 0x01, 0x09, 0x06, 0xA1, 0x01,
    0x05, 0x07, 0x19, 0xE0, 0x29, 0xE7,
    0x15, 0x00, 0x25, 0x01, 0x75, 0x01,
    0x95, 0x08, 0x81, 0x02, 0x95, 0x01,
    0x75, 0x08, 0x81, 0x01, 0x95, 0x06,
    0x75, 0x08, 0x15, 0x00, 0x25, 0x65,
    0x05, 0x07, 0x19, 0x00, 0x29, 0x65,
    0x81, 0x00, 0xC0,
])

KEY_H = 0x0B
KEY_I = 0x0C

async def main():
    hid_service = aioble.Service(_HID_UUID)
    report_map  = aioble.Characteristic(hid_service, _REPORT_MAP_UUID, read=True)
    hid_info    = aioble.Characteristic(hid_service, _HID_INFO_UUID,   read=True)
    ctrl_point  = aioble.Characteristic(hid_service, _CTRL_POINT_UUID, write=True, write_no_response=True)
    report      = aioble.Characteristic(hid_service, _REPORT_UUID,     read=True, notify=True)

    aioble.register_services(hid_service)
    report_map.write(REPORT_MAP)
    hid_info.write(bytes([0x11, 0x01, 0x00, 0x02]))
    report.write(bytes(8))

    print("BLE HID Keyboard ready — advertising as Logitext")
    while True:
        async with await aioble.advertise(
            250_000,
            name="Logitext",
            services=[_HID_UUID],
            appearance=0x03C1,   # BLE appearance = keyboard
        ) as connection:
            await asyncio.sleep_ms(1500)
            report.notify(connection, struct.pack("8B", 0, 0, KEY_H, 0, 0, 0, 0, 0))
            await asyncio.sleep_ms(80)
            report.notify(connection, bytes(8))
            await asyncio.sleep_ms(80)
            report.notify(connection, struct.pack("8B", 0, 0, KEY_I, 0, 0, 0, 0, 0))
            await asyncio.sleep_ms(80)
            report.notify(connection, bytes(8))
            await connection.disconnected()

asyncio.run(main())
```

### Deployed via mpremote

```bash
mpremote connect /dev/cu.usbmodem21401 cp main.py :main.py
mpremote connect /dev/cu.usbmodem21401 reset
```

---

## Timeline of the UF2 Switch

| Time | Event |
|------|-------|
| 14:54 | CircuitPython `Adapter not enabled` — fixed init order, still fails |
| 14:58 | Discovered `_bleio.adapter` is `None` at boot |
| 15:00 | Checked `_bleio` module — `Adapter` class exists, needs `uart` arg |
| 15:02 | No BT pins in `board` module for Pico 2 W |
| 15:03 | Found GPIO8/9/10/11 via `microcontroller.pin` |
| 15:05 | Manual HCI UART attempted — `Timeout waiting for HCI response` |
| 15:06 | `boot.py` approach tried — adapter still `None` |
| 15:07 | **Decision: CircuitPython BLE on Pico 2 W is non-functional in 10.1.3** |
| 15:07 | MicroPython v1.27.0 firmware downloaded (1.6MB) |
| 15:08 | BOOTSEL → plugged in → `RPI-RP2` appeared → UF2 dragged on |
| 15:09 | MicroPython booted — serial port `/dev/cu.usbmodem21401` confirmed |
| 15:09 | `mpremote` installed via pip3 |
| 15:10 | `aioble` installed on Pico via `mpremote mip install aioble` |
| 15:11 | `main.py` written and copied to Pico |
| 15:12 | **`Logitext` appeared in Mac Bluetooth — SUCCESS** |

---

## Key Lessons

1. **CircuitPython ≠ MicroPython for BLE on Pico 2 W**
   CircuitPython 10.1.3 BLE is broken on RP2350. MicroPython 1.27.0 works.

2. **MicroPython has no CIRCUITPY drive**
   Use `mpremote` for all file management. Files go to the Pico's internal filesystem.

3. **aioble is the right BLE library for MicroPython**
   Install via: `mpremote mip install aioble`

4. **Device name is set in the advertise call**
   `name="Logitext"` in `aioble.advertise(...)` — change here to rename.

5. **BLE keyboard appearance code is `0x03C1`**
   This tells macOS to show the device as a keyboard in Bluetooth settings.

---

*Firmware: MicroPython v1.27.0 | Library: aioble | Device name: Logitext*
