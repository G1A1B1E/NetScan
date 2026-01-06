#!/usr/bin/env python3
"""
NetScan Web Server Module
Simple Flask-based web interface for NetScan
"""

import os
import sys
import json
import argparse
from datetime import datetime

# Try to import Flask
try:
    from flask import Flask, render_template_string, jsonify, request
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False
    print("Flask is required for web interface. Install with: pip install flask")

# Import local modules
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from mac_lookup import MACLookup
from scanner import get_arp_table, scan_network, scan_ports, get_network_info


# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NetScan Web Interface</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #1a1a2e; color: #eee; min-height: 100vh; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        header { background: #16213e; padding: 20px; border-radius: 10px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
        h1 { font-size: 1.8em; color: #4ecca3; }
        .nav { display: flex; gap: 15px; }
        .nav a { color: #eee; text-decoration: none; padding: 8px 16px; border-radius: 5px; background: #0f3460; transition: background 0.3s; }
        .nav a:hover, .nav a.active { background: #4ecca3; color: #1a1a2e; }
        .card { background: #16213e; border-radius: 10px; padding: 20px; margin-bottom: 20px; }
        .card h2 { color: #4ecca3; margin-bottom: 15px; font-size: 1.3em; }
        input[type="text"], select { width: 100%; padding: 12px; border: none; border-radius: 5px; background: #0f3460; color: #eee; font-size: 1em; margin-bottom: 10px; }
        button { padding: 12px 24px; border: none; border-radius: 5px; background: #4ecca3; color: #1a1a2e; font-size: 1em; cursor: pointer; font-weight: bold; }
        button:hover { background: #3db892; }
        button:disabled { background: #555; cursor: not-allowed; }
        .result { margin-top: 15px; padding: 15px; background: #0f3460; border-radius: 5px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #0f3460; }
        th { color: #4ecca3; }
        tr:hover { background: #0f3460; }
        .loading { display: none; color: #4ecca3; }
        .error { color: #e74c3c; }
        .success { color: #4ecca3; }
        .flex { display: flex; gap: 10px; }
        .flex input { flex: 1; }
        @media (max-width: 768px) { .flex { flex-direction: column; } }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 NetScan</h1>
            <nav class="nav">
                <a href="#" onclick="showSection('lookup')" class="active" id="nav-lookup">MAC Lookup</a>
                <a href="#" onclick="showSection('scan')" id="nav-scan">Network Scan</a>
                <a href="#" onclick="showSection('arp')" id="nav-arp">ARP Table</a>
                <a href="#" onclick="showSection('ports')" id="nav-ports">Port Scan</a>
            </nav>
        </header>

        <!-- MAC Lookup Section -->
        <section id="section-lookup" class="card">
            <h2>MAC Address Lookup</h2>
            <div class="flex">
                <input type="text" id="mac-input" placeholder="Enter MAC address (e.g., 00:11:22:33:44:55)">
                <button onclick="lookupMAC()">Lookup</button>
            </div>
            <div id="mac-result" class="result" style="display:none;"></div>
        </section>

        <!-- Network Scan Section -->
        <section id="section-scan" class="card" style="display:none;">
            <h2>Network Scanner</h2>
            <div class="flex">
                <input type="text" id="scan-target" placeholder="IP range (e.g., 192.168.1.0/24) or leave empty for auto">
                <button onclick="scanNetwork()">Scan</button>
            </div>
            <p class="loading" id="scan-loading">Scanning network...</p>
            <div id="scan-result" class="result" style="display:none;"></div>
        </section>

        <!-- ARP Table Section -->
        <section id="section-arp" class="card" style="display:none;">
            <h2>ARP Table</h2>
            <button onclick="loadARP()">Refresh</button>
            <div id="arp-result" class="result" style="display:none;"></div>
        </section>

        <!-- Port Scan Section -->
        <section id="section-ports" class="card" style="display:none;">
            <h2>Port Scanner</h2>
            <div class="flex">
                <input type="text" id="port-target" placeholder="Target IP (e.g., 192.168.1.1)">
                <input type="text" id="port-list" placeholder="Ports (e.g., 22,80,443)" value="22,80,443,3389,445">
                <button onclick="scanPorts()">Scan</button>
            </div>
            <p class="loading" id="port-loading">Scanning ports...</p>
            <div id="port-result" class="result" style="display:none;"></div>
        </section>
    </div>

    <script>
        function showSection(name) {
            // Hide all sections
            document.querySelectorAll('[id^="section-"]').forEach(el => el.style.display = 'none');
            document.querySelectorAll('.nav a').forEach(el => el.classList.remove('active'));
            
            // Show selected
            document.getElementById('section-' + name).style.display = 'block';
            document.getElementById('nav-' + name).classList.add('active');
        }

        async function lookupMAC() {
            const mac = document.getElementById('mac-input').value.trim();
            if (!mac) return alert('Please enter a MAC address');
            
            const result = document.getElementById('mac-result');
            result.style.display = 'block';
            result.innerHTML = 'Looking up...';
            
            try {
                const res = await fetch('/api/lookup?mac=' + encodeURIComponent(mac));
                const data = await res.json();
                
                if (data.error) {
                    result.innerHTML = '<span class="error">' + data.error + '</span>';
                } else {
                    result.innerHTML = `
                        <p><strong>MAC:</strong> ${data.normalized}</p>
                        <p><strong>Prefix:</strong> ${data.prefix}</p>
                        <p><strong>Vendor:</strong> <span class="success">${data.vendor}</span></p>
                        <p><strong>Source:</strong> ${data.source}</p>
                    `;
                }
            } catch (e) {
                result.innerHTML = '<span class="error">Error: ' + e.message + '</span>';
            }
        }

        async function scanNetwork() {
            const target = document.getElementById('scan-target').value.trim();
            const result = document.getElementById('scan-result');
            const loading = document.getElementById('scan-loading');
            
            loading.style.display = 'block';
            result.style.display = 'none';
            
            try {
                const url = '/api/scan' + (target ? '?target=' + encodeURIComponent(target) : '');
                const res = await fetch(url);
                const data = await res.json();
                
                loading.style.display = 'none';
                result.style.display = 'block';
                
                if (data.length === 0) {
                    result.innerHTML = '<p>No hosts found</p>';
                } else {
                    result.innerHTML = `
                        <p>Found ${data.length} hosts:</p>
                        <table>
                            <tr><th>IP Address</th><th>MAC Address</th><th>Hostname</th></tr>
                            ${data.map(h => `<tr><td>${h.ip}</td><td>${h.mac || 'N/A'}</td><td>${h.hostname || ''}</td></tr>`).join('')}
                        </table>
                    `;
                }
            } catch (e) {
                loading.style.display = 'none';
                result.style.display = 'block';
                result.innerHTML = '<span class="error">Error: ' + e.message + '</span>';
            }
        }

        async function loadARP() {
            const result = document.getElementById('arp-result');
            result.style.display = 'block';
            result.innerHTML = 'Loading...';
            
            try {
                const res = await fetch('/api/arp');
                const data = await res.json();
                
                if (data.length === 0) {
                    result.innerHTML = '<p>ARP table is empty</p>';
                } else {
                    result.innerHTML = `
                        <p>${data.length} entries:</p>
                        <table>
                            <tr><th>IP Address</th><th>MAC Address</th><th>Type</th></tr>
                            ${data.map(e => `<tr><td>${e.ip}</td><td>${e.mac}</td><td>${e.type}</td></tr>`).join('')}
                        </table>
                    `;
                }
            } catch (e) {
                result.innerHTML = '<span class="error">Error: ' + e.message + '</span>';
            }
        }

        async function scanPorts() {
            const target = document.getElementById('port-target').value.trim();
            const ports = document.getElementById('port-list').value.trim();
            
            if (!target) return alert('Please enter a target IP');
            
            const result = document.getElementById('port-result');
            const loading = document.getElementById('port-loading');
            
            loading.style.display = 'block';
            result.style.display = 'none';
            
            try {
                const res = await fetch(`/api/ports?target=${encodeURIComponent(target)}&ports=${encodeURIComponent(ports)}`);
                const data = await res.json();
                
                loading.style.display = 'none';
                result.style.display = 'block';
                
                if (data.length === 0) {
                    result.innerHTML = '<p>No open ports found</p>';
                } else {
                    result.innerHTML = `
                        <p>Found ${data.length} open ports:</p>
                        <table>
                            <tr><th>Port</th><th>State</th><th>Service</th></tr>
                            ${data.map(p => `<tr><td>${p.port}</td><td>${p.state}</td><td>${p.service}</td></tr>`).join('')}
                        </table>
                    `;
                }
            } catch (e) {
                loading.style.display = 'none';
                result.style.display = 'block';
                result.innerHTML = '<span class="error">Error: ' + e.message + '</span>';
            }
        }

        // Load ARP on first view
        document.addEventListener('DOMContentLoaded', () => {
            // Enter key support
            document.getElementById('mac-input').addEventListener('keypress', e => {
                if (e.key === 'Enter') lookupMAC();
            });
        });
    </script>
</body>
</html>
'''


def create_app():
    """Create Flask application"""
    app = Flask(__name__)
    lookup = MACLookup()
    
    @app.route('/')
    def index():
        return render_template_string(HTML_TEMPLATE)
    
    @app.route('/api/lookup')
    def api_lookup():
        mac = request.args.get('mac', '')
        if not mac:
            return jsonify({'error': 'MAC address required'}), 400
        
        result = lookup.lookup(mac)
        return jsonify(result)
    
    @app.route('/api/scan')
    def api_scan():
        target = request.args.get('target')
        results = scan_network(target if target else None)
        return jsonify(results)
    
    @app.route('/api/arp')
    def api_arp():
        return jsonify(get_arp_table())
    
    @app.route('/api/ports')
    def api_ports():
        target = request.args.get('target', '')
        ports = request.args.get('ports', '22,80,443,3389,445')
        
        if not target:
            return jsonify({'error': 'Target IP required'}), 400
        
        results = scan_ports(target, ports)
        return jsonify(results)
    
    @app.route('/api/info')
    def api_info():
        return jsonify(get_network_info())
    
    return app


def main():
    """CLI entry point"""
    if not HAS_FLASK:
        print("Error: Flask is required for web interface")
        print("Install with: pip install flask")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(description='NetScan Web Server')
    parser.add_argument('-p', '--port', type=int, default=5555, help='Port to listen on')
    parser.add_argument('-H', '--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    app = create_app()
    
    print(f"\n  NetScan Web Interface")
    print(f"  =====================")
    print(f"  Running on: http://localhost:{args.port}")
    print(f"  Press Ctrl+C to stop\n")
    
    try:
        app.run(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        print("\n  Server stopped")


if __name__ == '__main__':
    main()
