# Raspberry Pi Pico 2 W — Bluetooth HID Keyboard Formula

**Target:** Pico 2 W (RP2350 + CYW43439) acting as a BLE HID keyboard
**Host:** MacBook Pro (macOS)
**Protocol:** Bluetooth Low Energy (BLE) HID over GATT

---

## Hardware Confirmed

| Component | Detail |
|-----------|--------|
| Board | Raspberry Pi Pico 2 W |
| Chip | RP2350 + CYW43439 |
| Wireless | WiFi 802.11n + Bluetooth 5.2 (BLE + Classic) |
| Connection | USB (for flashing) → Bluetooth (for HID) |

---

## Option A — CircuitPython (Recommended / Easiest)

### Step 1: Install on Mac

```bash
# No special Mac tools needed — Pico mounts as USB drive
# Optionally install Thonny IDE for code editing
brew install --cask thonny
```

**Install log (2026-02-27):**
```
# Attempt 1 — via Claude Code (non-interactive shell)
$ brew install --cask thonny
Homebrew auto-updated (5 taps updated)
Downloading thonny-4.1.7.pkg ... OK
Installing Cask thonny ...
FAILED: sudo requires interactive terminal — password prompt not reachable

# Attempt 2 — user ran in own terminal, Ctrl+C at password prompt
$ brew install --cask thonny
Password: ^C   ← cancelled

# Attempt 3 — user mistakenly ran with sudo prefix
$ sudo brew install --cask thonny
Error: Running Homebrew as root is extremely dangerous and no longer supported.

# Attempt 4 — user ran correctly, password entered at prompt
$ brew install --cask thonny
Password: ****
→ SUCCESS

# Attempt 5 — user re-ran to confirm
$ brew install --cask thonny
Warning: Not upgrading thonny, the latest version is already installed
→ CONFIRMED: thonny v4.1.7 installed
```

### Step 2: Flash CircuitPython Firmware

1. Hold **BOOTSEL** button on Pico 2 W
2. Plug USB into MacBook → Pico appears as `RPI-RP2` drive
3. Download firmware: https://circuitpython.org/board/raspberry_pi_pico2_w/
4. Drag `.uf2` file onto the `RPI-RP2` drive
5. Pico reboots → mounts as `CIRCUITPY` drive

### Step 3: Install Libraries

Download the CircuitPython library bundle:
https://circuitpython.org/libraries

Copy these folders into `CIRCUITPY/lib/`:

```
adafruit_ble/
adafruit_ble_radio/          # optional
adafruit_hid/
```

### Step 4: Write the Keyboard Code

Create `CIRCUITPY/code.py`:

```python
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
```

### Step 5: Pair on MacBook

1. Unplug USB (or keep it for power)
2. System Settings → Bluetooth
3. Find **Pico2W-Keyboard** → click Connect
4. Done — it will type "HI" once connected

---

## Option B — MicroPython + aioble

### Step 1: Flash MicroPython

1. Hold **BOOTSEL**, plug in → `RPI-RP2` appears
2. Download: https://micropython.org/download/RPI_PICO2_W/
3. Drag `.uf2` onto drive

### Step 2: Install mpremote on Mac

```bash
pip3 install mpremote
```

### Step 3: Upload aioble Library

```bash
# Clone MicroPython extras
git clone https://github.com/micropython/micropython-lib

# Copy aioble to Pico
mpremote mip install aioble
```

### Step 4: HID Keyboard Code

MicroPython BLE HID requires manual GATT profile construction.
Use this minimal example (`main.py`):

```python
import bluetooth
import struct
import time
from micropython import const

# BLE HID flags
_IO_CAPABILITY_NO_INPUT_OUTPUT = const(3)
_HID_SERVICE_UUID = bluetooth.UUID(0x1812)
_REPORT_CHAR_UUID = bluetooth.UUID(0x2A4D)

# Minimal keyboard report descriptor
HID_REPORT_DESC = bytes([
    0x05, 0x01,  # Usage Page (Generic Desktop)
    0x09, 0x06,  # Usage (Keyboard)
    0xA1, 0x01,  # Collection (Application)
    0x05, 0x07,  # Usage Page (Key Codes)
    0x19, 0xE0,  # Usage Minimum (224)
    0x29, 0xE7,  # Usage Maximum (231)
    0x15, 0x00,  # Logical Minimum (0)
    0x25, 0x01,  # Logical Maximum (1)
    0x75, 0x01,  # Report Size (1)
    0x95, 0x08,  # Report Count (8)
    0x81, 0x02,  # Input (Data, Variable, Absolute) -- Modifier Keys
    0x95, 0x01,  # Report Count (1)
    0x75, 0x08,  # Report Size (8)
    0x81, 0x01,  # Input (Constant) -- Reserved
    0x95, 0x06,  # Report Count (6)
    0x75, 0x08,  # Report Size (8)
    0x15, 0x00,  # Logical Minimum (0)
    0x25, 0x65,  # Logical Maximum (101)
    0x05, 0x07,  # Usage Page (Key Codes)
    0x19, 0x00,  # Usage Minimum (0)
    0x29, 0x65,  # Usage Maximum (101)
    0x81, 0x00,  # Input (Data, Array)
    0xC0        # End Collection
])

# See full example: https://github.com/micropython/micropython/tree/master/examples/bluetooth
print("BLE HID Keyboard - see full example in micropython repo")
```

> Note: Full MicroPython BLE HID requires ~150 lines. Use CircuitPython for simplicity.

---

## Option C — C/C++ SDK + BTstack (Most Control)

### Step 1: Install Tools on Mac

```bash
# Install Pico SDK dependencies
brew install cmake python3 git

# Install ARM GCC toolchain
brew install --cask gcc-arm-embedded
# OR
brew install arm-none-eabi-gcc

# Clone Pico SDK
git clone --recurse-submodules https://github.com/raspberrypi/pico-sdk ~/pico-sdk

# Set environment variable
echo 'export PICO_SDK_PATH=~/pico-sdk' >> ~/.zshrc
source ~/.zshrc
```

### Step 2: Build BTstack HID Example

```bash
# BTstack examples are bundled in pico-sdk extras
git clone https://github.com/raspberrypi/pico-examples
cd pico-examples
mkdir build && cd build
cmake .. -DPICO_BOARD=pico2_w
make pico_w/bluetooth/hid_keyboard -j4
```

### Step 3: Flash

1. Hold **BOOTSEL**, plug in
2. Copy `hid_keyboard.uf2` to `RPI-RP2` drive

---

## Quick Comparison

| | CircuitPython | MicroPython | C SDK |
|---|---|---|---|
| Difficulty | Easy | Medium | Hard |
| Setup time | ~15 min | ~30 min | ~1 hour |
| BLE HID library | Built-in (adafruit_ble) | Manual GATT | BTstack |
| Customisation | Medium | High | Full |
| Recommended for | Prototyping | Scripting | Production |

---

## Mac-Side Checklist

- [ ] Bluetooth turned ON in System Settings
- [ ] Remove old Pico pairings if re-flashing (Settings → Bluetooth → forget device)
- [ ] If pairing fails: put Pico in advertising mode again (reset board)
- [ ] macOS may ask for a PIN — enter `0000` or `123456`

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `CIRCUITPY` drive not appearing | Re-flash CircuitPython firmware |
| BLE device not visible on Mac | Check `ble.start_advertising()` is called |
| Paired but keys not working | Verify `HIDService` is in advertisement |
| Import errors | Confirm library folders are in `CIRCUITPY/lib/` |
| Bond/pairing issues on macOS | Forget device on Mac + reset Pico, re-pair |

---

## Key Links

- CircuitPython for Pico 2 W: https://circuitpython.org/board/raspberry_pi_pico2_w/
- CircuitPython Library Bundle: https://circuitpython.org/libraries
- MicroPython for Pico 2 W: https://micropython.org/download/RPI_PICO2_W/
- Pico SDK: https://github.com/raspberrypi/pico-sdk
- adafruit_hid keycodes: https://docs.circuitpython.org/projects/hid/en/latest/

---

*Board: Raspberry Pi Pico 2 W | Protocol: BLE HID over GATT | Host: macOS*
