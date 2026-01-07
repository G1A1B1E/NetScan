# NetScan# NetScan 🔍



> Network Intelligence Suite - CLI and Desktop GUI for Network Discovery> Network Device Finder & MAC Vendor Lookup Tool



A powerful network device discovery and MAC address vendor identification tool. Available as both an interactive CLI and a modern desktop GUI application.A powerful, interactive CLI tool for network device discovery and MAC address vendor identification. Supports multiple input formats with fast parsing and intelligent caching.



![Version](https://img.shields.io/badge/Version-3.0.0-blue)![Bash](https://img.shields.io/badge/Bash-4.0%2B-green)

![Bash](https://img.shields.io/badge/Bash-3.2%2B-green)![Python](https://img.shields.io/badge/Python-3.6%2B-blue)

![Python](https://img.shields.io/badge/Python-3.6%2B-blue)![License](https://img.shields.io/badge/License-MIT-yellow)

![Electron](https://img.shields.io/badge/Electron-28-9feaf9)

![License](https://img.shields.io/badge/License-MIT-yellow)## Features



## Downloads- 📂 **Multi-format Support** - Load nmap XML, ARP tables, CSV, JSON, or plain text

- 🔎 **Smart Search** - Search by hostname, IP, MAC address, or vendor

### Desktop GUI Application- 🏭 **Vendor Lookup** - Automatic MAC-to-vendor resolution via macvendors.com API

- 📡 **Network Scanning** - Built-in scanning with nmap, arp-scan, ping sweep

| Platform | Download | Description |- ⚡ **Async Scanning** - Python-powered concurrent network discovery

|----------|----------|-------------|- �️ **Real-time Monitoring** - Watch for new devices, alerts on unknown MACs

| macOS (Intel) | [NetScan-3.0.0.dmg](https://github.com/G1A1B1E/NetScan/releases/download/v3.0.0/NetScan-3.0.0.dmg) | Drag-and-drop installer |- 📊 **Report Generation** - PDF/HTML reports with vendor charts

| macOS (Apple Silicon) | [NetScan-3.0.0-arm64.dmg](https://github.com/G1A1B1E/NetScan/releases/download/v3.0.0/NetScan-3.0.0-arm64.dmg) | For M1/M2/M3 Macs |- 🌐 **Web Interface** - Browser-based dashboard and REST API

| macOS (Full Installer) | [NetScan-3.0.0-Installer.pkg](https://github.com/G1A1B1E/NetScan/releases/download/v3.0.0/NetScan-3.0.0-Installer.pkg) | GUI + CLI with options |- 💾 **Export Options** - Export results to CSV, JSON, HTML, or Markdown

| Windows | [NetScan-3.0.0-Setup.exe](https://github.com/G1A1B1E/NetScan/releases/download/v3.0.0/NetScan-3.0.0-Setup.exe) | Windows installer |- 🗄️ **Intelligent Caching** - SQLite-backed vendor cache (30-day expiry)

| Windows (Portable) | [NetScan-3.0.0-Windows.zip](https://github.com/G1A1B1E/NetScan/releases/download/v3.0.0/NetScan-3.0.0-Windows.zip) | No installation required |- ⚙️ **Configuration** - Custom OUI definitions, exclude lists, network profiles

- 📝 **Session Logging** - All actions logged for auditing

### CLI Only

## Installation

| Platform | Download |

|----------|----------|### Quick Install

| macOS | [NetScan-CLI-3.0.0.pkg](https://github.com/G1A1B1E/NetScan/releases/download/v3.0.0/NetScan-CLI-3.0.0.pkg) |

| Any (script) | `curl -fsSL https://raw.githubusercontent.com/G1A1B1E/NetScan/main/install.sh \| bash` |```bash

git clone https://github.com/yourusername/netscan.git

## Featurescd netscan

./install.sh

### Desktop GUI```

- Modern interface with dark/light themes

- Real-time network scanning with live updates### Install Options

- Device management with favorites and custom labels

- Network topology visualization```bash

- Security dashboard with risk assessment./install.sh              # Install to /usr/local/bin (may need sudo)

- Export to CSV, HTML, JSON, PDF formats./install.sh --local      # Install to ~/.local/bin

./install.sh --check      # Check dependencies only

### CLI Tool./install.sh --uninstall  # Remove installation

- Multi-format support - Load nmap XML, ARP tables, CSV, JSON, or plain text```

- Smart search - Search by hostname, IP, MAC address, or vendor

- Vendor lookup - Automatic MAC-to-vendor resolution### Dependencies

- Network scanning - Built-in scanning with nmap, arp-scan, ping sweep

- Async scanning - Python-powered concurrent network discovery**Required:**

- Real-time monitoring - Watch for new devices- Bash 4.0+

- Report generation - PDF/HTML reports with vendor charts- curl

- Web interface - Browser-based dashboard and REST API

- Export options - Export results to CSV, JSON, HTML, or Markdown**Optional (recommended):**

- Intelligent caching - SQLite-backed vendor cache (30-day expiry)- Python 3.6+ (enables caching, fast parsing, advanced features)

- jq (enhanced JSON parsing)

## Quick Start- nmap (network scanning)

- reportlab & matplotlib (PDF reports and charts)

### GUI Application

```bash

1. Download the installer for your platform from the [Releases](https://github.com/G1A1B1E/NetScan/releases) page# Install optional Python packages for reports/charts

2. Install and launch NetScanpip3 install reportlab matplotlib

3. Click "Quick Scan" to discover devices on your network```



### CLI Installation## Usage



```bash### Interactive Mode

# One-line install

curl -fsSL https://raw.githubusercontent.com/G1A1B1E/NetScan/main/install.sh | bash```bash

netscan

# Or clone and install```

git clone https://github.com/G1A1B1E/NetScan.git

cd NetScan### Load File on Startup

./install.sh

``````bash

netscan path/to/file.xml

### CLI Usage```



```bash### Menu Options

# Interactive mode

netscan| Option | Description |

|--------|-------------|

# Load a file on startup| 1 | Load a single file |

netscan path/to/scan.xml| 2 | Load multiple files |

```| 3 | List all loaded devices |

| 4 | Search devices by any field |

## CLI Menu Options| 5 | Search by vendor name |

| 6 | Find IP by hostname |

| Option | Description || 7 | Find IP by MAC address |

|--------|-------------|| 8 | Show network summary |

| 1 | Load a single file || 9 | Export to CSV |

| 2 | Load multiple files || s | **Network scanning** (12+ scan types) |

| 3 | List all loaded devices || e | Load example files |

| 4 | Search devices by any field || r | Refresh vendor data |

| 5 | Search by vendor name || c | Show system capabilities |

| 6 | Find IP by hostname || 0 | Exit |

| 7 | Find IP by MAC address |

| 8 | Show network summary |### Scanning Menu

| 9 | Export to CSV |

| s | Network scanning (12+ scan types) || Option | Description |

| e | Load example files ||--------|-------------|

| r | Refresh vendor data || 1 | ARP cache (instant) |

| c | Show system capabilities || 2 | Ping sweep (ICMP) |

| 0 | Exit || p | **Python async scan** (fast, concurrent) |

| 3-9 | Nmap scans (discovery, ports, services, OS, vuln) |

## Supported Input Formats| m | MAC discovery (nmap) |

| a | ARP-scan (layer 2) |

### Nmap XML| w | **Real-time monitor** (watch for new devices) |

```bash| t | **Generate report** (PDF/HTML) |

nmap -sn 192.168.1.0/24 -oX scan.xml| g | **Configuration** (preferences, custom OUIs) |

```| b | **Web interface** (browser dashboard) |



### ARP Table## Supported Input Formats

```bash

arp -a > arp.txt### Nmap XML

``````bash

nmap -sn 192.168.1.0/24 -oX scan.xml

### CSV```

```csv

mac,ip,hostname### ARP Table

AA:BB:CC:DD:EE:FF,192.168.1.100,device1```bash

```arp -a > arp.txt

```

### JSON

```json### CSV

[```csv

  {"mac": "AA:BB:CC:DD:EE:FF", "ip": "192.168.1.100", "hostname": "device1"}mac,ip,hostname

]AA:BB:CC:DD:EE:FF,192.168.1.100,device1

``````



### Plain Text (MAC addresses)### JSON

``````json

AA:BB:CC:DD:EE:FF[

BB-CC-DD-EE-FF-00  {"mac": "AA:BB:CC:DD:EE:FF", "ip": "192.168.1.100", "hostname": "device1"}

```]

```

## Project Structure

### Plain Text

``````

NetScan/AA:BB:CC:DD:EE:FF

├── netscan              # Main CLI entry pointBB-CC-DD-EE-FF-00

├── install.sh           # CLI installation script```

├── lib/                 # Bash modules

├── helpers/             # Python acceleration modules## Project Structure

├── netscan-gui/         # Electron desktop application

├── installer/           # Installer build scripts```

├── docs/                # Documentationnetscan/

│   └── website/         # GitHub Pages documentation├── netscan              # Main entry point

├── example/             # Sample input files├── install.sh           # Installation script

└── cache/               # Vendor cache (gitignored)├── README.md            # This file

```├── LICENSE              # MIT License

├── CHANGELOG.md         # Version history

## Dependencies├── package.json         # Package metadata

│

### Required├── lib/                 # Bash modules

- Bash 3.2+│   ├── config.sh        # Colors, globals, directories

- curl│   ├── errors.sh        # Error handling & validation

│   ├── logging.sh       # Session logging

### Optional (Recommended)│   ├── ui.sh            # Banner, menus, display helpers

- Python 3.6+ (enables caching, fast parsing, advanced features)│   ├── parsers.sh       # Format detection & parsing

- jq (enhanced JSON parsing)│   ├── vendor.sh        # MAC vendor lookup

- nmap (network scanning)│   ├── loader.sh        # File loading functions

│   ├── search.sh        # Search & display functions

### For PDF Reports│   ├── export.sh        # CSV/JSON export

```bash│   └── scanner.sh       # Network scanning (outline)

pip3 install reportlab matplotlib│

```├── helpers/             # Python acceleration

│   ├── vendor_cache.py  # SQLite vendor caching

## Documentation│   ├── fast_parser.py   # High-performance parsing

│   ├── mac_normalizer.py # MAC address formatting

Full documentation is available at: https://g1a1b1e.github.io/NetScan/│   ├── network_helper.py # IP/CIDR operations

│   ├── export_helper.py # Multi-format export

- [Installation Guide](https://g1a1b1e.github.io/NetScan/installation.html)│   ├── async_scanner.py # Concurrent network scanning

- [Quick Start](https://g1a1b1e.github.io/NetScan/quickstart.html)│   ├── monitor.py       # Real-time device monitoring

- [CLI Reference](https://g1a1b1e.github.io/NetScan/cli-reference.html)│   ├── report_generator.py # PDF/HTML reports

- [Network Scanning](https://g1a1b1e.github.io/NetScan/network-scanning.html)│   ├── config_manager.py # Configuration management

- [API Reference](https://g1a1b1e.github.io/NetScan/api.html)│   └── web_server.py    # Web interface & REST API

│

## Docker Support├── docs/                # Documentation

│   ├── ARCHITECTURE.md  # Technical architecture

```bash│   ├── CONTRIBUTING.md  # Contribution guidelines

# Build and run with Docker Compose│   └── SCANNING.md      # Scanning commands reference

docker-compose up -d│

├── example/             # Sample input files

# Or use the helper script│   ├── arp.txt          # Sample ARP output

./docker.sh build│   ├── scan.xml         # Sample nmap XML

./docker.sh start│   ├── devices.csv      # Sample CSV

```│   ├── network.json     # Sample JSON

│   └── macs.txt         # Sample plain text MACs

See [Docker Documentation](docs/DOCKER.md) for more details.│

├── files/               # Runtime data (gitignored)

## Contributing│   ├── exports/         # Exported CSV/JSON files

│   ├── logs/            # Session logs

Contributions are welcome! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.│   └── output/          # Scan output files

│

## License└── cache/               # Vendor cache (gitignored)

```

MIT License - see [LICENSE](LICENSE) for details.

## Configuration

## Changelog

### Environment Variables

See [CHANGELOG.md](CHANGELOG.md) for version history.

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
