# Project: Raspberry Pi Pico 2 W — Logitext BLE/WiFi Keyboard Bridge

## Hardware
- Board: Raspberry Pi Pico 2 W (RP2350 + CYW43439)
- Host Mac: MacBook Pro (macOS)
- Target: Windows PC

## WiFi
Credentials are in `.env` — do NOT ask for them again.
- SSID: HUAWEI_H112_5E6B_5G_EXT
- See `.env` for password

## Current Architecture
Mac → WiFi (HTTP POST) → Pico 2 W → USB HID keyboard → Windows PC

## Firmware
- CircuitPython 10.1.3 (for USB HID + WiFi)
- .uf2 at: downloads/adafruit-circuitpython-raspberry_pi_pico2_w-en_US-10.1.3.uf2

## Key Files
- `code.py` — CircuitPython WiFi HTTP server + USB HID
- `settings.toml` — WiFi credentials for CircuitPython
- `send_wifi.py` — Mac script to send text to Pico over WiFi
- `send_ble.py` — Mac script to send text over BLE (MicroPython only)
- `send.py` — Mac script to send text over USB serial (MicroPython only)

## Serial Port
- Mac: /dev/cu.usbmodem21401 (may vary)
- mpremote for MicroPython file management

## Known Issues
- CircuitPython 10.1.3: BLE (adafruit_ble) broken on Pico 2 W — adapter never initializes
- MicroPython 1.27.0: no `usb` module — USB HID not available
- Solution: CircuitPython for USB HID + WiFi HTTP for Mac→Pico link
