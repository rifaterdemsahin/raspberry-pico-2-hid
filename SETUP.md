# Setup Guide — Raspberry Pi Pico 2 W HID Keyboard

## Quick Start (New Machine)

### 1. Find the Pico on the Network
```bash
python find_pico.py
```

This will:
- Scan the network (defaults to 192.168.3.x where the Pico typically connects)
- Detect HTTP servers on port 80
- Automatically save the Pico's IP to `.pico_ip`

If multiple devices are found, manually verify which is the Pico and save its IP:
```bash
echo "192.168.3.xxx" > .pico_ip
```

### 2. Test the Connection
```bash
python send_wifi.py "hello world"
```

This sends text to the Pico, which types it via USB HID.

### 3. Send Clipboard Contents
```bash
python send_wifi.py --clip
```

---

## Network Configuration

**Known Networks:**
- **Pico Network:** 192.168.3.x (HUAWEI_H112_5E6B_5G_EXT router)
- **WiFi SSID:** HUAWEI_H112_5E6B_5G_EXT
- **WiFi Password:** Stored in `.env` and `settings.toml`

The Pico connects to this WiFi network on boot and gets a DHCP IP address.

---

## Files

| File | Purpose |
|------|---------|
| `find_pico.py` | Network scanner to locate Pico's IP address |
| `.pico_ip` | Cached IP address (auto-created by find_pico.py) |
| `send_wifi.py` | Send text to Pico over WiFi |
| `code.py` | CircuitPython firmware (runs on Pico) |
| `settings.toml` | WiFi credentials (on Pico's CIRCUITPY drive) |

---

## Troubleshooting

### Pico Not Found
1. Verify Pico is powered on (check for LED activity)
2. Ensure Pico is connected to WiFi (HUAWEI_H112_5E6B_5G_EXT)
3. Check serial console output for IP address:
   ```
   Connecting to WiFi...
   IP: 192.168.3.xxx
   Logitext ready at http://192.168.3.xxx
   ```
4. Manually save IP to `.pico_ip` if auto-detection fails

### Wrong Network
If your computer is on a different network (e.g., 10.x.x.x), the Pico may not be reachable. Either:
- Connect your computer to the same WiFi network as the Pico
- Modify `find_pico.py` to scan your local network

### Multiple Devices Found
The scanner may find other HTTP servers. Test each one:
```bash
echo "192.168.3.xxx" > .pico_ip
python send_wifi.py "test"
```

The correct device will respond with `OK` and type the text.

---

## Architecture

```
Mac (send_wifi.py)
    |
    | HTTP POST /type
    | text=hello+world
    |
    v
Pico 2 W (code.py)
    |
    | USB HID Keyboard
    |
    v
Windows PC
```

The Pico acts as a WiFi-to-USB bridge, receiving text over HTTP and typing it as a USB keyboard.
