import socket
import threading
import urllib.request
import json
from datetime import datetime


def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}"
    print(entry)
    with open("honeypot.log", "a") as f:
        f.write(entry + "\n")

def get_geo(ip):
    """
    Returns geographic info for an IP address.
    Skips lookup for localhost addresses.
    """
    if ip in ("127.0.0.1", "::1", "localhost"):
        return "localhost"

    try:
        url = f"http://ip-api.com/json/{ip}?fields=country,city,isp,query"
        with urllib.request.urlopen(url, timeout=3) as response:
            data = json.loads(response.read())
            if data.get("status") == "fail":
                return "unknown location"
            return f"{data.get('city', '?')}, {data.get('country', '?')} — ISP: {data.get('isp', '?')}"
    except:
        return "location unavailable"
    
def handle_connection(conn, addr, port):
    geo = get_geo(addr[0])
    log(f"CONNECTION on port {port} from {addr[0]}:{addr[1]} — {geo}")

    try:
        conn.settimeout(3)
        data = conn.recv(1024)
        if data:
            log(f"DATA received from {addr[0]}: {data[:100]}")
    except:
        pass
    finally:
        conn.close()

def listen(port):
    """
    Opens a socket on the given port and waits for connections.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind(("0.0.0.0", port))
        server.listen(5)
        log(f"Honeypot listening on port {port}")

        while True:
            conn, addr = server.accept()
            # Handle each connection in a separate thread
            t = threading.Thread(target=handle_connection, args=(conn, addr, port))
            t.daemon = True
            t.start()

    except PermissionError:
        log(f"Permission denied on port {port}. Use ports above 1024 or run with sudo.")
    except Exception as e:
        log(f"Error on port {port}: {e}")
    finally:
        server.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 honeypot.py <port1> [port2] [port3] ...")
        print("Example: python3 honeypot.py 8080 8443 2222")
        sys.exit(1)

    ports = [int(p) for p in sys.argv[1:]]

    # Start a listener thread for each port
    threads = []
    for port in ports:
        t = threading.Thread(target=listen, args=(port,))
        t.daemon = True
        threads.append(t)
        t.start()

    print(f"\nHoneypot active on {len(ports)} port(s). Press Ctrl+C to stop.\n")

    try:
        # Keep main thread alive
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        print("\nHoneypot stopped.")