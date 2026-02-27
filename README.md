# Logitext — Raspberry Pi Pico 2 W WiFi Keyboard Bridge

🌐 **[Live Site → rifaterdemsahin.github.io/raspberry-pico-2-hid](https://rifaterdemsahin.github.io/raspberry-pico-2-hid/)**

Send text from your Mac to a Windows PC over WiFi using a Raspberry Pi Pico 2 W as a USB HID keyboard.

```
Mac  ──WiFi HTTP──►  Pico 2 W  ──USB HID──►  Windows PC
```

---

## Hardware

- Raspberry Pi Pico 2 W (RP2350 + CYW43439 WiFi chip)
- USB cable (Pico → Windows PC)
- Mac and Windows PC on the same 2.4GHz WiFi network

---

## Setup

### 1. Flash CircuitPython

Download CircuitPython 10.1.3 for Pico 2 W and flash it:

1. Hold BOOTSEL on the Pico and plug into Mac
2. Copy `adafruit-circuitpython-raspberry_pi_pico2_w-en_US-10.1.3.uf2` to the RPI-RP2 drive
3. Pico reboots and mounts as `CIRCUITPY`

### 2. Install Libraries

Copy these to `CIRCUITPY/lib/`:
- `adafruit_hid/` (keyboard + keycode)

### 3. Configure WiFi

Edit `CIRCUITPY/settings.toml`:

```toml
CIRCUITPY_WIFI_SSID = "YourNetwork_2.4GHz"
CIRCUITPY_WIFI_PASSWORD = "yourpassword"
```

> **Important:** The Pico 2 W's CYW43439 chip is **2.4GHz only**.
> Do not use a 5GHz SSID (e.g. anything with `_5G` in the name).

### 4. Deploy code.py

Copy `code.py` to the root of `CIRCUITPY/`. It will auto-run.

On boot the Pico prints its IP:
```
Connecting to WiFi...
IP: 192.168.3.214
Logitext ready at http://192.168.3.214
```

### 5. Save the Pico's IP

```bash
echo "192.168.3.214" > .pico_ip
```

### 6. Plug Pico into Windows

Move the USB cable to the Windows PC. The Pico acts as a USB HID keyboard on Windows while staying connected to WiFi.

---

## Usage

With the Pico plugged into Windows and both Mac + Pico on the same WiFi:

```bash
python3 send_wifi.py "hello world"
```

The text is typed on the Windows PC via USB HID.

---

## How It Works

1. `send_wifi.py` on Mac sends an HTTP POST to the Pico's IP on port 80
2. The Pico's HTTP server receives the request and extracts the `text=` body field
3. The Pico types each character via `adafruit_hid.keyboard` over USB to Windows

---

## Troubleshooting

### `ConnectionError: No network with that ssid`
The Pico can't see your WiFi network. Check that you're using the **2.4GHz** SSID, not the 5GHz one.

### Pico connects but send_wifi.py times out
The HTTP server is running but `recv_into` returns before the request body arrives (TCP split segments). Fixed in `send_wifi.py` by using a raw socket to send headers + body in a single `sendall()` call.

### Pico not found on network
- Run `arp -a` to check recently seen devices
- Connect the Pico back to Mac via USB — the serial output shows the IP in the terminal title: `🐍192.168.3.xxx | code.py`
- Save the IP to `.pico_ip`

### Port busy on Mac serial
```bash
lsof /dev/cu.usbmodem21401
kill -9 <PID>
```

---

## Files

| File | Description |
|------|-------------|
| `code.py` | CircuitPython firmware — WiFi HTTP server + USB HID |
| `settings.toml` | WiFi credentials (on CIRCUITPY drive) |
| `send_wifi.py` | Mac script — sends text to Pico over WiFi |
| `semblance.md` | Troubleshooting log with root causes and fixes |
| `FLASH_FORMULA.md` | Step-by-step firmware flashing guide |

---

## Known Limitations

- CircuitPython 10.1.3 BLE is broken on Pico 2 W — WiFi is used instead
- MicroPython 1.27.0 has no `usb` module — USB HID unavailable
- Windows PC must NOT be the only network path — it can be on VPN, the Pico communicates via WiFi independently
