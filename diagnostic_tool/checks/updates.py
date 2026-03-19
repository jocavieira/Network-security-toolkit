import subprocess
import platform


def check():
    """Checks for pending system updates depending on OS."""
    
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
            ["softwareupdate", "-l"],
            capture_output=True, text=True, timeout=30
        )
        output = result.stdout + result.stderr

        if "No new software available" in output:
            return {
                "Status": "UP TO DATE",
                "Pending updates": [],
            }

        updates = []
        for line in output.splitlines():
            line = line.strip()
            if line.startswith("*") or line.startswith("-"):
                updates.append(line.lstrip("*- ").strip())

        return {
            "Status": "UPDATES AVAILABLE" if updates else "UP TO DATE",
            "Pending updates": updates,
        }
    except Exception as e:
        return {"Status": "error", "Detail": str(e)}


def check_linux():
    try:
        # Try apt (Debian/Ubuntu)
        result = subprocess.run(
            ["apt", "list", "--upgradable"],
            capture_output=True, text=True, timeout=30
        )
        lines = [l for l in result.stdout.splitlines()
                 if "/" in l and "upgradable" not in l]
        return {
            "Status": "UPDATES AVAILABLE" if lines else "UP TO DATE",
            "Pending updates": lines[:20],  # cap at 20
            "Total": len(lines),
        }
    except:
        pass

    try:
        # Try dnf (Fedora/RHEL)
        result = subprocess.run(
            ["dnf", "check-update"],
            capture_output=True, text=True, timeout=30
        )
        lines = [l for l in result.stdout.splitlines() if l.strip()]
        return {
            "Status": "UPDATES AVAILABLE" if lines else "UP TO DATE",
            "Pending updates": lines[:20],
        }
    except:
        return {"Status": "unavailable"}


def check_windows():
    try:
        result = subprocess.run(
            ["powershell", "-Command",
             "Get-WindowsUpdate | Select-Object Title | ConvertTo-Json"],
            capture_output=True, text=True, timeout=60
        )
        if result.stdout.strip():
            import json
            updates = json.loads(result.stdout)
            if isinstance(updates, dict):
                updates = [updates]
            titles = [u.get("Title", "unknown") for u in updates]
            return {
                "Status": "UPDATES AVAILABLE",
                "Pending updates": titles,
            }
        return {"Status": "UP TO DATE", "Pending updates": []}
    except:
        return {"Status": "unavailable — PSWindowsUpdate module may be required"}