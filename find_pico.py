#!/usr/bin/env python3
# find_pico.py — scan network for Raspberry Pi Pico 2 W running HTTP server
import socket
import subprocess
import sys
import concurrent.futures

def get_local_network():
    """Get local network IP range to scan"""
    # Pico is typically on 192.168.3.x network (HUAWEI router)
    # Try this network first, then fall back to local network detection
    try:
        # Get local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()

        # Check if we're on the same network as Pico
        if local_ip.startswith("192.168.3."):
            return "192.168.3", local_ip

        # Otherwise, try Pico's known network first
        print(f"Local IP: {local_ip}")
        print(f"Scanning Pico's network (192.168.3.x) first...")
        return "192.168.3", local_ip
    except Exception as e:
        print(f"Error getting local network: {e}")
        # Default to Pico's known network
        return "192.168.3", "unknown"

def check_pico(ip):
    """Check if IP responds to HTTP request on port 80"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        s.connect((ip, 80))

        # Send a simple HTTP GET request
        request = b"GET / HTTP/1.1\r\nHost: " + ip.encode() + b"\r\nConnection: close\r\n\r\n"
        s.sendall(request)

        response = s.recv(1024)
        s.close()

        # Check if response mentions "Logitext" or typical Pico response
        if b"200" in response or b"400" in response:
            return True
    except:
        pass
    return False

def scan_network(network):
    """Scan network range for Pico"""
    print(f"Scanning {network}.1-254 for Pico...")
    found = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = {}
        for i in range(1, 255):
            ip = f"{network}.{i}"
            futures[executor.submit(check_pico, ip)] = ip

        for future in concurrent.futures.as_completed(futures):
            ip = futures[future]
            if future.result():
                print(f"Found device at {ip}")
                found.append(ip)

    return found

if __name__ == "__main__":
    network, local_ip = get_local_network()
    if not network:
        print("Could not determine local network")
        sys.exit(1)

    print(f"Local IP: {local_ip}")
    found = scan_network(network)

    if len(found) == 0:
        print("\nNo HTTP servers found on port 80.")
        print("Is the Pico powered on and connected to WiFi?")
        sys.exit(1)
    elif len(found) == 1:
        pico_ip = found[0]
        print(f"\nFound Pico at: {pico_ip}")

        # Save to .pico_ip file
        with open(".pico_ip", "w") as f:
            f.write(pico_ip)
        print(f"Saved IP to .pico_ip")
    else:
        print(f"\nFound {len(found)} HTTP servers:")
        for ip in found:
            print(f"  - {ip}")
        print("\nManually verify which is the Pico and save to .pico_ip")
