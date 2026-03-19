import psutil


# Thresholds for suspicious processes
CPU_THRESHOLD    = 50.0  # % CPU
MEMORY_THRESHOLD = 10.0  # % RAM


def check():
    """Returns processes consuming high CPU or memory."""

    high_cpu    = []
    high_memory = []

    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'username']):
        try:
            info = proc.info

            if info['cpu_percent'] and info['cpu_percent'] > CPU_THRESHOLD:
                high_cpu.append({
                    "PID":     info['pid'],
                    "Name":    info['name'],
                    "CPU":     f"{info['cpu_percent']:.1f}%",
                    "User":    info['username'],
                })

            if info['memory_percent'] and info['memory_percent'] > MEMORY_THRESHOLD:
                high_memory.append({
                    "PID":     info['pid'],
                    "Name":    info['name'],
                    "Memory":  f"{info['memory_percent']:.1f}%",
                    "User":    info['username'],
                })

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return {
        "Thresholds": {
            "CPU":    f">{CPU_THRESHOLD}%",
            "Memory": f">{MEMORY_THRESHOLD}%",
        },
        "High CPU":    high_cpu    if high_cpu    else ["none"],
        "High Memory": high_memory if high_memory else ["none"],
    }
