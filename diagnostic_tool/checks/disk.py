import psutil
import platform
import subprocess


def check():
    """Returns disk usage. On macOS reads APFS volumes correctly."""
    
    if platform.system() == "Darwin":
        return check_macos()
    
    # Linux and Windows
    partitions = psutil.disk_partitions()
    result = {}
    for partition in partitions:
        if any(skip in partition.mountpoint for skip in [
            "/System/Volumes", "/private/var/vm",
            "/dev", "/run", "/sys", "/proc"
        ]):
            continue
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            result[partition.mountpoint] = {
                "Device": partition.device,
                "File System": partition.fstype,
                "Total": format_bytes(usage.total),
                "Used": format_bytes(usage.used),
                "Free": format_bytes(usage.free),
                "Usage": f"{usage.percent}%",
                "Status": status(usage.percent),
            }
        except PermissionError:
            result[partition.mountpoint] = {"Status": "permission denied"}
    return result


def check_macos():
    """Reads all APFS volumes and sums used space."""
    try:
        # Volumes to include in used space calculation
        volumes = {
        "disk3s1": "Macintosh HD - Data",
        "disk3s3": "Macintosh HD (System)",
        "disk3s4": "Preboot",
        "disk3s6": "VM",
        }

        total = free = None
        total_used = 0

        for disk, name in volumes.items():
            result = subprocess.run(
                ["diskutil", "info", disk],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.splitlines():
                line = line.strip()
                if "Container Total Space" in line and total is None:
                    total = extract_bytes(line)
                elif "Container Free Space" in line and free is None:
                    free = extract_bytes(line)
                elif "Volume Used Space" in line:
                    val = extract_bytes(line)
                    if val:
                        total_used += val

        if total and free and total_used:
            percent = (total_used / total) * 100
            return {
                "Macintosh HD": {
                    "Total": format_bytes(total),
                    "Used": format_bytes(total_used),
                    "Free": format_bytes(free),
                    "Usage": f"{percent:.1f}%",
                    "Status": status(percent),
                }
            }
    except:
        pass

    # Fallback
    usage = psutil.disk_usage("/")
    return {
        "/": {
            "Total": format_bytes(usage.total),
            "Used": format_bytes(usage.used),
            "Free": format_bytes(usage.free),
            "Usage": f"{usage.percent}%",
            "Status": status(usage.percent),
        }
    }
def extract_bytes(line):
    """Extracts byte value from diskutil output line."""
    try:
        parts = line.split("(")
        if len(parts) > 1:
            return int(parts[1].split()[0])
    except:
        pass
    return None
def status(percent):
    if percent >= 90:
        return "CRITICAL"
    elif percent >= 75:
        return "WARNING"
    return "OK"


def format_bytes(b):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} PB"