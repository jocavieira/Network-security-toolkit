import psutil
import socket
import urllib.request


def check():
    """Returns network interfaces and connectivity status."""
    return {
        "Interfaces": get_interfaces(),
        "Local IP": get_local_ip(),
        "Internet": check_internet(),
    }


def get_interfaces():
    interfaces = {}
    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()

    for name, addr_list in addrs.items():
        if name in ("lo", "lo0") or name.startswith(("utun", "anpi", "llw", "gif", "stf")):
            continue

        is_up = stats[name].isup if name in stats else False
        ips = [a.address for a in addr_list if a.family == socket.AF_INET]

        if is_up and ips:
            interfaces[name] = {
                "Status": "UP",
                "IP": ips[0],
            }

    return interfaces


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "unavailable"


def check_internet():
    try:
        urllib.request.urlopen("http://www.google.com", timeout=3)
        return "CONNECTED"
    except:
        return "DISCONNECTED"