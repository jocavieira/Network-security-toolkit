import platform
import socket
import datetime


def check():
    """Returns system information."""

    # Uptime — different approach per OS
    uptime = get_uptime()

    return {
        "OS": platform.system(),
        "OS Version": platform.version(),
        "OS Release": platform.release(),
        "Hostname": socket.gethostname(),
        "Architecture": platform.machine(),
        "Python": platform.python_version(),
        "Uptime": uptime,
    }


def get_uptime():
    try:
        import psutil
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.datetime.now() - boot_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"
    except:
        return "unavailable"