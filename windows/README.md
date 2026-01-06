# NetScan for Windows

A network scanning and MAC address lookup tool for Windows systems.

## Quick Start

### Prerequisites

- Windows 10/11
- PowerShell 5.1+ (included with Windows)
- Python 3.6+ ([Download](https://www.python.org/downloads/))
- Optional: [nmap](https://nmap.org/download.html) for advanced scanning

### Installation

1. **Run the installer** (recommended):

   ```powershell
   # Open PowerShell as Administrator
   .\install.ps1
   ```

   Or for user-only installation:

   ```powershell
   .\install.ps1
   ```

2. **Manual Installation**:

   ```powershell
   # Copy files to installation directory
   mkdir "$env:LOCALAPPDATA\NetScan"
   Copy-Item -Recurse * "$env:LOCALAPPDATA\NetScan"
   
   # Add to PATH
   $path = [Environment]::GetEnvironmentVariable("Path", "User")
   [Environment]::SetEnvironmentVariable("Path", "$path;$env:LOCALAPPDATA\NetScan", "User")
   ```

## Usage

### Command Line

```powershell
# MAC Address Lookup
netscan -Lookup 00:11:22:33:44:55
netscan -Lookup 00-11-22-33-44-55

# Network Scanning
netscan -Scan                           # Auto-detect local network
netscan -Scan -Target 192.168.1.0/24    # Scan specific range

# Port Scanning
netscan -Ports 192.168.1.1              # Common ports
netscan -Ports 192.168.1.1 -PortList "22,80,443,3389"

# Output Options
netscan -Scan -Json                     # JSON output
netscan -Scan -Output results.txt       # Save to file

# Interactive Menu
netscan -Menu

# Help
netscan -Help
```

### Interactive Menu

Run `netscan -Menu` to access the interactive interface:

```
  [1] MAC Lookup        - Look up vendor by MAC address
  [2] Network Scan      - Discover devices on network
  [3] Port Scan         - Scan ports on a target
  [4] ARP Table         - View local ARP cache
  [5] Network Info      - Show network interfaces
  [6] Web Interface     - Start web dashboard
  [7] Settings          - Configuration options
  [q] Quit
```

### Python Helpers

You can also use the Python modules directly:

```python
# MAC Lookup
python helpers\mac_lookup.py 00:11:22:33:44:55
python helpers\mac_lookup.py --batch MAC1 MAC2 MAC3
python helpers\mac_lookup.py --stats

# Network Scanner
python helpers\scanner.py --scan
python helpers\scanner.py --scan 192.168.1.0/24
python helpers\scanner.py --arp
python helpers\scanner.py --info
python helpers\scanner.py --ports 192.168.1.1
```

## File Structure

```
windows/
├── netscan.ps1         # Main PowerShell script
├── netscan.bat         # Batch launcher
├── install.ps1         # Windows installer
├── README.md           # This file
├── helpers/
│   ├── __init__.py     # Package init
│   ├── mac_lookup.py   # MAC vendor lookup
│   ├── oui_parser.py   # OUI database parser
│   ├── scanner.py      # Network scanner
│   └── menu.py         # Interactive menu
└── data/
    └── oui.txt         # OUI database (downloaded on install)
```

## Features

### MAC Address Lookup

- Local OUI database lookup (offline)
- Web API fallback (online)
- Support for multiple MAC formats:
  - `00:11:22:33:44:55`
  - `00-11-22-33-44-55`
  - `001122334455`
  - `0011.2233.4455`

### Network Scanning

- Auto-detect local network
- Custom IP range scanning
- ARP table parsing
- Hostname resolution
- nmap integration (when available)

### Port Scanning

- Common port presets
- Custom port ranges
- Service identification
- Native Windows scanning
- nmap integration (when available)

## Configuration

Configuration is stored in `config.json`:

```json
{
  "version": "1.0.0",
  "oui_path": "C:\\Users\\...\\NetScan\\data\\oui.txt",
  "cache_dir": "C:\\Users\\...\\NetScan\\cache",
  "log_dir": "C:\\Users\\...\\NetScan\\logs",
  "web_port": 5555,
  "scan_timeout": 30,
  "nmap_available": true
}
```

## Troubleshooting

### PowerShell Execution Policy

If you get an execution policy error:

```powershell
# Option 1: Run with bypass
powershell -ExecutionPolicy Bypass -File netscan.ps1

# Option 2: Change policy for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Python Not Found

1. Download from [python.org](https://www.python.org/downloads/)
2. **Important**: Check "Add Python to PATH" during installation
3. Restart terminal/PowerShell

### Permission Errors

Some scanning features require Administrator privileges:

```powershell
# Right-click PowerShell > "Run as Administrator"
# Then run netscan
```

### nmap Not Working

1. Download from [nmap.org](https://nmap.org/download.html)
2. Install with "Add to PATH" option
3. Restart terminal

## Uninstallation

```powershell
# Remove NetScan
.\install.ps1 -Uninstall

# Or manually
Remove-Item -Recurse "$env:LOCALAPPDATA\NetScan"
```

## Differences from Unix Version

| Feature | Unix | Windows |
|---------|------|---------|
| Entry Point | `netscan.sh` | `netscan.ps1` |
| Shell | Bash | PowerShell |
| ARP Command | `arp -a` | `arp -a` (different format) |
| Network Info | `ifconfig`/`ip` | `ipconfig` |
| Admin Rights | `sudo` | Run as Administrator |
| Package Manager | apt/brew | Manual/chocolatey |

## License

MIT License - See main project for details.

## Links

- [Main Repository](https://github.com/G1A1B1E/NetScan)
- [Documentation](https://github.com/G1A1B1E/NetScan/tree/main/docs)
- [Report Issues](https://github.com/G1A1B1E/NetScan/issues)
