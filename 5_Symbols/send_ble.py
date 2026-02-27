#!/usr/bin/env python3
# send_ble.py — Mac BLE sender to Logitext keyboard bridge
# Usage: python3 send_ble.py "erdem"

import asyncio
import sys
from bleak import BleakScanner, BleakClient

DEVICE_NAME = "Logitext"
NUS_RX_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"  # write text here

async def send(text):
    print(f"Scanning for {DEVICE_NAME}...")
    device = await BleakScanner.find_device_by_name(DEVICE_NAME, timeout=10)
    if not device:
        print(f"'{DEVICE_NAME}' not found. Is Pico powered and advertising?")
        return

    print(f"Found {device.name} — connecting...")
    async with BleakClient(device) as client:
        print("Connected via BLE")
        await client.write_gatt_char(NUS_RX_UUID, (text + "\n").encode(), response=False)
        print(f"Sent: {text!r}")
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python3 send_ble.py "text to type"')
        sys.exit(1)
    asyncio.run(send(sys.argv[1]))
