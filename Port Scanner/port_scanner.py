import socket
import sys

def get_service(port):
    """
    Returns the service name for a given port.
    Falls back to 'unknown' if not recognized.
    """
    try:
        return socket.getservbyport(port)
    except:
        return "unknown"
def scan_port(host, port, timeout=1):
    """
    Tenta conectar na porta especificada.
    Retorna True se aberta, False se fechada.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except socket.gaierror:
        print(f"Hostname '{host}' not found.")
        sys.exit(1)
    except socket.error as e:
        print(f"Connection error: {e}")
        sys.exit(1)

def scan_range(host, start_port, end_port, timeout=1, output_file=None):
    print(f"\nScanning {host} from port {start_port} to {end_port}...")

    from datetime import datetime
    start_time = datetime.now()
    print(f"Started at: {start_time.strftime('%H:%M:%S')}\n")

    open_ports = []
    lines = []
    lines.append(f"Scan report for {host}")
    lines.append(f"Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Port range: {start_port} - {end_port}")
    lines.append("-" * 40)

    for port in range(start_port, end_port + 1):
        if scan_port(host, port, timeout):
            service = get_service(port)
            print(f"  Port {port:5d}  OPEN  {service}")
            open_ports.append(port)
            lines.append(f"Port {port:5d}  OPEN  {service}")

    end_time = datetime.now()
    duration = (end_time - start_time).seconds

    summary = f"\nScan complete. {len(open_ports)} open port(s) found. Duration: {duration}s"
    print(summary)
    lines.append(summary)

    # Save to file if requested
    if output_file:
        with open(output_file, 'w') as f:
            f.write('\n'.join(lines))
        print(f"Results saved to {output_file}")

    return open_ports


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 port_scanner.py <host> <start_port> <end_port> [output_file]")
        print("Example: python3 port_scanner.py localhost 1 1024 results.txt")
        sys.exit(1)

    host  = sys.argv[1]
    start = int(sys.argv[2])
    end   = int(sys.argv[3])
    out   = sys.argv[4] if len(sys.argv) > 4 else None

    scan_range(host, start, end, output_file=out)