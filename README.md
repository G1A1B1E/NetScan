# NetScan 🔍

> Network Device Finder & MAC Vendor Lookup Tool

A powerful, interactive CLI tool for network device discovery and MAC address vendor identification. Supports multiple input formats with fast parsing and intelligent caching.

![Bash](https://img.shields.io/badge/Bash-4.0%2B-green)
![Python](https://img.shields.io/badge/Python-3.6%2B-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Features

- 📂 **Multi-format Support** - Load nmap XML, ARP tables, CSV, JSON, or plain text
- 🔎 **Smart Search** - Search by hostname, IP, MAC address, or vendor
- 🏭 **Vendor Lookup** - Automatic MAC-to-vendor resolution via macvendors.com API
- 📡 **Network Scanning** - Built-in scanning with nmap, arp-scan, ping sweep
- ⚡ **Async Scanning** - Python-powered concurrent network discovery
- �️ **Real-time Monitoring** - Watch for new devices, alerts on unknown MACs
- 📊 **Report Generation** - PDF/HTML reports with vendor charts
- 🌐 **Web Interface** - Browser-based dashboard and REST API
- 💾 **Export Options** - Export results to CSV, JSON, HTML, or Markdown
- 🗄️ **Intelligent Caching** - SQLite-backed vendor cache (30-day expiry)
- ⚙️ **Configuration** - Custom OUI definitions, exclude lists, network profiles
- 📝 **Session Logging** - All actions logged for auditing

## Installation

### Quick Install

```bash
git clone https://github.com/yourusername/netscan.git
cd netscan
./install.sh
```

### Install Options

```bash
./install.sh              # Install to /usr/local/bin (may need sudo)
./install.sh --local      # Install to ~/.local/bin
./install.sh --check      # Check dependencies only
./install.sh --uninstall  # Remove installation
```

### Dependencies

**Required:**
- Bash 4.0+
- curl

**Optional (recommended):**
- Python 3.6+ (enables caching, fast parsing, advanced features)
- jq (enhanced JSON parsing)
- nmap (network scanning)
- reportlab & matplotlib (PDF reports and charts)

```bash
# Install optional Python packages for reports/charts
pip3 install reportlab matplotlib
```

## Usage

### Interactive Mode

```bash
netscan
```

### Load File on Startup

```bash
netscan path/to/file.xml
```

### Menu Options

| Option | Description |
|--------|-------------|
| 1 | Load a single file |
| 2 | Load multiple files |
| 3 | List all loaded devices |
| 4 | Search devices by any field |
| 5 | Search by vendor name |
| 6 | Find IP by hostname |
| 7 | Find IP by MAC address |
| 8 | Show network summary |
| 9 | Export to CSV |
| s | **Network scanning** (12+ scan types) |
| e | Load example files |
| r | Refresh vendor data |
| c | Show system capabilities |
| 0 | Exit |

### Scanning Menu

| Option | Description |
|--------|-------------|
| 1 | ARP cache (instant) |
| 2 | Ping sweep (ICMP) |
| p | **Python async scan** (fast, concurrent) |
| 3-9 | Nmap scans (discovery, ports, services, OS, vuln) |
| m | MAC discovery (nmap) |
| a | ARP-scan (layer 2) |
| w | **Real-time monitor** (watch for new devices) |
| t | **Generate report** (PDF/HTML) |
| g | **Configuration** (preferences, custom OUIs) |
| b | **Web interface** (browser dashboard) |

## Supported Input Formats

### Nmap XML
```bash
nmap -sn 192.168.1.0/24 -oX scan.xml
```

### ARP Table
```bash
arp -a > arp.txt
```

### CSV
```csv
mac,ip,hostname
AA:BB:CC:DD:EE:FF,192.168.1.100,device1
```

### JSON
```json
[
  {"mac": "AA:BB:CC:DD:EE:FF", "ip": "192.168.1.100", "hostname": "device1"}
]
```

### Plain Text
```
AA:BB:CC:DD:EE:FF
BB-CC-DD-EE-FF-00
```

## Project Structure

```
netscan/
├── netscan              # Main entry point
├── install.sh           # Installation script
├── README.md            # This file
├── LICENSE              # MIT License
├── CHANGELOG.md         # Version history
├── package.json         # Package metadata
│
├── lib/                 # Bash modules
│   ├── config.sh        # Colors, globals, directories
│   ├── errors.sh        # Error handling & validation
│   ├── logging.sh       # Session logging
│   ├── ui.sh            # Banner, menus, display helpers
│   ├── parsers.sh       # Format detection & parsing
│   ├── vendor.sh        # MAC vendor lookup
│   ├── loader.sh        # File loading functions
│   ├── search.sh        # Search & display functions
│   ├── export.sh        # CSV/JSON export
│   └── scanner.sh       # Network scanning (outline)
│
├── helpers/             # Python acceleration
│   ├── vendor_cache.py  # SQLite vendor caching
│   ├── fast_parser.py   # High-performance parsing
│   ├── mac_normalizer.py # MAC address formatting
│   ├── network_helper.py # IP/CIDR operations
│   ├── export_helper.py # Multi-format export
│   ├── async_scanner.py # Concurrent network scanning
│   ├── monitor.py       # Real-time device monitoring
│   ├── report_generator.py # PDF/HTML reports
│   ├── config_manager.py # Configuration management
│   └── web_server.py    # Web interface & REST API
│
├── docs/                # Documentation
│   ├── ARCHITECTURE.md  # Technical architecture
│   ├── CONTRIBUTING.md  # Contribution guidelines
│   └── SCANNING.md      # Scanning commands reference
│
├── example/             # Sample input files
│   ├── arp.txt          # Sample ARP output
│   ├── scan.xml         # Sample nmap XML
│   ├── devices.csv      # Sample CSV
│   ├── network.json     # Sample JSON
│   └── macs.txt         # Sample plain text MACs
│
├── files/               # Runtime data (gitignored)
│   ├── exports/         # Exported CSV/JSON files
│   ├── logs/            # Session logs
│   └── output/          # Scan output files
│
└── cache/               # Vendor cache (gitignored)
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NETSCAN_LOG_DIR` | Log directory | `./files/logs` |
| `NETSCAN_EXPORT_DIR` | Export directory | `./files/exports` |
| `NETSCAN_OUTPUT_DIR` | Scan output directory | `./files/output` |
| `NETSCAN_CACHE_DIR` | Cache directory | `./cache` |

### Cache Management

```bash
# View cache stats
python3 helpers/vendor_cache.py --stats

# Clean expired entries
python3 helpers/vendor_cache.py --cleanup
```

## Examples

### Scan and Analyze Local Network

```bash
# 1. Scan your network with nmap
sudo nmap -sn 192.168.1.0/24 -oX ~/network_scan.xml

# 2. Load and analyze
netscan ~/network_scan.xml
```

### Quick ARP Analysis

```bash
# Capture and load ARP table
arp -a > /tmp/arp.txt && netscan /tmp/arp.txt
```

### Batch Processing

```bash
# Load multiple files at once using menu option 2
netscan
# Then select option 2 and enter: scan1.xml scan2.xml arp.txt
```

## API Rate Limiting

The macvendors.com API is rate-limited. NetScan includes:
- 0.5s delay between API requests
- 30-day local cache for vendor lookups

## Advanced Features

### Python Async Scanner

High-performance concurrent network scanning:

```bash
# Quick scan
python3 helpers/async_scanner.py 192.168.1.0/24

# Full discovery with services
python3 helpers/async_scanner.py 192.168.1.0/24 --full

# Just read ARP table
python3 helpers/async_scanner.py --arp
```

### Real-time Network Monitoring

Watch your network for changes and new devices:

```bash
# Start monitoring (Ctrl+C to stop)
python3 helpers/monitor.py

# List known devices
python3 helpers/monitor.py --list

# Show unknown devices
python3 helpers/monitor.py --unknown

# Mark device as known
python3 helpers/monitor.py --mark-known AA:BB:CC:DD:EE:FF
```

### Report Generation

Create PDF/HTML reports with charts:

```bash
# Generate HTML report
python3 helpers/report_generator.py scan.json --html > report.html

# Generate PDF report (requires reportlab)
python3 helpers/report_generator.py scan.json --pdf report.pdf

# Compare two scans
python3 helpers/report_generator.py new.json --compare old.json --html > diff.html
```

### Web Interface

Browser-based dashboard and REST API:

```bash
# Start web server
python3 helpers/web_server.py

# Access at http://localhost:8080

# API endpoints:
# GET /api/devices - List devices
# GET /api/scan    - Trigger scan
# GET /api/vendors - Vendor info
```

### Configuration Management

Customize NetScan behavior:

```bash
# Show current config
python3 helpers/config_manager.py --show

# Add custom OUI mapping
python3 helpers/config_manager.py --add-oui AABBCC "My Company"

# Add known device
python3 helpers/config_manager.py --add-device AA:BB:CC:DD:EE:FF "My Router"

# Exclude device from scans
python3 helpers/config_manager.py --exclude-mac AA:BB:CC:DD:EE:FF
```

## Network Scanning

NetScan includes comprehensive network scanning capabilities. Scan outputs are saved to `files/output/`.

### Scan Types

| Scan | Command | Root | Description |
|------|---------|------|-------------|
| ARP Cache | `arp -a` | No | Show devices from ARP cache |
| Ping Sweep | `ping` | No | ICMP host discovery |
| **Async Scan** | Python | No | Fast concurrent discovery |
| Host Discovery | `nmap -sn` | No | Find live hosts |
| Quick Scan | `nmap -F` | No | Top 100 ports |
| Full Scan | `nmap -p-` | No | All 65535 ports |
| Service Detection | `nmap -sV` | No | Identify services |
| OS Detection | `nmap -O` | Yes | Identify OS |
| ARP-Scan | `arp-scan` | Yes | Layer 2 MAC discovery |

### Quick Commands (Manual)

```bash
# ARP cache
arp -a > files/output/arp.txt

# Nmap host discovery with MACs
sudo nmap -sn 192.168.1.0/24 -oX files/output/scan.xml

# ARP-scan (install: brew install arp-scan)
sudo arp-scan --localnet > files/output/arpscan.txt
```

See [docs/SCANNING.md](docs/SCANNING.md) for full command reference.
- Batch lookup support for efficiency

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [macvendors.com](https://macvendors.com) for the MAC vendor lookup API
- The nmap project for network scanning capabilities
