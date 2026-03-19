# 🔐 Network Security Toolkit

A collection of lightweight Python tools for network reconnaissance, intrusion monitoring, and system diagnostics.

---

## Projects

### 1. Port Scanner

Scans a range of TCP ports on a target host, identifies open ports, and maps them to their registered service names. Results can be exported to a text file.

```bash
python3 port_scanner.py <host> <start_port> <end_port> [output_file]

# Examples
python3 port_scanner.py localhost 1 1024
python3 port_scanner.py 192.168.1.1 1 65535 results.txt
```

---

### 2. Honeypot

Opens one or more ports and listens for incoming connections, logging the source IP, timestamp, port, and any data sent by the client. Resolves the geographic location of each connecting IP via the ip-api.com free API.

```bash
python3 honeypot.py <port1> [port2] [port3] ...

# Examples
python3 honeypot.py 2222
python3 honeypot.py 2222 8080 8443
```

All events are saved to `honeypot.log`.

---

### 3. System Diagnostic Tool

Runs a full system health check and displays a colour-coded dashboard in the terminal. Detects the operating system and runs the appropriate checks for macOS, Linux, and Windows.

```bash
python3 diagnostic.py
```

Checks performed:

- **System** — OS, version, hostname, architecture, uptime
- **CPU & Memory** — usage, core count, frequency, RAM and swap pressure
- **Disk** — used, free, and total space per partition (APFS-aware on macOS)
- **Network** — active interfaces, local IP, internet connectivity
- **Open Ports** — scans common ports on localhost
- **Processes** — flags processes exceeding CPU or memory thresholds
- **Updates** — pending system updates (softwareupdate / apt / dnf / PowerShell)
- **Firewall** — firewall and stealth mode status

Output is colour-coded: ✔ green for healthy, ⚠ yellow for warnings, ✘ red for critical findings. A full JSON report is saved automatically on each run.


## Requirements

- Python 3.6+
- `psutil` — required for the diagnostic tool only

```bash
pip3 install psutil
```

All other functionality uses the Python standard library only.

---

## Legal Notice

These tools are intended for use on systems you own or have explicit permission to test. Scanning or probing systems without authorisation is illegal in most jurisdictions.

---

*Built as part of a cybersecurity study project covering network fundamentals, socket programming, and intrusion detection concepts.*
