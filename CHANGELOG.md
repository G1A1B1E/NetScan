# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-01-06

### Added
- **Device Fingerprinting** (`fingerprint.py`)
  - Device type classification (router, phone, laptop, IoT, printer, etc.)
  - OS detection via TTL and port signatures
  - Service identification with confidence scoring
  - MAC vendor + open ports + TTL analysis
  - Batch fingerprinting from scan results

- **Wake-on-LAN** (`wol.py`)
  - Magic packet generation and sending
  - Favorites list for quick device waking
  - Multiple MAC format support (colons, dashes, plain)
  - Broadcast and directed wake modes
  - Wake multiple devices at once

- **Export Module** (`export.py`)
  - CSV export (spreadsheet compatible)
  - Styled HTML reports with charts
  - JSON structured data export
  - PDF generation (via wkhtmltopdf)
  - Bulk export to all formats

- **Scheduled Scanning** (`scheduler.py`)
  - Cron integration (Linux)
  - launchd integration (macOS)
  - Predefined schedules (hourly, daily, weekly, monthly)
  - Custom cron expressions
  - Email notifications on changes
  - Automatic report generation

- **Network Topology** (`topology.py`)
  - ASCII art network visualization
  - Interactive HTML with vis.js
  - DOT/Graphviz export
  - Gateway and subnet detection
  - Device type grouping

- **Security Audit** (`security.py`)
  - Open port risk assessment
  - Service vulnerability checks
  - SSL certificate validation
  - HTTP security header analysis
  - Risk scoring (critical/high/medium/low)
  - HTML security reports
  - Actionable recommendations

- **Desktop Notifications** in monitor.py
  - macOS notification center support
  - Linux libnotify support
  - Windows toast notifications
  - Configurable alert triggers

### Changed
- Enhanced scanner.sh menu with v1.1 features
- Added 6 new menu options (f, z, j, y, s, x)
- Improved shell function organization

## [2.0.0] - 2026-01-06

### Added
- **Async Network Scanner** (`async_scanner.py`)
  - High-performance concurrent network discovery
  - CIDR expansion (e.g., /24, /16 networks)
  - Parallel ping sweeps (100+ hosts simultaneously)
  - Port scanning with service detection
  - Automatic vendor lookup with caching
  - JSON output for easy parsing

- **Real-time Network Monitor** (`monitor.py`)
  - Continuous device tracking with SQLite database
  - New device detection and alerts
  - Baseline creation and diff comparison
  - Webhook notifications (Slack, Discord, etc.)
  - Known device list to suppress alerts
  - Device history tracking

- **Report Generator** (`report_generator.py`)
  - PDF report generation (requires reportlab)
  - HTML report export with embedded CSS
  - Vendor distribution charts (requires matplotlib)
  - Scan comparison/diff reports
  - Markdown export option
  - Network summary statistics

- **Configuration Manager** (`config_manager.py`)
  - User preferences management
  - Custom OUI definitions
  - Known device database
  - Exclude lists (MACs/IPs)
  - Network profiles
  - Configuration import/export

- **Web Interface** (`web_server.py`)
  - Browser-based dashboard
  - REST API endpoints
  - Real-time device listing
  - Scan triggering from browser
  - JSON API for integration

- Additional Python helpers
  - `mac_normalizer.py` - MAC address format conversion
  - `network_helper.py` - IP/CIDR operations
  - `export_helper.py` - Multi-format data export

### Changed
- Updated `scanner.sh` with new menu options for advanced features
- Extended menu with Python-powered scan options
- Improved installation script with optional dependency checks
- Updated documentation with new features

### Fixed
- Scanner menu double-press issue resolved

## [1.0.0] - 2026-01-06

### Added
- Initial release of modular NetScan
- Multi-format file support (nmap XML, ARP table, CSV, JSON, plain text)
- Automatic format detection
- MAC vendor lookup via macvendors.com API
- Python helpers for performance optimization
  - `vendor_cache.py` - SQLite-backed vendor caching (30-day expiry)
  - `fast_parser.py` - High-performance file parsing
- Modular architecture with separate library files
  - `lib/config.sh` - Configuration and globals
  - `lib/errors.sh` - Error handling and validation
  - `lib/logging.sh` - Session logging
  - `lib/ui.sh` - User interface components
  - `lib/parsers.sh` - File format parsers
  - `lib/vendor.sh` - Vendor lookup functions
  - `lib/loader.sh` - File loading
  - `lib/search.sh` - Search functionality
  - `lib/export.sh` - Export functions
- Installation script with dependency checking
- Session logging to `logs/` directory
- Export capabilities (CSV, JSON)
- System capabilities display
- Graceful degradation when optional dependencies missing

### Security
- Input validation for file paths and MAC addresses
- Safe curl operations with timeout and retry
- Trap handlers for clean exit on interrupt

## [0.1.0] - 2026-01-01

### Added
- Initial monolithic script (`mac_vendor_lookup.sh`)
- Basic MAC vendor lookup
- nmap XML parsing
- ARP table parsing
