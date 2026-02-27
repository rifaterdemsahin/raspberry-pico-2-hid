import wifi, socketpool, usb_hid, os, time
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

KEYMAP = {
    'a':Keycode.A,'b':Keycode.B,'c':Keycode.C,'d':Keycode.D,
    'e':Keycode.E,'f':Keycode.F,'g':Keycode.G,'h':Keycode.H,
    'i':Keycode.I,'j':Keycode.J,'k':Keycode.K,'l':Keycode.L,
    'm':Keycode.M,'n':Keycode.N,'o':Keycode.O,'p':Keycode.P,
    'q':Keycode.Q,'r':Keycode.R,'s':Keycode.S,'t':Keycode.T,
    'u':Keycode.U,'v':Keycode.V,'w':Keycode.W,'x':Keycode.X,
    'y':Keycode.Y,'z':Keycode.Z,
    '0':Keycode.ZERO,'1':Keycode.ONE,'2':Keycode.TWO,
    '3':Keycode.THREE,'4':Keycode.FOUR,'5':Keycode.FIVE,
    '6':Keycode.SIX,'7':Keycode.SEVEN,'8':Keycode.EIGHT,'9':Keycode.NINE,
    ' ':Keycode.SPACE,'\n':Keycode.ENTER,'\t':Keycode.TAB,
    '.':Keycode.PERIOD,',':Keycode.COMMA,'-':Keycode.MINUS,
}

kbd = Keyboard(usb_hid.devices)

def url_decode(s):
    out = []
    i = 0
    while i < len(s):
        if s[i] == '+':
            out.append(' ')
            i += 1
        elif s[i] == '%' and i + 2 < len(s):
            try:
                out.append(chr(int(s[i+1:i+3], 16)))
                i += 3
            except ValueError:
                out.append(s[i])
                i += 1
        else:
            out.append(s[i])
            i += 1
    return ''.join(out)

def type_text(text):
    for ch in text.lower():
        if ch in KEYMAP:
            kbd.press(KEYMAP[ch])
            time.sleep(0.05)
            kbd.release_all()
            time.sleep(0.05)

print("Connecting to WiFi...")
wifi.radio.connect(
    os.getenv("CIRCUITPY_WIFI_SSID"),
    os.getenv("CIRCUITPY_WIFI_PASSWORD")
)
ip = str(wifi.radio.ipv4_address)
print("IP:", ip)

pool   = socketpool.SocketPool(wifi.radio)
server = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
server.setsockopt(pool.SOL_SOCKET, pool.SO_REUSEADDR, 1)
server.bind(("0.0.0.0", 80))
server.listen(1)
server.setblocking(False)
print("Logitext ready at http://" + ip)

buf = bytearray(4096)
chunk = bytearray(1024)
while True:
    try:
        conn, addr = server.accept()
        conn.setblocking(True)

        # Read until we have the full body
        raw = b""
        content_length = 0
        header_done = False
        while True:
            size = conn.recv_into(chunk)
            if size == 0:
                break
            raw += bytes(chunk[:size])
            if not header_done and b"\r\n\r\n" in raw:
                header_done = True
                header_part, body_part = raw.split(b"\r\n\r\n", 1)
                for line in header_part.split(b"\r\n"):
                    if line.lower().startswith(b"content-length:"):
                        content_length = int(line.split(b":", 1)[1].strip())
            if header_done and len(raw) - raw.index(b"\r\n\r\n") - 4 >= content_length:
                break

        request = raw.decode("utf-8", "ignore")
        body = request.split("\r\n\r\n", 1)[1] if "\r\n\r\n" in request else ""

        text = ""
        for part in body.split("&"):
            if part.startswith("text="):
                text = url_decode(part[5:]).strip()

        if text:
            print("Typing:", text[:40])
            # Respond immediately so Mac doesn't wait
            conn.send(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK")
            conn.close()
            type_text(text)
        else:
            conn.send(b"HTTP/1.1 400 Bad Request\r\nContent-Length: 9\r\n\r\nno text=")
            conn.close()
    except OSError:
        pass
    time.sleep(0.01)
