#!/usr/bin/env python3
"""
Web Server - Simple local web UI and REST API for NetScan
Provides a browser-based interface for viewing network data
"""

import sys
import os
import json
import argparse
import threading
import webbrowser
import mimetypes
from datetime import datetime
from typing import Dict, List, Optional, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import socket
import html

# Import our modules
try:
    from async_scanner import AsyncScanner
    from monitor import NetworkMonitor, DeviceDatabase
    from config_manager import ConfigManager
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from async_scanner import AsyncScanner
    from monitor import NetworkMonitor, DeviceDatabase
    from config_manager import ConfigManager


# Embedded HTML template for the web UI
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NetScan - Network Scanner</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a2e;
            color: #eee;
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(135deg, #16213e 0%, #1a1a2e 100%);
            padding: 20px;
            border-bottom: 1px solid #4a90d9;
        }
        .header h1 {
            color: #4a90d9;
            font-size: 24px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .header h1::before { content: "🔍"; }
        .nav {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        .nav button {
            background: #4a90d9;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.2s;
        }
        .nav button:hover { background: #357abd; }
        .nav button.active { background: #50c878; }
        .nav button:disabled { background: #444; cursor: not-allowed; }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: #16213e;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            border: 1px solid #333;
        }
        .stat-value {
            font-size: 36px;
            font-weight: bold;
            color: #4a90d9;
        }
        .stat-label {
            color: #888;
            margin-top: 5px;
            font-size: 14px;
        }
        .card {
            background: #16213e;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #333;
        }
        .card h2 {
            color: #4a90d9;
            margin-bottom: 15px;
            font-size: 18px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #333;
        }
        th {
            background: #0f3460;
            color: #4a90d9;
            font-weight: 600;
            position: sticky;
            top: 0;
        }
        tr:hover { background: #1f4068; }
        .mac, .ip { font-family: 'Monaco', 'Menlo', monospace; font-size: 13px; }
        .status-up { color: #50c878; }
        .status-down { color: #e94560; }
        .status-new { 
            background: #50c878; 
            color: #1a1a2e;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 12px;
        }
        .status-unknown {
            background: #e94560;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 12px;
        }
        .search-box {
            width: 100%;
            padding: 12px;
            background: #0f3460;
            border: 1px solid #333;
            border-radius: 5px;
            color: #eee;
            font-size: 14px;
            margin-bottom: 15px;
        }
        .search-box:focus {
            outline: none;
            border-color: #4a90d9;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #888;
        }
        .spinner {
            border: 4px solid #333;
            border-top: 4px solid #4a90d9;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .alert {
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 15px;
        }
        .alert-info { background: #0f3460; border-left: 4px solid #4a90d9; }
        .alert-success { background: #1a4d2e; border-left: 4px solid #50c878; }
        .alert-warning { background: #4d3a1a; border-left: 4px solid #f0a500; }
        .alert-error { background: #4d1a1a; border-left: 4px solid #e94560; }
        .actions button {
            background: transparent;
            border: 1px solid #4a90d9;
            color: #4a90d9;
            padding: 5px 10px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
            margin-right: 5px;
        }
        .actions button:hover {
            background: #4a90d9;
            color: white;
        }
        .vendor-chart {
            height: 300px;
            display: flex;
            align-items: flex-end;
            gap: 10px;
            padding: 20px 0;
        }
        .chart-bar {
            flex: 1;
            background: linear-gradient(180deg, #4a90d9 0%, #357abd 100%);
            border-radius: 5px 5px 0 0;
            min-width: 40px;
            position: relative;
            transition: height 0.3s;
        }
        .chart-bar:hover {
            background: linear-gradient(180deg, #50c878 0%, #3da861 100%);
        }
        .chart-label {
            text-align: center;
            font-size: 11px;
            color: #888;
            margin-top: 5px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 100%;
        }
        .chart-value {
            position: absolute;
            top: -25px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 12px;
            color: #eee;
        }
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 12px;
        }
        .hidden { display: none; }
        #scan-target {
            padding: 10px;
            background: #0f3460;
            border: 1px solid #333;
            border-radius: 5px;
            color: #eee;
            width: 200px;
            margin-right: 10px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>NetScan</h1>
        <div class="nav">
            <button onclick="showTab('devices')" id="tab-devices" class="active">Devices</button>
            <button onclick="showTab('monitor')" id="tab-monitor">Monitor</button>
            <button onclick="showTab('stats')" id="tab-stats">Statistics</button>
            <span style="flex: 1;"></span>
            <input type="text" id="scan-target" placeholder="192.168.1.0/24" value="192.168.1.0/24">
            <button onclick="startScan()" id="scan-btn">🔍 Scan Network</button>
            <button onclick="refreshData()">🔄 Refresh</button>
        </div>
    </div>

    <div class="container">
        <!-- Devices Tab -->
        <div id="devices-tab">
            <div class="stats-grid" id="stats-cards">
                <div class="stat-card">
                    <div class="stat-value" id="total-devices">-</div>
                    <div class="stat-label">Total Devices</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="known-devices">-</div>
                    <div class="stat-label">Known</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="unknown-devices">-</div>
                    <div class="stat-label">Unknown</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="last-scan">-</div>
                    <div class="stat-label">Last Scan</div>
                </div>
            </div>

            <div class="card">
                <h2>Network Devices</h2>
                <input type="text" class="search-box" placeholder="Search devices..." 
                       onkeyup="filterDevices(this.value)" id="search-input">
                <div id="devices-table">
                    <div class="loading">
                        <div class="spinner"></div>
                        <p>Loading devices...</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Monitor Tab -->
        <div id="monitor-tab" class="hidden">
            <div class="card">
                <h2>Real-time Monitor</h2>
                <div class="alert alert-info">
                    Monitor is watching for new devices on the network.
                </div>
                <div id="monitor-events">
                    <p style="color: #888; text-align: center; padding: 20px;">
                        No events yet. Start monitoring to see device changes.
                    </p>
                </div>
            </div>
        </div>

        <!-- Stats Tab -->
        <div id="stats-tab" class="hidden">
            <div class="card">
                <h2>Vendor Distribution</h2>
                <div class="vendor-chart" id="vendor-chart">
                    <div class="loading">Loading chart...</div>
                </div>
            </div>
            <div class="card">
                <h2>Database Statistics</h2>
                <div id="db-stats">Loading...</div>
            </div>
        </div>
    </div>

    <div class="footer">
        NetScan Web Interface | <span id="connection-status">Connected</span>
    </div>

    <script>
        let devices = [];
        let lastScanTime = null;
        
        function showTab(tab) {
            document.querySelectorAll('.container > div').forEach(el => el.classList.add('hidden'));
            document.querySelectorAll('.nav button').forEach(btn => btn.classList.remove('active'));
            document.getElementById(tab + '-tab').classList.remove('hidden');
            document.getElementById('tab-' + tab).classList.add('active');
            
            if (tab === 'stats') loadStats();
        }
        
        async function refreshData() {
            try {
                const response = await fetch('/api/devices');
                const data = await response.json();
                devices = data.devices || [];
                updateDevicesTable();
                updateStats(data);
                lastScanTime = new Date();
                document.getElementById('last-scan').textContent = 'Just now';
            } catch (err) {
                console.error('Error fetching devices:', err);
            }
        }
        
        async function startScan() {
            const btn = document.getElementById('scan-btn');
            const target = document.getElementById('scan-target').value;
            btn.disabled = true;
            btn.textContent = '⏳ Scanning...';
            
            try {
                const response = await fetch('/api/scan?target=' + encodeURIComponent(target));
                const data = await response.json();
                devices = data.devices || [];
                updateDevicesTable();
                updateStats(data);
                lastScanTime = new Date();
                document.getElementById('last-scan').textContent = 'Just now';
            } catch (err) {
                console.error('Error scanning:', err);
            } finally {
                btn.disabled = false;
                btn.textContent = '🔍 Scan Network';
            }
        }
        
        function updateDevicesTable() {
            const container = document.getElementById('devices-table');
            
            if (devices.length === 0) {
                container.innerHTML = '<p style="color: #888; text-align: center; padding: 20px;">No devices found. Click "Scan Network" to discover devices.</p>';
                return;
            }
            
            let html = '<table><thead><tr>' +
                '<th>IP Address</th><th>MAC Address</th><th>Hostname</th>' +
                '<th>Vendor</th><th>Status</th><th>Actions</th></tr></thead><tbody>';
            
            for (const device of devices) {
                const isKnown = device.is_known ? '' : '<span class="status-unknown">Unknown</span>';
                html += '<tr>' +
                    '<td class="ip">' + escapeHtml(device.ip || '') + '</td>' +
                    '<td class="mac">' + escapeHtml(device.mac || '') + '</td>' +
                    '<td>' + escapeHtml(device.hostname || device.known_name || '') + '</td>' +
                    '<td>' + escapeHtml(device.vendor || '') + '</td>' +
                    '<td>' + isKnown + '</td>' +
                    '<td class="actions">' +
                        '<button onclick="markKnown(\\''+device.mac+'\\')">✓ Known</button>' +
                        '<button onclick="excludeDevice(\\''+device.mac+'\\')">✗ Exclude</button>' +
                    '</td></tr>';
            }
            
            html += '</tbody></table>';
            container.innerHTML = html;
        }
        
        function updateStats(data) {
            document.getElementById('total-devices').textContent = devices.length;
            const known = devices.filter(d => d.is_known).length;
            document.getElementById('known-devices').textContent = known;
            document.getElementById('unknown-devices').textContent = devices.length - known;
        }
        
        function filterDevices(query) {
            query = query.toLowerCase();
            const rows = document.querySelectorAll('#devices-table tbody tr');
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            });
        }
        
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                
                // Vendor chart
                const vendors = stats.vendors || {};
                const chartContainer = document.getElementById('vendor-chart');
                const maxCount = Math.max(...Object.values(vendors), 1);
                
                let chartHtml = '';
                const items = Object.entries(vendors).slice(0, 10);
                for (const [vendor, count] of items) {
                    const height = (count / maxCount) * 250;
                    chartHtml += '<div style="flex: 1; display: flex; flex-direction: column; align-items: center;">' +
                        '<div class="chart-bar" style="height: ' + height + 'px;">' +
                        '<span class="chart-value">' + count + '</span></div>' +
                        '<div class="chart-label" title="' + escapeHtml(vendor) + '">' + 
                        escapeHtml(vendor.slice(0, 15)) + '</div></div>';
                }
                chartContainer.innerHTML = chartHtml || '<p style="color: #888;">No vendor data</p>';
                
                // DB stats
                document.getElementById('db-stats').innerHTML = 
                    '<p>Total devices in database: <strong>' + (stats.total_devices || 0) + '</strong></p>' +
                    '<p>Known devices: <strong>' + (stats.known_devices || 0) + '</strong></p>' +
                    '<p>Active (24h): <strong>' + (stats.active_24h || 0) + '</strong></p>';
                    
            } catch (err) {
                console.error('Error loading stats:', err);
            }
        }
        
        async function markKnown(mac) {
            const name = prompt('Enter device name:', '');
            if (name) {
                try {
                    await fetch('/api/known?mac=' + encodeURIComponent(mac) + '&name=' + encodeURIComponent(name), {method: 'POST'});
                    refreshData();
                } catch (err) {
                    console.error('Error:', err);
                }
            }
        }
        
        async function excludeDevice(mac) {
            if (confirm('Exclude this device from scans?')) {
                try {
                    await fetch('/api/exclude?mac=' + encodeURIComponent(mac), {method: 'POST'});
                    refreshData();
                } catch (err) {
                    console.error('Error:', err);
                }
            }
        }
        
        function escapeHtml(str) {
            const div = document.createElement('div');
            div.textContent = str;
            return div.innerHTML;
        }
        
        // Update last scan time display
        setInterval(() => {
            if (lastScanTime) {
                const seconds = Math.floor((new Date() - lastScanTime) / 1000);
                if (seconds < 60) {
                    document.getElementById('last-scan').textContent = seconds + 's ago';
                } else {
                    document.getElementById('last-scan').textContent = Math.floor(seconds / 60) + 'm ago';
                }
            }
        }, 1000);
        
        // Initial load
        refreshData();
    </script>
</body>
</html>'''


class NetScanAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for NetScan API"""
    
    scanner: Optional[AsyncScanner] = None
    monitor: Optional[NetworkMonitor] = None
    config: Optional[ConfigManager] = None
    devices: List[Dict] = []
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass
    
    def send_json(self, data: Any, status: int = 200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())
    
    def send_html(self, content: str):
        """Send HTML response"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(content.encode())
    
    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        
        # Serve main page
        if path == '/' or path == '/index.html':
            self.send_html(HTML_TEMPLATE)
            return
        
        # API endpoints
        if path == '/api/devices':
            self.handle_get_devices()
        elif path == '/api/scan':
            target = params.get('target', [''])[0]
            self.handle_scan(target)
        elif path == '/api/stats':
            self.handle_get_stats()
        elif path == '/api/device':
            mac = params.get('mac', [''])[0]
            self.handle_get_device(mac)
        elif path == '/api/history':
            mac = params.get('mac', [''])[0]
            self.handle_get_history(mac)
        else:
            self.send_json({'error': 'Not found'}, 404)
    
    def do_POST(self):
        """Handle POST requests"""
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        
        if path == '/api/known':
            mac = params.get('mac', [''])[0]
            name = params.get('name', [''])[0]
            self.handle_mark_known(mac, name)
        elif path == '/api/exclude':
            mac = params.get('mac', [''])[0]
            self.handle_exclude(mac)
        else:
            self.send_json({'error': 'Not found'}, 404)
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def handle_get_devices(self):
        """Return current devices"""
        # Enrich devices with config data
        devices = NetScanAPIHandler.devices
        if NetScanAPIHandler.config:
            devices = NetScanAPIHandler.config.enrich_devices(devices)
            devices = NetScanAPIHandler.config.filter_devices(devices)
        
        self.send_json({
            'devices': devices,
            'count': len(devices),
            'timestamp': datetime.now().isoformat()
        })
    
    def handle_scan(self, target: str):
        """Perform network scan"""
        import asyncio
        
        if not NetScanAPIHandler.scanner:
            NetScanAPIHandler.scanner = AsyncScanner(verbose=False)
        
        scanner = NetScanAPIHandler.scanner
        
        # Run async scan
        async def do_scan():
            if target:
                return await scanner.quick_scan(target)
            else:
                return scanner.get_arp_table()
        
        try:
            devices = asyncio.run(do_scan())
            NetScanAPIHandler.devices = [d.to_dict() for d in devices]
            
            # Enrich and filter
            if NetScanAPIHandler.config:
                NetScanAPIHandler.devices = NetScanAPIHandler.config.enrich_devices(
                    NetScanAPIHandler.devices
                )
                NetScanAPIHandler.devices = NetScanAPIHandler.config.filter_devices(
                    NetScanAPIHandler.devices
                )
            
            self.send_json({
                'devices': NetScanAPIHandler.devices,
                'count': len(NetScanAPIHandler.devices),
                'target': target,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def handle_get_stats(self):
        """Get statistics"""
        # Calculate vendor distribution
        vendors = {}
        known_count = 0
        
        for device in NetScanAPIHandler.devices:
            vendor = device.get('vendor', 'Unknown') or 'Unknown'
            vendors[vendor] = vendors.get(vendor, 0) + 1
            if device.get('is_known'):
                known_count += 1
        
        # Sort vendors by count
        vendors = dict(sorted(vendors.items(), key=lambda x: x[1], reverse=True))
        
        stats = {
            'total_devices': len(NetScanAPIHandler.devices),
            'known_devices': known_count,
            'unknown_devices': len(NetScanAPIHandler.devices) - known_count,
            'vendors': vendors,
            'active_24h': len(NetScanAPIHandler.devices)
        }
        
        # Add DB stats if monitor is available
        if NetScanAPIHandler.monitor:
            db_stats = NetScanAPIHandler.monitor.db.get_stats()
            stats.update(db_stats)
        
        self.send_json(stats)
    
    def handle_get_device(self, mac: str):
        """Get single device details"""
        for device in NetScanAPIHandler.devices:
            if device.get('mac', '').lower() == mac.lower():
                self.send_json(device)
                return
        self.send_json({'error': 'Device not found'}, 404)
    
    def handle_get_history(self, mac: str):
        """Get device history"""
        if NetScanAPIHandler.monitor:
            history = NetScanAPIHandler.monitor.db.get_device_history(mac)
            self.send_json({'mac': mac, 'history': history})
        else:
            self.send_json({'mac': mac, 'history': []})
    
    def handle_mark_known(self, mac: str, name: str):
        """Mark device as known"""
        if NetScanAPIHandler.config and mac:
            NetScanAPIHandler.config.add_known_device(mac, name or 'Unknown')
            self.send_json({'success': True, 'mac': mac, 'name': name})
        else:
            self.send_json({'error': 'Invalid request'}, 400)
    
    def handle_exclude(self, mac: str):
        """Exclude device"""
        if NetScanAPIHandler.config and mac:
            NetScanAPIHandler.config.exclude_mac(mac)
            self.send_json({'success': True, 'mac': mac})
        else:
            self.send_json({'error': 'Invalid request'}, 400)


def run_server(host: str = '127.0.0.1', port: int = 8080, 
               open_browser: bool = True, verbose: bool = False):
    """Run the web server"""
    # Initialize components
    NetScanAPIHandler.scanner = AsyncScanner(verbose=verbose)
    NetScanAPIHandler.config = ConfigManager()
    
    # Try to find an available port
    original_port = port
    while port < original_port + 100:
        try:
            server = HTTPServer((host, port), NetScanAPIHandler)
            break
        except socket.error:
            port += 1
    else:
        print(f"Error: Could not find available port", file=sys.stderr)
        return 1
    
    url = f"http://{host}:{port}"
    print(f"\n🌐 NetScan Web Server")
    print(f"   URL: {url}")
    print(f"   Press Ctrl+C to stop\n")
    
    if open_browser:
        # Open browser in background thread
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        server.shutdown()
    
    return 0


# =============================================================================
# CLI Interface
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='NetScan Web Server - Browser-based network scanning',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Start server on localhost:8080
  %(prog)s -p 3000                  # Use port 3000
  %(prog)s --host 0.0.0.0           # Listen on all interfaces
  %(prog)s --no-browser             # Don't open browser automatically
        """
    )
    
    parser.add_argument('--host', '-H', default='127.0.0.1',
                        help='Host to bind to (default: 127.0.0.1)')
    parser.add_argument('--port', '-p', type=int, default=8080,
                        help='Port to listen on (default: 8080)')
    parser.add_argument('--no-browser', action='store_true',
                        help="Don't open browser automatically")
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    
    args = parser.parse_args()
    
    return run_server(
        host=args.host,
        port=args.port,
        open_browser=not args.no_browser,
        verbose=args.verbose
    )


if __name__ == '__main__':
    sys.exit(main())
