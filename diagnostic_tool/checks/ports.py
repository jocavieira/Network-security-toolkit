import socket


# Most common ports to check
COMMON_PORTS = {
    21:   "FTP",
    22:   "SSH",
    23:   "Telnet",
    25:   "SMTP",
    53:   "DNS",
    80:   "HTTP",
    110:  "POP3",
    143:  "IMAP",
    443:  "HTTPS",
    445:  "SMB",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    5900: "VNC",
    6379: "Redis",
    8080: "HTTP-alt",
    8443: "HTTPS-alt",
    27017:"MongoDB",
}


def check(host="localhost", timeout=0.5):
    """Checks which common ports are open on the host."""
    open_ports = {}
    closed_ports = {}

    for port, service in COMMON_PORTS.items():
        if is_open(host, port, timeout):
            open_ports[port] = service
        else:
            closed_ports[port] = service

    return {
        "Host": host,
        "Open": open_ports,
        "Closed count": len(closed_ports),
    }


def is_open(host, port, timeout=0.5):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False