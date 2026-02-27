#!/usr/bin/env python3
# send_wifi.py — send text to Logitext keyboard over WiFi
# Usage: python3 send_wifi.py "hello world"

import sys
import urllib.request
import urllib.parse

PICO_IP = "auto"   # set to Pico's IP if auto-detect fails e.g. "192.168.1.42"

def find_pico_ip():
    # Try common IPs if auto not set
    import socket
    if PICO_IP != "auto":
        return PICO_IP
    # Read from .pico_ip cache if saved
    try:
        with open(".pico_ip") as f:
            return f.read().strip()
    except:
        print("No cached IP. Run: python3 find_pico.py  OR set PICO_IP in send_wifi.py")
        sys.exit(1)

if len(sys.argv) < 2:
    print('Usage: python3 send_wifi.py "text to type"')
    sys.exit(1)

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
    s = socket.create_connection((ip, 80), timeout=5)
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
