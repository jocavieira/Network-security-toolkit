import subprocess
import platform


def check():
    """Checks firewall status depending on OS."""

    os_name = platform.system()

    if os_name == "Darwin":
        return check_macos()
    elif os_name == "Linux":
        return check_linux()
    elif os_name == "Windows":
        return check_windows()
    else:
        return {"Status": "unsupported OS"}


def check_macos():
    try:
        result = subprocess.run(
            ["/usr/libexec/ApplicationFirewall/socketfilterfw", "--getglobalstate"],
            capture_output=True, text=True, timeout=5
        )
        output = result.stdout.strip()

        if "enabled" in output.lower():
            status = "ENABLED"
        elif "disabled" in output.lower():
            status = "DISABLED"
        else:
            status = "unknown"

        return {
            "Status": status,
            "Stealth mode": get_stealth_mode(),
            "Raw": output,
        }
    except Exception as e:
        return {"Status": "error", "Detail": str(e)}


def get_stealth_mode():
    try:
        result = subprocess.run(
            ["/usr/libexec/ApplicationFirewall/socketfilterfw", "--getstealthmode"],
            capture_output=True, text=True, timeout=5
        )
        output = result.stdout.strip().lower()
        return "ENABLED" if "enabled" in output else "DISABLED"
    except:
        return "unavailable"

def check_linux():
    # Try ufw first
    try:
        result = subprocess.run(
            ["ufw", "status"],
            capture_output=True, text=True, timeout=5
        )
        if "Status: active" in result.stdout:
            return {"Status": "ENABLED (ufw)", "Detail": result.stdout.strip()}
        elif "Status: inactive" in result.stdout:
            return {"Status": "DISABLED (ufw)"}
    except:
        pass

    # Try iptables
    try:
        result = subprocess.run(
            ["iptables", "-L", "--line-numbers"],
            capture_output=True, text=True, timeout=5
        )
        rules = [l for l in result.stdout.splitlines()
                 if l.strip() and not l.startswith("Chain")]
        return {
            "Status": "ENABLED (iptables)" if rules else "No rules (iptables)",
            "Rules count": len(rules),
        }
    except:
        return {"Status": "unavailable — run with sudo"}


def check_windows():
    try:
        result = subprocess.run(
            ["netsh", "advfirewall", "show", "allprofiles", "state"],
            capture_output=True, text=True, timeout=5
        )
        profiles = {}
        current = None
        for line in result.stdout.splitlines():
            line = line.strip()
            if "Profile Settings" in line:
                current = line.split()[0]
            elif "State" in line and current:
                profiles[current] = line.split()[-1]
        return {"Status": "OK", "Profiles": profiles}
    except Exception as e:
        return {"Status": "error", "Detail": str(e)}