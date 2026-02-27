#!/usr/bin/env python3
# send.py — Mac-side script to type text via Logitext BLE keyboard
# Usage: python3 send.py "hello world"
#        python3 send.py "erdem"

import sys
import glob
import time

try:
    import serial
except ImportError:
    print("Install pyserial first: pip3 install pyserial --break-system-packages")
    sys.exit(1)

def find_pico_port():
    ports = glob.glob('/dev/cu.usbmodem*')
    if not ports:
        print("Pico not found. Is it plugged in via USB?")
        sys.exit(1)
    return ports[0]

if len(sys.argv) < 2:
    print("Usage: python3 send.py \"text to type\"")
    sys.exit(1)

text = sys.argv[1]
port = find_pico_port()

print(f"Sending to Logitext ({port}): {text!r}")

with serial.Serial(port, 115200, timeout=2) as ser:
    time.sleep(0.3)
    ser.write((text + "\n").encode())
    time.sleep(0.3)
    response = ser.read(ser.in_waiting).decode(errors="ignore")
    if response:
        print("Pico:", response.strip())

print("Done")
