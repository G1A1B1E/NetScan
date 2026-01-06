#!/usr/bin/env python3
"""
Report Generator - Enhanced reporting with PDF, charts, and comparisons
Generates professional network reports in multiple formats
"""

import sys
import os
import json
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from collections import Counter
from pathlib import Path
import html
import base64
import io

# Optional imports for enhanced features
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


class ReportGenerator:
    """Generate network reports in various formats"""
    
    def __init__(self, title: str = "Network Report"):
        self.title = title
        self.devices: List[Dict] = []
        self.previous_devices: List[Dict] = []
        self.scan_time = datetime.now()
        self.stats: Dict[str, Any] = {}
    
    def load_devices(self, devices: List[Dict]):
        """Load device data for reporting"""
        self.devices = devices
        self._calculate_stats()
    
    def load_previous(self, devices: List[Dict]):
        """Load previous scan for comparison"""
        self.previous_devices = devices
    
    def load_from_json(self, filepath: str):
        """Load devices from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
            if isinstance(data, list):
                self.devices = data
            elif isinstance(data, dict) and 'devices' in data:
                self.devices = data['devices']
            else:
                self.devices = [data]
        self._calculate_stats()
    
    def _calculate_stats(self):
        """Calculate statistics from device data"""
        vendors = Counter()
        with_hostname = 0
        with_vendor = 0
        with_mac = 0
        
        for device in self.devices:
            vendor = device.get('vendor', 'Unknown') or 'Unknown'
            vendors[vendor] += 1
            
            if device.get('hostname'):
                with_hostname += 1
            if device.get('vendor'):
                with_vendor += 1
            if device.get('mac'):
                with_mac += 1
        
        self.stats = {
            'total_devices': len(self.devices),
            'with_hostname': with_hostname,
            'with_vendor': with_vendor,
            'with_mac': with_mac,
            'vendors': dict(vendors.most_common(20)),
            'scan_time': self.scan_time.isoformat()
        }
    
    def _get_comparison(self) -> Dict:
        """Compare current vs previous scan"""
        if not self.previous_devices:
            return {}
        
        current_macs = {d.get('mac', '').lower() for d in self.devices if d.get('mac')}
        previous_macs = {d.get('mac', '').lower() for d in self.previous_devices if d.get('mac')}
        
        new_macs = current_macs - previous_macs
        gone_macs = previous_macs - current_macs
        same_macs = current_macs & previous_macs
        
        new_devices = [d for d in self.devices if d.get('mac', '').lower() in new_macs]
        gone_devices = [d for d in self.previous_devices if d.get('mac', '').lower() in gone_macs]
        
        return {
            'new_count': len(new_macs),
            'gone_count': len(gone_macs),
            'same_count': len(same_macs),
            'new_devices': new_devices,
            'gone_devices': gone_devices
        }
    
    # =========================================================================
    # Chart Generation
    # =========================================================================
    
    def _generate_vendor_chart_matplotlib(self) -> Optional[bytes]:
        """Generate vendor distribution chart using matplotlib"""
        if not HAS_MATPLOTLIB or not self.stats.get('vendors'):
            return None
        
        vendors = self.stats['vendors']
        
        # Limit to top 10 for readability
        items = list(vendors.items())[:10]
        if len(vendors) > 10:
            other_count = sum(v for k, v in list(vendors.items())[10:])
            items.append(('Other', other_count))
        
        labels = [item[0][:20] for item in items]  # Truncate long names
        sizes = [item[1] for item in items]
        
        # Create pie chart
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Pie chart
        colors_list = plt.cm.Set3(range(len(labels)))
        wedges, texts, autotexts = ax1.pie(sizes, labels=None, autopct='%1.1f%%',
                                           colors=colors_list, startangle=90)
        ax1.set_title('Vendor Distribution')
        ax1.legend(wedges, labels, title="Vendors", loc="center left", 
                   bbox_to_anchor=(1, 0, 0.5, 1), fontsize=8)
        
        # Bar chart
        ax2.barh(labels, sizes, color=colors_list)
        ax2.set_xlabel('Number of Devices')
        ax2.set_title('Devices by Vendor')
        ax2.invert_yaxis()
        
        plt.tight_layout()
        
        # Save to bytes
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        plt.close()
        buf.seek(0)
        return buf.getvalue()
    
    def _generate_vendor_chart_svg(self) -> str:
        """Generate simple SVG chart without external dependencies"""
        vendors = self.stats.get('vendors', {})
        if not vendors:
            return ""
        
        items = list(vendors.items())[:8]
        total = sum(v for _, v in items)
        
        # SVG dimensions
        width, height = 400, 250
        bar_height = 25
        max_bar_width = 280
        
        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',
            '<style>',
            '  .bar { fill: #4a90d9; }',
            '  .bar:hover { fill: #357abd; }',
            '  .label { font-family: sans-serif; font-size: 12px; fill: #333; }',
            '  .value { font-family: sans-serif; font-size: 11px; fill: #666; }',
            '  .title { font-family: sans-serif; font-size: 14px; font-weight: bold; fill: #333; }',
            '</style>',
            f'<text x="{width/2}" y="20" class="title" text-anchor="middle">Vendor Distribution</text>'
        ]
        
        max_count = max(v for _, v in items) if items else 1
        y_offset = 40
        
        colors = ['#4a90d9', '#50c878', '#f4a460', '#dda0dd', '#87ceeb', 
                  '#f0e68c', '#98d8c8', '#f7dc6f']
        
        for i, (vendor, count) in enumerate(items):
            bar_width = (count / max_count) * max_bar_width
            color = colors[i % len(colors)]
            y = y_offset + i * (bar_height + 5)
            
            # Truncate vendor name
            display_name = vendor[:25] + '...' if len(vendor) > 25 else vendor
            
            svg_parts.append(
                f'<rect x="100" y="{y}" width="{bar_width}" height="{bar_height}" '
                f'class="bar" style="fill: {color};" rx="3"/>'
            )
            svg_parts.append(
                f'<text x="95" y="{y + bar_height/2 + 4}" class="label" '
                f'text-anchor="end">{html.escape(display_name)}</text>'
            )
            svg_parts.append(
                f'<text x="{105 + bar_width}" y="{y + bar_height/2 + 4}" class="value">'
                f'{count} ({count*100//total}%)</text>'
            )
        
        svg_parts.append('</svg>')
        return '\n'.join(svg_parts)
    
    # =========================================================================
    # HTML Report
    # =========================================================================
    
    def generate_html(self, include_charts: bool = True) -> str:
        """Generate HTML report"""
        comparison = self._get_comparison()
        
        # Generate chart
        chart_html = ""
        if include_charts:
            if HAS_MATPLOTLIB:
                chart_bytes = self._generate_vendor_chart_matplotlib()
                if chart_bytes:
                    b64_chart = base64.b64encode(chart_bytes).decode()
                    chart_html = f'<img src="data:image/png;base64,{b64_chart}" alt="Vendor Chart" style="max-width: 100%;">'
            else:
                chart_html = self._generate_vendor_chart_svg()
        
        # Build HTML
        html_parts = [
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<head>',
            '  <meta charset="UTF-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            f'  <title>{html.escape(self.title)}</title>',
            '  <style>',
            '''
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
           margin: 0; padding: 20px; background: #f5f5f5; }
    .container { max-width: 1200px; margin: 0 auto; background: white; 
                 border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 30px; }
    h1 { color: #333; border-bottom: 2px solid #4a90d9; padding-bottom: 10px; }
    h2 { color: #4a90d9; margin-top: 30px; }
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                  gap: 20px; margin: 20px 0; }
    .stat-card { background: #f8f9fa; border-radius: 8px; padding: 20px; text-align: center; }
    .stat-value { font-size: 36px; font-weight: bold; color: #4a90d9; }
    .stat-label { color: #666; margin-top: 5px; }
    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
    th { background: #4a90d9; color: white; }
    tr:hover { background: #f5f5f5; }
    .mac { font-family: monospace; }
    .ip { font-family: monospace; }
    .new { background: #d4edda !important; }
    .gone { background: #f8d7da !important; }
    .chart-container { margin: 30px 0; text-align: center; }
    .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; 
              color: #666; font-size: 12px; }
    .comparison-section { margin: 20px 0; padding: 20px; border-radius: 8px; }
    .comparison-new { background: #d4edda; }
    .comparison-gone { background: #f8d7da; }
            ''',
            '  </style>',
            '</head>',
            '<body>',
            '  <div class="container">',
            f'    <h1>📊 {html.escape(self.title)}</h1>',
            f'    <p>Generated: {self.scan_time.strftime("%Y-%m-%d %H:%M:%S")}</p>',
            '',
            '    <h2>Summary Statistics</h2>',
            '    <div class="stats-grid">',
            f'      <div class="stat-card"><div class="stat-value">{self.stats["total_devices"]}</div><div class="stat-label">Total Devices</div></div>',
            f'      <div class="stat-card"><div class="stat-value">{self.stats["with_mac"]}</div><div class="stat-label">With MAC</div></div>',
            f'      <div class="stat-card"><div class="stat-value">{self.stats["with_hostname"]}</div><div class="stat-label">With Hostname</div></div>',
            f'      <div class="stat-card"><div class="stat-value">{self.stats["with_vendor"]}</div><div class="stat-label">Identified Vendor</div></div>',
            '    </div>',
        ]
        
        # Comparison section
        if comparison:
            html_parts.extend([
                '    <h2>Changes Since Last Scan</h2>',
                '    <div class="stats-grid">',
                f'      <div class="stat-card" style="background: #d4edda;"><div class="stat-value">{comparison["new_count"]}</div><div class="stat-label">New Devices</div></div>',
                f'      <div class="stat-card" style="background: #f8d7da;"><div class="stat-value">{comparison["gone_count"]}</div><div class="stat-label">Gone Devices</div></div>',
                f'      <div class="stat-card"><div class="stat-value">{comparison["same_count"]}</div><div class="stat-label">Unchanged</div></div>',
                '    </div>',
            ])
            
            if comparison['new_devices']:
                html_parts.append('    <div class="comparison-section comparison-new">')
                html_parts.append('      <h3>🆕 New Devices</h3>')
                html_parts.append('      <table>')
                html_parts.append('        <tr><th>IP Address</th><th>MAC Address</th><th>Hostname</th><th>Vendor</th></tr>')
                for d in comparison['new_devices']:
                    html_parts.append(
                        f'        <tr><td class="ip">{html.escape(d.get("ip", ""))}</td>'
                        f'<td class="mac">{html.escape(d.get("mac", ""))}</td>'
                        f'<td>{html.escape(d.get("hostname", "") or "")}</td>'
                        f'<td>{html.escape(d.get("vendor", "") or "")}</td></tr>'
                    )
                html_parts.append('      </table>')
                html_parts.append('    </div>')
            
            if comparison['gone_devices']:
                html_parts.append('    <div class="comparison-section comparison-gone">')
                html_parts.append('      <h3>👋 Gone Devices</h3>')
                html_parts.append('      <table>')
                html_parts.append('        <tr><th>IP Address</th><th>MAC Address</th><th>Hostname</th><th>Vendor</th></tr>')
                for d in comparison['gone_devices']:
                    html_parts.append(
                        f'        <tr><td class="ip">{html.escape(d.get("ip", ""))}</td>'
                        f'<td class="mac">{html.escape(d.get("mac", ""))}</td>'
                        f'<td>{html.escape(d.get("hostname", "") or "")}</td>'
                        f'<td>{html.escape(d.get("vendor", "") or "")}</td></tr>'
                    )
                html_parts.append('      </table>')
                html_parts.append('    </div>')
        
        # Chart
        if chart_html:
            html_parts.extend([
                '    <h2>Vendor Distribution</h2>',
                '    <div class="chart-container">',
                f'      {chart_html}',
                '    </div>',
            ])
        
        # Device table
        html_parts.extend([
            '    <h2>All Devices</h2>',
            '    <table>',
            '      <tr><th>IP Address</th><th>MAC Address</th><th>Hostname</th><th>Vendor</th></tr>',
        ])
        
        # Sort devices by IP
        sorted_devices = sorted(
            self.devices,
            key=lambda d: tuple(map(int, d.get('ip', '0.0.0.0').split('.')))
        )
        
        for device in sorted_devices:
            html_parts.append(
                f'      <tr><td class="ip">{html.escape(device.get("ip", ""))}</td>'
                f'<td class="mac">{html.escape(device.get("mac", ""))}</td>'
                f'<td>{html.escape(device.get("hostname", "") or "")}</td>'
                f'<td>{html.escape(device.get("vendor", "") or "")}</td></tr>'
            )
        
        html_parts.extend([
            '    </table>',
            '',
            '    <div class="footer">',
            '      Generated by NetScan Report Generator',
            '    </div>',
            '  </div>',
            '</body>',
            '</html>'
        ])
        
        return '\n'.join(html_parts)
    
    # =========================================================================
    # PDF Report
    # =========================================================================
    
    def generate_pdf(self, output_path: str) -> bool:
        """Generate PDF report"""
        if not HAS_REPORTLAB:
            print("Error: reportlab not installed. Install with: pip install reportlab", 
                  file=sys.stderr)
            return False
        
        doc = SimpleDocTemplate(output_path, pagesize=letter,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=72)
        
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#4a90d9')
        )
        story.append(Paragraph(self.title, title_style))
        story.append(Paragraph(f"Generated: {self.scan_time.strftime('%Y-%m-%d %H:%M:%S')}", 
                              styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Summary stats
        story.append(Paragraph("Summary Statistics", styles['Heading2']))
        stats_data = [
            ['Total Devices', str(self.stats['total_devices'])],
            ['With MAC Address', str(self.stats['with_mac'])],
            ['With Hostname', str(self.stats['with_hostname'])],
            ['Identified Vendor', str(self.stats['with_vendor'])],
        ]
        stats_table = Table(stats_data, colWidths=[200, 100])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.white),
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 20))
        
        # Vendor breakdown
        story.append(Paragraph("Top Vendors", styles['Heading2']))
        vendor_data = [['Vendor', 'Count']]
        for vendor, count in list(self.stats['vendors'].items())[:10]:
            vendor_data.append([vendor[:40], str(count)])
        
        vendor_table = Table(vendor_data, colWidths=[350, 80])
        vendor_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90d9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ddd')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        story.append(vendor_table)
        story.append(Spacer(1, 20))
        
        # Device list
        story.append(Paragraph("Device List", styles['Heading2']))
        device_data = [['IP Address', 'MAC Address', 'Hostname', 'Vendor']]
        
        sorted_devices = sorted(
            self.devices,
            key=lambda d: tuple(map(int, d.get('ip', '0.0.0.0').split('.')))
        )
        
        for device in sorted_devices[:50]:  # Limit to 50 for PDF
            device_data.append([
                device.get('ip', ''),
                device.get('mac', ''),
                (device.get('hostname', '') or '')[:20],
                (device.get('vendor', '') or '')[:25]
            ])
        
        device_table = Table(device_data, colWidths=[90, 110, 130, 140])
        device_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90d9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (1, -1), 'Courier'),  # Monospace for IP/MAC
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ddd')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        story.append(device_table)
        
        if len(self.devices) > 50:
            story.append(Spacer(1, 10))
            story.append(Paragraph(f"... and {len(self.devices) - 50} more devices", 
                                  styles['Normal']))
        
        # Build PDF
        doc.build(story)
        return True
    
    # =========================================================================
    # JSON Report
    # =========================================================================
    
    def generate_json(self, pretty: bool = True) -> str:
        """Generate JSON report"""
        report = {
            'title': self.title,
            'generated': self.scan_time.isoformat(),
            'statistics': self.stats,
            'devices': self.devices
        }
        
        if self.previous_devices:
            report['comparison'] = self._get_comparison()
        
        indent = 2 if pretty else None
        return json.dumps(report, indent=indent, default=str)
    
    # =========================================================================
    # Markdown Report
    # =========================================================================
    
    def generate_markdown(self) -> str:
        """Generate Markdown report"""
        lines = [
            f"# {self.title}",
            "",
            f"**Generated:** {self.scan_time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary Statistics",
            "",
            f"| Metric | Value |",
            f"| --- | --- |",
            f"| Total Devices | {self.stats['total_devices']} |",
            f"| With MAC Address | {self.stats['with_mac']} |",
            f"| With Hostname | {self.stats['with_hostname']} |",
            f"| Identified Vendor | {self.stats['with_vendor']} |",
            "",
            "## Top Vendors",
            "",
            "| Vendor | Count |",
            "| --- | --- |",
        ]
        
        for vendor, count in list(self.stats['vendors'].items())[:10]:
            lines.append(f"| {vendor} | {count} |")
        
        # Comparison
        comparison = self._get_comparison()
        if comparison:
            lines.extend([
                "",
                "## Changes Since Last Scan",
                "",
                f"- **New devices:** {comparison['new_count']}",
                f"- **Gone devices:** {comparison['gone_count']}",
                f"- **Unchanged:** {comparison['same_count']}",
            ])
            
            if comparison['new_devices']:
                lines.extend(["", "### New Devices", ""])
                lines.append("| IP | MAC | Vendor |")
                lines.append("| --- | --- | --- |")
                for d in comparison['new_devices']:
                    lines.append(f"| {d.get('ip', '')} | {d.get('mac', '')} | {d.get('vendor', '')} |")
            
            if comparison['gone_devices']:
                lines.extend(["", "### Gone Devices", ""])
                lines.append("| IP | MAC | Vendor |")
                lines.append("| --- | --- | --- |")
                for d in comparison['gone_devices']:
                    lines.append(f"| {d.get('ip', '')} | {d.get('mac', '')} | {d.get('vendor', '')} |")
        
        # Device list
        lines.extend([
            "",
            "## All Devices",
            "",
            "| IP Address | MAC Address | Hostname | Vendor |",
            "| --- | --- | --- | --- |",
        ])
        
        sorted_devices = sorted(
            self.devices,
            key=lambda d: tuple(map(int, d.get('ip', '0.0.0.0').split('.')))
        )
        
        for device in sorted_devices:
            lines.append(
                f"| {device.get('ip', '')} | {device.get('mac', '')} | "
                f"{device.get('hostname', '') or ''} | {device.get('vendor', '') or ''} |"
            )
        
        lines.extend([
            "",
            "---",
            "*Generated by NetScan Report Generator*"
        ])
        
        return '\n'.join(lines)


# =============================================================================
# CLI Interface
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Report Generator - Create network reports',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s devices.json --html > report.html
  %(prog)s devices.json --pdf report.pdf
  %(prog)s devices.json --markdown > report.md
  %(prog)s current.json --compare previous.json --html > diff.html
  cat devices.json | %(prog)s --html > report.html
        """
    )
    
    parser.add_argument('input', nargs='?', help='Input JSON file (or stdin)')
    parser.add_argument('--compare', '-c', metavar='FILE',
                        help='Previous scan file for comparison')
    parser.add_argument('--title', '-t', default='Network Report',
                        help='Report title')
    
    # Output formats
    parser.add_argument('--html', action='store_true', help='Generate HTML report')
    parser.add_argument('--pdf', metavar='FILE', help='Generate PDF report')
    parser.add_argument('--markdown', '-m', action='store_true', help='Generate Markdown report')
    parser.add_argument('--json', '-j', action='store_true', help='Generate JSON report')
    
    # Options
    parser.add_argument('--no-charts', action='store_true', help='Exclude charts from HTML')
    parser.add_argument('--output', '-o', metavar='FILE', help='Output file (default: stdout)')
    
    args = parser.parse_args()
    
    # Create generator
    generator = ReportGenerator(title=args.title)
    
    # Load data
    if args.input:
        generator.load_from_json(args.input)
    else:
        # Read from stdin
        data = json.load(sys.stdin)
        if isinstance(data, list):
            generator.load_devices(data)
        elif isinstance(data, dict) and 'devices' in data:
            generator.load_devices(data['devices'])
        else:
            generator.load_devices([data])
    
    # Load comparison data
    if args.compare:
        with open(args.compare, 'r') as f:
            prev_data = json.load(f)
            if isinstance(prev_data, list):
                generator.load_previous(prev_data)
            elif isinstance(prev_data, dict) and 'devices' in prev_data:
                generator.load_previous(prev_data['devices'])
    
    # Generate output
    output = None
    
    if args.pdf:
        if generator.generate_pdf(args.pdf):
            print(f"PDF report saved to: {args.pdf}")
        else:
            return 1
        return 0
    elif args.html:
        output = generator.generate_html(include_charts=not args.no_charts)
    elif args.markdown:
        output = generator.generate_markdown()
    elif args.json:
        output = generator.generate_json()
    else:
        # Default to HTML
        output = generator.generate_html(include_charts=not args.no_charts)
    
    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Report saved to: {args.output}", file=sys.stderr)
    else:
        print(output)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
