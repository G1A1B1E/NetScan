#!/usr/bin/env python3
"""
NetScan Export Module
Export scan results to various formats: CSV, HTML, JSON, PDF

Features:
- CSV export for spreadsheets
- Styled HTML reports
- JSON export for APIs
- PDF reports (requires weasyprint)
- Prometheus metrics format
"""

import os
import sys
import json
import csv
import argparse
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict
import html


@dataclass
class ScanResult:
    """Represents a single scan result"""
    ip: str
    mac: str
    hostname: str = ""
    vendor: str = ""
    device_type: str = ""
    ports: List[int] = None
    first_seen: str = ""
    last_seen: str = ""
    status: str = "up"
    
    def __post_init__(self):
        if self.ports is None:
            self.ports = []
    
    def to_dict(self) -> dict:
        return asdict(self)


class Exporter:
    """Export scan results to various formats"""
    
    def __init__(self, results: List[Dict], metadata: Dict = None):
        """
        Initialize exporter
        
        Args:
            results: List of scan results (dicts with ip, mac, hostname, vendor, etc.)
            metadata: Optional metadata (scan_time, network, etc.)
        """
        self.results = results
        self.metadata = metadata or {
            'scan_time': datetime.now().isoformat(),
            'tool': 'NetScan',
            'version': '1.1.0'
        }
    
    def to_csv(self, filepath: str = None, include_header: bool = True) -> str:
        """
        Export to CSV format
        
        Args:
            filepath: Output file path (if None, returns string)
            include_header: Include column headers
        
        Returns:
            CSV string if no filepath provided
        """
        if not self.results:
            return ""
        
        # Determine columns from first result
        columns = ['ip', 'mac', 'hostname', 'vendor', 'device_type', 'status', 'ports']
        
        output = []
        
        if include_header:
            output.append(','.join(columns))
        
        for result in self.results:
            row = []
            for col in columns:
                value = result.get(col, '')
                if isinstance(value, list):
                    value = ';'.join(map(str, value))
                # Escape commas and quotes
                value = str(value).replace('"', '""')
                if ',' in value or '"' in value:
                    value = f'"{value}"'
                row.append(value)
            output.append(','.join(row))
        
        csv_content = '\n'.join(output)
        
        if filepath:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                f.write(csv_content)
        
        return csv_content
    
    def to_json(self, filepath: str = None, pretty: bool = True) -> str:
        """
        Export to JSON format
        
        Args:
            filepath: Output file path (if None, returns string)
            pretty: Pretty print with indentation
        
        Returns:
            JSON string if no filepath provided
        """
        data = {
            'metadata': self.metadata,
            'device_count': len(self.results),
            'devices': self.results
        }
        
        indent = 2 if pretty else None
        json_content = json.dumps(data, indent=indent, default=str)
        
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json_content)
        
        return json_content
    
    def to_html(self, filepath: str = None, title: str = "Network Scan Report") -> str:
        """
        Export to styled HTML report
        
        Args:
            filepath: Output file path (if None, returns string)
            title: Report title
        
        Returns:
            HTML string if no filepath provided
        """
        scan_time = self.metadata.get('scan_time', datetime.now().isoformat())
        network = self.metadata.get('network', 'Local Network')
        
        # Count device types
        type_counts = {}
        vendor_counts = {}
        for r in self.results:
            dt = r.get('device_type', 'unknown')
            type_counts[dt] = type_counts.get(dt, 0) + 1
            vendor = r.get('vendor', 'Unknown')[:30]
            vendor_counts[vendor] = vendor_counts.get(vendor, 0) + 1
        
        # Generate HTML
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        header {{
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }}
        h1 {{
            color: #4ecca3;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .meta {{
            color: #888;
            font-size: 0.9em;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #4ecca3;
        }}
        .stat-label {{
            color: #888;
            text-transform: uppercase;
            font-size: 0.8em;
            margin-top: 5px;
        }}
        .card {{
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
        }}
        .card h2 {{
            color: #4ecca3;
            margin-bottom: 20px;
            font-size: 1.3em;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th {{
            background: rgba(78, 204, 163, 0.2);
            color: #4ecca3;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        tr:hover td {{
            background: rgba(255,255,255,0.05);
        }}
        .mac {{ font-family: monospace; color: #f39c12; }}
        .ip {{ font-family: monospace; color: #3498db; }}
        .vendor {{ color: #9b59b6; }}
        .hostname {{ color: #e74c3c; }}
        .device-type {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.8em;
            background: rgba(78, 204, 163, 0.2);
            color: #4ecca3;
        }}
        .status-up {{ color: #2ecc71; }}
        .status-down {{ color: #e74c3c; }}
        footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.8em;
        }}
        @media print {{
            body {{ background: white; color: black; }}
            .card, header {{ background: #f5f5f5; }}
            th {{ background: #4ecca3; color: white; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 {html.escape(title)}</h1>
            <p class="meta">
                Generated: {scan_time[:19].replace('T', ' ')} | 
                Network: {html.escape(network)} |
                Tool: NetScan v1.1
            </p>
        </header>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{len(self.results)}</div>
                <div class="stat-label">Total Devices</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(vendor_counts)}</div>
                <div class="stat-label">Unique Vendors</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{type_counts.get('router', 0)}</div>
                <div class="stat-label">Routers</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{sum(1 for r in self.results if r.get('status') == 'up')}</div>
                <div class="stat-label">Online</div>
            </div>
        </div>
        
        <div class="card">
            <h2>📋 Device List</h2>
            <table>
                <thead>
                    <tr>
                        <th>IP Address</th>
                        <th>MAC Address</th>
                        <th>Hostname</th>
                        <th>Vendor</th>
                        <th>Type</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
'''
        
        for device in sorted(self.results, key=lambda x: [int(p) for p in x.get('ip', '0.0.0.0').split('.')]):
            ip = html.escape(device.get('ip', 'N/A'))
            mac = html.escape(device.get('mac', 'N/A'))
            hostname = html.escape(device.get('hostname', ''))[:30] or '-'
            vendor = html.escape(device.get('vendor', 'Unknown'))[:35]
            device_type = html.escape(device.get('device_type', 'unknown'))
            status = device.get('status', 'up')
            status_class = 'status-up' if status == 'up' else 'status-down'
            
            html_content += f'''                    <tr>
                        <td class="ip">{ip}</td>
                        <td class="mac">{mac}</td>
                        <td class="hostname">{hostname}</td>
                        <td class="vendor">{vendor}</td>
                        <td><span class="device-type">{device_type}</span></td>
                        <td class="{status_class}">●</td>
                    </tr>
'''
        
        html_content += '''                </tbody>
            </table>
        </div>
        
        <footer>
            Generated by NetScan | https://github.com/G1A1B1E/NetScan
        </footer>
    </div>
</body>
</html>'''
        
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
        
        return html_content
    
    def to_prometheus(self, filepath: str = None) -> str:
        """
        Export to Prometheus metrics format
        
        Args:
            filepath: Output file path (if None, returns string)
        
        Returns:
            Prometheus format string
        """
        lines = [
            '# HELP netscan_devices_total Total number of discovered devices',
            '# TYPE netscan_devices_total gauge',
            f'netscan_devices_total {len(self.results)}',
            '',
            '# HELP netscan_device_info Device information',
            '# TYPE netscan_device_info gauge',
        ]
        
        for device in self.results:
            ip = device.get('ip', 'unknown')
            mac = device.get('mac', 'unknown')
            vendor = device.get('vendor', 'unknown').replace('"', '\\"')
            hostname = device.get('hostname', '').replace('"', '\\"')
            device_type = device.get('device_type', 'unknown')
            
            labels = f'ip="{ip}",mac="{mac}",vendor="{vendor}",hostname="{hostname}",type="{device_type}"'
            lines.append(f'netscan_device_info{{{labels}}} 1')
        
        # Add timestamp
        lines.extend([
            '',
            '# HELP netscan_last_scan_timestamp Last scan timestamp',
            '# TYPE netscan_last_scan_timestamp gauge',
            f'netscan_last_scan_timestamp {int(datetime.now().timestamp())}'
        ])
        
        content = '\n'.join(lines)
        
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return content
    
    def to_markdown(self, filepath: str = None) -> str:
        """
        Export to Markdown format
        
        Args:
            filepath: Output file path (if None, returns string)
        
        Returns:
            Markdown string
        """
        scan_time = self.metadata.get('scan_time', datetime.now().isoformat())
        
        md = f'''# Network Scan Report

**Generated:** {scan_time[:19].replace('T', ' ')}  
**Devices Found:** {len(self.results)}

## Device List

| IP Address | MAC Address | Hostname | Vendor | Type |
|------------|-------------|----------|--------|------|
'''
        
        for device in sorted(self.results, key=lambda x: x.get('ip', '')):
            ip = device.get('ip', 'N/A')
            mac = device.get('mac', 'N/A')
            hostname = device.get('hostname', '-')[:20] or '-'
            vendor = device.get('vendor', 'Unknown')[:25]
            device_type = device.get('device_type', 'unknown')
            
            md += f'| {ip} | `{mac}` | {hostname} | {vendor} | {device_type} |\n'
        
        md += '\n---\n*Generated by [NetScan](https://github.com/G1A1B1E/NetScan)*\n'
        
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(md)
        
        return md
    
    def export(self, format: str, filepath: str = None, **kwargs) -> str:
        """
        Export to specified format
        
        Args:
            format: Export format (csv, json, html, prometheus, markdown)
            filepath: Output file path
            **kwargs: Additional format-specific options
        
        Returns:
            Exported content as string
        """
        exporters = {
            'csv': self.to_csv,
            'json': self.to_json,
            'html': self.to_html,
            'prometheus': self.to_prometheus,
            'prom': self.to_prometheus,
            'md': self.to_markdown,
            'markdown': self.to_markdown
        }
        
        exporter_func = exporters.get(format.lower())
        if not exporter_func:
            raise ValueError(f"Unsupported format: {format}. Supported: {', '.join(exporters.keys())}")
        
        return exporter_func(filepath, **kwargs)


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Export network scan results to various formats',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Export from JSON input
  cat scan.json | python export.py -f html -o report.html
  
  # Export from stdin
  python scanner.py --scan --json | python export.py -f csv -o devices.csv
  
  # Generate HTML report
  python export.py -i scan.json -f html -o report.html --title "Office Network"
  
  # Export to Prometheus format
  python export.py -i scan.json -f prometheus -o metrics.prom

Supported formats: csv, json, html, markdown, prometheus
        '''
    )
    
    parser.add_argument('-i', '--input', metavar='FILE',
                       help='Input JSON file (default: stdin)')
    parser.add_argument('-o', '--output', metavar='FILE',
                       help='Output file (default: stdout)')
    parser.add_argument('-f', '--format', default='json',
                       choices=['csv', 'json', 'html', 'markdown', 'md', 'prometheus', 'prom'],
                       help='Output format (default: json)')
    parser.add_argument('--title', default='Network Scan Report',
                       help='Report title (for HTML)')
    parser.add_argument('--network', default='Local Network',
                       help='Network name for metadata')
    parser.add_argument('--no-pretty', action='store_true',
                       help='Disable pretty printing for JSON')
    
    args = parser.parse_args()
    
    # Read input
    if args.input:
        with open(args.input, 'r') as f:
            input_data = json.load(f)
    else:
        # Read from stdin
        input_data = json.load(sys.stdin)
    
    # Extract results and metadata
    if isinstance(input_data, list):
        results = input_data
        metadata = {}
    else:
        results = input_data.get('devices', input_data.get('results', []))
        metadata = input_data.get('metadata', {})
    
    # Add CLI metadata
    metadata['network'] = args.network
    if 'scan_time' not in metadata:
        metadata['scan_time'] = datetime.now().isoformat()
    
    # Create exporter
    exporter = Exporter(results, metadata)
    
    # Export
    kwargs = {}
    if args.format == 'html':
        kwargs['title'] = args.title
    elif args.format == 'json':
        kwargs['pretty'] = not args.no_pretty
    
    output = exporter.export(args.format, args.output, **kwargs)
    
    # Print to stdout if no output file
    if not args.output:
        print(output)


if __name__ == '__main__':
    main()
