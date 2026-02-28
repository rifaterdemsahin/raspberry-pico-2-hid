#!/usr/bin/env python3
# perf_test.py — Performance testing for Pico WiFi HID keyboard
# Measures timing from send to completion of typing

import sys
import time
import json
import os
from datetime import datetime

# Import send_wifi functionality
sys.path.insert(0, os.path.dirname(__file__))
from send_wifi import find_pico_ip

PERF_LOG = "performance.log"

def send_with_timing(text):
    """Send text and measure timing"""
    import socket
    import urllib.parse

    ip = find_pico_ip()

    # Timing markers
    send_start = time.time()

    # Prepare request
    body = urllib.parse.urlencode({"text": text}).encode()
    request = (
        f"POST / HTTP/1.1\r\n"
        f"Host: {ip}\r\n"
        f"Content-Type: application/x-www-form-urlencoded\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    ).encode() + body

    timeout = 120

    try:
        # Send request
        s = socket.create_connection((ip, 80), timeout=timeout)
        s.settimeout(5)  # Short timeout since Pico responds quickly
        s.sendall(request)
        send_complete = time.time()

        # Wait for response (Pico closes connection after responding)
        response = b""
        try:
            while True:
                chunk = s.recv(1024)
                if not chunk:
                    break
                response += chunk
        except:
            pass  # Connection closed by Pico is expected
        s.close()
        response_received = time.time()

        # Calculate timings
        send_time = (send_complete - send_start) * 1000  # ms
        response_time = (response_received - send_start) * 1000  # ms

        return {
            "success": b"200" in response,
            "send_time_ms": round(send_time, 2),
            "response_time_ms": round(response_time, 2),
            "send_start": send_start
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "send_start": send_start
        }

def wait_for_user_completion(auto_mode=False, auto_delay=40):
    """Wait for user to confirm typing completed"""
    if auto_mode:
        print("\n" + "="*60)
        print(f"AUTO MODE: Waiting {auto_delay} seconds for typing to complete...")
        print("="*60)
        time.sleep(auto_delay)
        return time.time()
    else:
        print("\n" + "="*60)
        print("PRESS ENTER when the Pico finishes typing on the target PC")
        print("="*60)
        input()
        return time.time()

def log_performance(text, timing_data, completion_time):
    """Log performance data to file"""
    char_count = len(text)
    send_start = timing_data["send_start"]
    total_time = (completion_time - send_start) * 1000  # ms

    log_entry = {
        "timestamp": datetime.fromtimestamp(send_start).isoformat(),
        "text_length": char_count,
        "send_time_ms": timing_data.get("send_time_ms", 0),
        "response_time_ms": timing_data.get("response_time_ms", 0),
        "total_completion_ms": round(total_time, 2),
        "chars_per_second": round(char_count / (total_time / 1000), 2) if total_time > 0 else 0,
        "success": timing_data["success"]
    }

    # Append to log file
    with open(PERF_LOG, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return log_entry

def print_results(log_entry):
    """Print formatted results"""
    print("\n" + "="*60)
    print("PERFORMANCE RESULTS")
    print("="*60)
    print(f"Text Length:        {log_entry['text_length']} characters")
    print(f"Send Time:          {log_entry['send_time_ms']} ms")
    print(f"Response Time:      {log_entry['response_time_ms']} ms")
    print(f"Total Time:         {log_entry['total_completion_ms']} ms")
    print(f"Typing Speed:       {log_entry['chars_per_second']} chars/sec")
    print(f"Success:            {log_entry['success']}")
    print("="*60)
    print(f"\nLogged to: {PERF_LOG}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python perf_test.py \"text to test\"")
        print("       python perf_test.py --long    (use predefined long text)")
        print("       python perf_test.py --long --auto <seconds>  (auto-complete after N seconds)")
        sys.exit(1)

    # Check for auto mode
    auto_mode = False
    auto_delay = 40  # default
    if "--auto" in sys.argv:
        auto_mode = True
        auto_idx = sys.argv.index("--auto")
        if auto_idx + 1 < len(sys.argv) and sys.argv[auto_idx + 1].isdigit():
            auto_delay = int(sys.argv[auto_idx + 1])

    # Predefined long test text
    LONG_TEXT = """The quick brown fox jumps over the lazy dog. This is a performance test for the Raspberry Pi Pico 2 W WiFi keyboard bridge. We are measuring the time it takes to send text over WiFi and type it via USB HID. This test includes multiple sentences with various punctuation marks, numbers like 123, 456, 789, and special characters. The goal is to measure real-world performance."""

    if sys.argv[1] == "--long":
        text = LONG_TEXT
        print(f"Testing with long text ({len(text)} characters)...")
    else:
        text = sys.argv[1]

    print(f"\nSending: {text[:50]}{'...' if len(text) > 50 else ''}")
    print(f"Length: {len(text)} characters\n")

    # Send and measure
    timing_data = send_with_timing(text)

    if not timing_data["success"]:
        print(f"Error: {timing_data.get('error', 'Unknown error')}")
        sys.exit(1)

    print(f"[OK] Sent to Pico (took {timing_data['send_time_ms']} ms)")
    print(f"[OK] Response received (took {timing_data['response_time_ms']} ms)")

    # Wait for user confirmation
    completion_time = wait_for_user_completion(auto_mode, auto_delay)

    # Log and display results
    log_entry = log_performance(text, timing_data, completion_time)
    print_results(log_entry)
