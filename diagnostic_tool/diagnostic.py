import json
import platform
from datetime import datetime

from checks import system, cpu_memory, disk, network, ports, processes, updates, firewall


# ── ANSI colours ─────────────────────────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def ok(text):      return f"{GREEN}✔ {text}{RESET}"
def warn(text):    return f"{YELLOW}⚠ {text}{RESET}"
def danger(text):  return f"{RED}✘ {text}{RESET}"
def header(text):  return f"{BOLD}{CYAN}{text}{RESET}"
def label(text):   return f"{BOLD}{text}{RESET}"


# ── Formatters ───────────────────────────────────────────────
def fmt_system(data):
    print(f"  {label('OS:')}           {data['OS']} {data['OS Release']}")
    print(f"  {label('Hostname:')}     {data['Hostname']}")
    print(f"  {label('Architecture:')} {data['Architecture']}")
    print(f"  {label('Uptime:')}       {data['Uptime']}")
    print(f"  {label('Python:')}       {data['Python']}")


def fmt_cpu_memory(data):
    cpu = data['CPU']
    mem = data['Memory']
    swp = data['Swap']

    cpu_pct = float(cpu['Usage'].strip('%'))
    mem_pct = float(mem['Usage'].strip('%'))
    swp_pct = float(swp['Usage'].strip('%'))

    cpu_str = f"CPU: {cpu['Usage']} ({cpu['Cores']} cores, {cpu['Frequency']})"
    print(f"  {ok(cpu_str) if cpu_pct < 70 else warn(cpu_str) if cpu_pct < 90 else danger(cpu_str)}")

    mem_str = f"RAM: {mem['Used']} / {mem['Total']} ({mem['Usage']})"
    print(f"  {ok(mem_str) if mem_pct < 70 else warn(mem_str) if mem_pct < 90 else danger(mem_str)}")

    swp_str = f"Swap: {swp['Used']} / {swp['Total']} ({swp['Usage']})"
    print(f"  {ok(swp_str) if swp_pct < 50 else warn(swp_str) if swp_pct < 80 else danger(swp_str)}")


def fmt_disk(data):
    for mount, info in data.items():
        pct = float(info['Usage'].strip('%'))
        line = f"{mount}: {info['Used']} / {info['Total']} ({info['Usage']})"
        print(f"  {ok(line) if pct < 75 else warn(line) if pct < 90 else danger(line)}")


def fmt_network(data):
    for name, iface in data['Interfaces'].items():
        status = iface['Status']
        line = f"{name}: {iface['IP']} ({status})"
        print(f"  {ok(line) if status == 'UP' else danger(line)}")

    internet = data['Internet']
    print(f"  {ok('Internet: ' + internet) if internet == 'CONNECTED' else danger('Internet: ' + internet)}")


def fmt_ports(data):
    open_ports = data['Open']
    if not open_ports:
        print(f"  {ok('No common ports open')}")
    else:
        for port, service in open_ports.items():
            print(f"  {warn(f'Port {port} open ({service})')}")


def fmt_processes(data):
    high_cpu = data['High CPU']
    high_mem = data['High Memory']

    if high_cpu == ["none"]:
        print(f"  {ok('No high CPU processes')}")
    else:
        for p in high_cpu:
            msg = f"High CPU: {p['Name']} (PID {p['PID']}) — {p['CPU']}"
            print(f"  {danger(msg)}")

    if high_mem == ["none"]:
        print(f"  {ok('No high memory processes')}")
    else:
        for p in high_mem:
            msg = f"High Memory: {p['Name']} (PID {p['PID']}) — {p['Memory']}"
            print(f"  {danger(msg)}")
def fmt_updates(data):
    status = data['Status']
    if status == "UP TO DATE":
        print(f"  {ok('System is up to date')}")
    else:
        updates = data.get('Pending updates', [])
        print(f"  {warn(f'{len(updates)} update(s) available:')}")
        for u in updates:
            print(f"    {YELLOW}→ {u}{RESET}")


def fmt_firewall(data):
    status = data['Status']
    stealth = data.get('Stealth mode', 'unavailable')

    fw_line = f"Firewall: {status}"
    print(f"  {ok(fw_line) if status == 'ENABLED' else danger(fw_line)}")

    st_line = f"Stealth mode: {stealth}"
    print(f"  {ok(st_line) if stealth == 'ENABLED' else warn(st_line)}")


# ── Main ─────────────────────────────────────────────────────
def run():
    print("\n" + "=" * 60)
    print(header("  SYSTEM DIAGNOSTIC TOOL"))
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    checks = [
        ("System",       system.check,    fmt_system),
        ("CPU & Memory", cpu_memory.check, fmt_cpu_memory),
        ("Disk",         disk.check,      fmt_disk),
        ("Network",      network.check,   fmt_network),
        ("Open Ports",   ports.check,     fmt_ports),
        ("Processes",    processes.check, fmt_processes),
        ("Updates",      updates.check,   fmt_updates),
        ("Firewall",     firewall.check,  fmt_firewall),
    ]

    results = {}

    for name, fn, fmt in checks:
        print(f"\n{header('── ' + name + ' ' + '─' * (54 - len(name)))}")
        try:
            data = fn()
            results[name] = data
            fmt(data)
        except Exception as e:
            print(f"  {danger(f'Error: {str(e)}')}")
            results[name] = {"error": str(e)}

    # Save report
    report_file = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"  {ok(f'Report saved to {report_file}')}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run()