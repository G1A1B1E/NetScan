# NetScan GUI

A modern, cross-platform desktop application for network scanning and device discovery.

## Features

- Network Scanning - Discover all devices on your network
- Dashboard - Visual overview of your network status
- Topology View - Network map visualization
- Security Audit - Check for vulnerabilities
- Real-time Monitoring - Watch for new devices
- MAC Lookup - Identify device manufacturers
- Wake-on-LAN - Wake sleeping devices
- Dark/Light Themes - Beautiful UI in any mode

## Downloads

| Platform | Download |
|----------|----------|
| macOS (Intel) | [NetScan-3.0.0.dmg](https://github.com/G1A1B1E/NetScan/releases/download/v3.0.0/NetScan-3.0.0.dmg) |
| macOS (Apple Silicon) | [NetScan-3.0.0-arm64.dmg](https://github.com/G1A1B1E/NetScan/releases/download/v3.0.0/NetScan-3.0.0-arm64.dmg) |
| Windows | [NetScan-3.0.0-Setup.exe](https://github.com/G1A1B1E/NetScan/releases/download/v3.0.0/NetScan-3.0.0-Setup.exe) |
| Windows (Portable) | [NetScan-3.0.0-Windows.zip](https://github.com/G1A1B1E/NetScan/releases/download/v3.0.0/NetScan-3.0.0-Windows.zip) |

## Build from Source

### Prerequisites

- Node.js 18+
- npm 9+
- Python 3.6+ (for backend features)

### Development

```bash
# Clone the repository
git clone https://github.com/G1A1B1E/NetScan.git
cd NetScan/netscan-gui

# Install dependencies
npm install

# Run in development mode
npm start

# Run with DevTools open
npm run dev
```

### Build Installers

```bash
# Build for current platform
npm run build

# Build for macOS
npm run build:mac

# Build for Windows
npm run build:win

# Build for Linux
npm run build:linux
```

Built installers will be in the `dist/` directory.

## Project Structure

```
netscan-gui/
├── main.js              # Electron main process
├── preload.js           # IPC bridge (security)
├── package.json         # Project configuration
├── assets/              # Application icons
│   ├── icon.svg         # Source icon
│   ├── icon.icns        # macOS icon
│   └── icon.ico         # Windows icon
└── src/
    ├── index.html       # Main application UI
    ├── styles/
    │   ├── main.css     # Core styles and themes
    │   └── components.css
    └── scripts/
        ├── app.js       # Application controller
        ├── views.js     # View templates
        └── renderer.js  # Renderer initialization
```

## Usage

### Quick Start

1. Launch NetScan
2. The dashboard shows your network overview
3. Click "Quick Scan" to discover devices
4. View detailed device information in the Devices tab

### Navigation

| Tab | Description |
|-----|-------------|
| Dashboard | Network overview and quick actions |
| Devices | List of discovered devices |
| Topology | Network map visualization |
| Security | Security audit and findings |
| Monitor | Real-time device monitoring |
| MAC Lookup | Manual MAC address lookup |
| Wake-on-LAN | Wake sleeping devices |
| Settings | Application preferences |

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Cmd/Ctrl+R | Refresh |
| Cmd/Ctrl+E | Export |
| Cmd/Ctrl+, | Settings |
| Cmd/Ctrl+Q | Quit |

### Theme Switching

Click the theme toggle in the top-right corner or go to Settings to switch between dark and light themes.

## Configuration

Settings are stored in:
- macOS: `~/Library/Application Support/NetScan/`
- Windows: `%APPDATA%/NetScan/`
- Linux: `~/.config/NetScan/`

## Troubleshooting

### Scanning requires elevated privileges

Some scan types (ARP scan, ping sweep) may require administrator/root privileges. Run NetScan with elevated permissions for full functionality.

### Python modules not found

Ensure Python 3.6+ is installed and the NetScan helper modules are in your PATH. The GUI will fall back to basic functionality if Python is unavailable.

### Build errors on Windows

Install Visual Studio Build Tools and ensure Python is in your PATH.

## License

MIT License - see [LICENSE](../LICENSE) for details.
