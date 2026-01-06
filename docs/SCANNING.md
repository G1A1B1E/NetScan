# Network Scanning Commands Reference

This document outlines the scanning commands that NetScan supports.

## Quick Reference

| Scan Type | Command | Root Required | Output Format |
|-----------|---------|---------------|---------------|
| ARP Cache | `arp -a` | No | Text |
| Ping Sweep | `ping -c 1` | No | Text |
| Python Async Scan | `async_scanner.py` | No | JSON |
| Host Discovery | `nmap -sn` | No | XML |
| Quick Port Scan | `nmap -F` | No | XML |
| Full Port Scan | `nmap -p-` | No | XML |
| Service Detection | `nmap -sV` | No | XML |
| OS Detection | `nmap -O` | Yes | XML |
| ARP-Scan | `arp-scan --localnet` | Yes | Text |
| MAC Scan | `nmap -sn --send-eth` | Yes | XML |
| Real-time Monitor | `monitor.py` | No | SQLite |
| Report Generator | `report_generator.py` | No | PDF/HTML |

---

## Python-Powered Advanced Features

NetScan includes Python helpers for advanced network operations. These provide better performance and additional features.

### Async Network Scanner (`async_scanner.py`)

High-performance concurrent network scanning using Python's asyncio.

```bash
# Quick network discovery (ping + ARP)
python3 helpers/async_scanner.py --scan 192.168.1.0/24

# Full discovery (ping + ARP + ports + vendor lookup)
python3 helpers/async_scanner.py --discover 192.168.1.0/24

# Ping sweep only
python3 helpers/async_scanner.py --ping-sweep 192.168.1.0/24

# Port scan (common ports)
python3 helpers/async_scanner.py --port-scan 192.168.1.1

# With JSON output
python3 helpers/async_scanner.py --scan 192.168.1.0/24 --output scan.json
```

**Features:**
- CIDR expansion (e.g., /24, /16)
- Concurrent ping sweeps (100+ hosts at once)
- Automatic vendor lookup with caching
- Port scanning with service detection
- JSON output for easy parsing

### Real-time Network Monitor (`monitor.py`)

Watch your network for changes, new devices, and alerts.

```bash
# Start continuous monitoring
python3 helpers/monitor.py --watch --interval 60

# Create a baseline snapshot
python3 helpers/monitor.py --baseline

# Compare current network to baseline
python3 helpers/monitor.py --diff

# View device history
python3 helpers/monitor.py --history

# Configure alerts
python3 helpers/monitor.py --alerts
```

**Features:**
- Device tracking database (SQLite)
- New device detection and alerts
- Diff detection vs baseline
- Webhook notifications (Slack, Discord, etc.)
- Known device list (suppress false alarms)

### Report Generator (`report_generator.py`)

Create professional reports with charts and analysis.

```bash
# Generate PDF report
python3 helpers/report_generator.py --pdf scan.json --output report.pdf

# Generate HTML report
python3 helpers/report_generator.py --html scan.json --output report.html

# Generate vendor distribution chart
python3 helpers/report_generator.py --chart vendor scan.json

# Network summary
python3 helpers/report_generator.py --summary scan.json

# Compare two scans
python3 helpers/report_generator.py --compare scan1.json scan2.json
```

**Optional dependencies:**
```bash
pip install reportlab matplotlib  # For PDF and charts
```

### Configuration Manager (`config_manager.py`)

Manage preferences, custom OUI definitions, and network profiles.

```bash
# Initialize configuration
python3 helpers/config_manager.py --init

# View preferences
python3 helpers/config_manager.py --list preferences

# Set a preference
python3 helpers/config_manager.py --set "scan.timeout" "5"

# Add custom OUI mapping
python3 helpers/config_manager.py --add-oui "AA:BB:CC" "My Custom Vendor"

# Add known device
python3 helpers/config_manager.py --add-device "AA:BB:CC:DD:EE:FF" "My Phone"

# Exclude MAC from scans
python3 helpers/config_manager.py --exclude "AA:BB:CC:DD:EE:FF"

# Manage network profiles
python3 helpers/config_manager.py --profile create "home"
python3 helpers/config_manager.py --profile load "home"
```

### Web Interface (`web_server.py`)

Browser-based dashboard and REST API.

```bash
# Start web server
python3 helpers/web_server.py --port 8080

# Access at: http://localhost:8080
```

**API Endpoints:**
- `GET /api/devices` - List discovered devices
- `GET /api/scan` - Trigger network scan
- `GET /api/vendors` - Get vendor information
- `GET /api/status` - System status

---

## ARP Commands

### arp -a (ARP Cache)
Display the system's ARP cache - devices that have been communicated with recently.

```bash
# Basic usage
arp -a

# Output format:
# hostname (192.168.1.1) at aa:bb:cc:dd:ee:ff on en0 ifscope [ethernet]
```

**Pros:** Instant, no network traffic
**Cons:** Only shows recently contacted devices

### arp-scan (Layer 2 Discovery)
Send ARP requests to discover all devices on local network.

```bash
# Install
brew install arp-scan

# Scan local network
sudo arp-scan --localnet

# Scan specific interface
sudo arp-scan --interface=en0 --localnet

# Scan specific range
sudo arp-scan 192.168.1.0/24

# Output format:
# 192.168.1.1    aa:bb:cc:dd:ee:ff    Vendor Name
```

**Pros:** Fast, reliable MAC discovery
**Cons:** Requires root, local network only

---

## Ping Commands

### Ping Sweep
Discover live hosts by sending ICMP echo requests.

```bash
# Single host
ping -c 1 192.168.1.1

# Sweep with bash loop
for i in {1..254}; do
    ping -c 1 -W 1 192.168.1.$i &
done | grep "bytes from"

# Using fping (faster)
brew install fping
fping -a -g 192.168.1.0/24 2>/dev/null
```

**Pros:** Simple, widely supported
**Cons:** Many devices block ICMP

---

## Nmap Commands

### Installation
```bash
brew install nmap
```

### Host Discovery (-sn)
Find live hosts without port scanning.

```bash
# Discover hosts on subnet
nmap -sn 192.168.1.0/24

# With XML output
nmap -sn 192.168.1.0/24 -oX scan.xml

# With MAC addresses (requires root on local network)
sudo nmap -sn 192.168.1.0/24
```

### Quick Port Scan (-F)
Scan top 100 most common ports.

```bash
# Quick scan
nmap -F 192.168.1.0/24

# With service versions
nmap -F -sV 192.168.1.0/24

# With XML output
nmap -F 192.168.1.0/24 -oX quick_scan.xml
```

### Full Port Scan (-p-)
Scan all 65535 ports.

```bash
# Full port scan (slow)
nmap -p- 192.168.1.1

# With timing optimization
nmap -p- -T4 192.168.1.1

# Specific port ranges
nmap -p 1-1000 192.168.1.1
nmap -p 22,80,443,8080 192.168.1.1
```

### Service Version Detection (-sV)
Identify running services and versions.

```bash
# Service detection
nmap -sV 192.168.1.1

# With intensity level (0-9)
nmap -sV --version-intensity 5 192.168.1.1

# Light version scan
nmap -sV --version-light 192.168.1.1
```

### OS Detection (-O)
Attempt to identify operating system.

```bash
# OS detection (requires root)
sudo nmap -O 192.168.1.1

# With version detection
sudo nmap -O -sV 192.168.1.1

# Aggressive OS detection
sudo nmap -O --osscan-guess 192.168.1.1
```

### MAC Address Scanning
Get MAC addresses from local network.

```bash
# ARP ping scan (local network, requires root)
sudo nmap -sn -PR 192.168.1.0/24

# Send raw ethernet frames
sudo nmap -sn --send-eth 192.168.1.0/24

# Include MAC vendor info
sudo nmap -sn 192.168.1.0/24 --script broadcast-arp
```

### Useful Nmap Options

| Option | Description |
|--------|-------------|
| `-oX file.xml` | XML output |
| `-oN file.txt` | Normal text output |
| `-oG file.gnmap` | Grepable output |
| `-oA basename` | All formats |
| `-T0` to `-T5` | Timing (0=paranoid, 5=insane) |
| `-v` | Verbose |
| `-A` | Aggressive (OS, version, scripts, traceroute) |
| `--open` | Only show open ports |
| `-Pn` | Skip host discovery |
| `--reason` | Show why port is open/closed |

---

## Network Information Commands

### Interface Information
```bash
# macOS
ifconfig
ifconfig en0

# Get IP address
ipconfig getifaddr en0

# Get subnet mask
ipconfig getoption en0 subnet_mask
```

### Gateway and Routing
```bash
# Default gateway
netstat -nr | grep default
route -n get default | grep gateway

# Routing table
netstat -nr
```

### DNS Information
```bash
# DNS servers
scutil --dns | grep nameserver

# Resolve hostname
nslookup hostname
dig hostname
host hostname
```

### Network Connections
```bash
# Active connections
netstat -an | grep ESTABLISHED

# Listening ports
netstat -an | grep LISTEN
lsof -i -P | grep LISTEN
```

---

## Output File Naming Convention

NetScan will save scan outputs with timestamped filenames:

```
files/output/
├── arp_20260106_143052.txt
├── arpscan_20260106_143105.txt
├── nmap_discovery_20260106_143200.xml
├── nmap_quick_20260106_143245.xml
├── nmap_services_20260106_143512.xml
└── ping_sweep_20260106_142930.txt
```

Format: `{scan_type}_{YYYYMMDD}_{HHMMSS}.{ext}`

---

## Scan Profiles (Future)

### Stealth Scan
```bash
nmap -sS -T2 -f --data-length 24 target
```

### Comprehensive Scan
```bash
nmap -sS -sV -O -A -p- target
```

### Quick Network Inventory
```bash
nmap -sn -oX inventory.xml 192.168.1.0/24
```

---

## Security Considerations

⚠️ **Important:** Only scan networks you own or have explicit permission to scan.

- Unauthorized scanning may be illegal
- Some scans (especially aggressive ones) may trigger security alerts
- OS detection and service probing can be intrusive
- Always get written permission before scanning corporate networks
