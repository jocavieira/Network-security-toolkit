import psutil


def check():
    """Returns CPU and memory usage."""

    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    cpu_freq = psutil.cpu_freq()

    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()

    return {
        "CPU": {
            "Usage": f"{cpu_percent}%",
            "Cores": cpu_count,
            "Frequency": f"{cpu_freq.current:.0f} MHz" if cpu_freq else "unavailable",
        },
        "Memory": {
            "Total": format_bytes(mem.total),
            "Used": format_bytes(mem.used),
            "Available": format_bytes(mem.available),
            "Usage": f"{mem.percent}%",
        },
        "Swap": {
            "Total": format_bytes(swap.total),
            "Used": format_bytes(swap.used),
            "Usage": f"{swap.percent}%",
        }
    }


def format_bytes(b):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} PB"