# NetScan GUI

A modern, cross-platform desktop application for network scanning and device discovery.

![NetScan GUI](assets/screenshot.png)

## Features

- 🔍 **Network Scanning** - Discover all devices on your network
- 📊 **Dashboard** - Visual overview of your network status
- 🗺️ **Topology View** - Network map visualization
- 🔒 **Security Audit** - Check for vulnerabilities
- 👁️ **Real-time Monitoring** - Watch for new devices
- 🔎 **MAC Lookup** - Identify device manufacturers
- ⚡ **Wake-on-LAN** - Wake sleeping devices
- 🌙 **Dark/Light Themes** - Beautiful UI in any mode

## Installation

### Pre-built Installers

Download the latest release for your platform:
- **macOS**: `NetScan-x.x.x.dmg`
- **Windows**: `NetScan-Setup-x.x.x.exe`

### Build from Source

```bash
# Clone the repository
git clone https://github.com/G1A1B1E/NetScan.git
cd NetScan/netscan-gui

# Install dependencies
npm install

# Run in development mode
npm start

# Build for production
npm run dist
```

## Requirements

### Runtime
- Node.js 18+ (for development)
- Python 3.6+ with required modules

### Development
- npm 9+
- electron-builder (included in devDependencies)

## Project Structure

```
netscan-gui/
├── main.js              # Electron main process
├── preload.js           # IPC bridge (security)
├── package.json         # Project configuration
├── assets/              # Application icons
│   ├── icon.svg
│   ├── icon.icns        # macOS
│   └── icon.ico         # Windows
└── src/
    ├── index.html       # Main application UI
    ├── styles/
    │   ├── main.css     # Core styles & themes
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

### Security Audit

1. Navigate to the Security tab
2. Click "Run Security Audit"
3. Review findings and recommendations

### Wake-on-LAN

1. Go to the WoL tab
2. Enter the MAC address of the device
3. Click "Wake Device"

## Development

### Running in Development

```bash
npm start
```

### Building Installers

```bash
# Build for current platform
npm run dist

# Build for all platforms
npm run dist:all

# Platform-specific builds
npm run dist:mac
npm run dist:win
```

### Debugging

Press `Cmd/Ctrl + Shift + I` to open DevTools.

## Configuration

Settings are stored in:
- **macOS**: `~/Library/Application Support/NetScan/settings.json`
- **Windows**: `%APPDATA%/NetScan/settings.json`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see [LICENSE](../LICENSE) for details.

## Credits

Built with:
- [Electron](https://www.electronjs.org/)
- [Node.js](https://nodejs.org/)
- Python network tools

## Support

- GitHub Issues: [Report a bug](https://github.com/G1A1B1E/NetScan/issues)
- Documentation: [Full docs](https://g1a1b1e.github.io/NetScan/)
