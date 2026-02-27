#!/usr/bin/env python3
# send_wifi.py — send text to Logitext keyboard over WiFi
# Usage: python3 send_wifi.py "hello world"
#        python3 send_wifi.py --clip        (send clipboard contents)

import sys
import urllib.parse
import subprocess

PICO_IP = "auto"   # set to Pico's IP if auto-detect fails e.g. "192.168.1.42"

def find_pico_ip():
    if PICO_IP != "auto":
        return PICO_IP
    try:
        with open(".pico_ip") as f:
            return f.read().strip()
    except:
        print("No cached IP. Set PICO_IP in send_wifi.py or save IP to .pico_ip")
        sys.exit(1)

def get_clipboard():
    result = subprocess.run(["pbpaste"], capture_output=True, text=True)
    return result.stdout

if len(sys.argv) < 2:
    print('Usage: python3 send_wifi.py "text to type"')
    print('       python3 send_wifi.py --clip')
    sys.exit(1)

if sys.argv[1] == "--clip":
    text = get_clipboard()
    if not text:
        print("Clipboard is empty.")
        sys.exit(1)
    print(f"Clipboard: {text!r}")
else:
    text = sys.argv[1]
ip   = find_pico_ip()
url  = f"http://{ip}/type"
data = urllib.parse.urlencode({"text": text}).encode()

print(f"Sending to Logitext ({ip}): {text!r}")
try:
    import socket
    body = urllib.parse.urlencode({"text": text}).encode()
    request = (
        f"POST / HTTP/1.1\r\n"
        f"Host: {ip}\r\n"
        f"Content-Type: application/x-www-form-urlencoded\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    ).encode() + body
    timeout = 120 if sys.argv[1] == "--clip" else 10
    s = socket.create_connection((ip, 80), timeout=timeout)
    s.settimeout(timeout)
    s.sendall(request)
    response = b""
    while True:
        chunk = s.recv(1024)
        if not chunk:
            break
        response += chunk
    s.close()
    if b"200" in response:
        print("OK")
    else:
        print("Error response:", response.split(b"\r\n\r\n", 1)[-1].decode())
except Exception as e:
    print("Error:", e)
    print("Is Pico powered and on the same WiFi?")
