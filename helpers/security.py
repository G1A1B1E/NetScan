#!/usr/bin/env python3
"""
NetScan Security Audit Module
Check for common network security issues and vulnerabilities

Features:
- Open port risk assessment
- Default credential detection
- Service version vulnerability checks  
- Network segmentation analysis
- Security recommendations
"""

import os
import sys
import json
import argparse
import subprocess
import socket
import ssl
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime


@dataclass
class SecurityFinding:
    """A security finding/issue"""
    severity: str  # critical, high, medium, low, info
    category: str  # open_ports, credentials, services, config
    title: str
    description: str
    target: str  # IP or host
    port: int = 0
    recommendation: str = ""
    references: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SecurityReport:
    """Complete security audit report"""
    scan_time: str
    target_network: str
    total_hosts: int
    findings: List[SecurityFinding] = field(default_factory=list)
    risk_summary: Dict[str, int] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            'scan_time': self.scan_time,
            'target_network': self.target_network,
            'total_hosts': self.total_hosts,
            'findings': [f.to_dict() for f in self.findings],
            'risk_summary': self.risk_summary,
            'recommendations': self.recommendations
        }


class SecurityAuditor:
    """Network security auditor"""
    
    # Risky open ports
    RISKY_PORTS = {
        21: ('FTP', 'high', 'FTP transmits data in cleartext. Consider SFTP instead.'),
        23: ('Telnet', 'critical', 'Telnet transmits data in cleartext. Use SSH instead.'),
        25: ('SMTP', 'medium', 'Open mail relay can be abused for spam.'),
        53: ('DNS', 'low', 'Ensure DNS server is not misconfigured for amplification attacks.'),
        80: ('HTTP', 'medium', 'HTTP is unencrypted. Consider using HTTPS.'),
        110: ('POP3', 'high', 'POP3 transmits credentials in cleartext.'),
        111: ('RPC', 'high', 'RPC services can expose system information.'),
        135: ('MSRPC', 'high', 'Windows RPC can be vulnerable to attacks.'),
        139: ('NetBIOS', 'high', 'NetBIOS can leak system information.'),
        143: ('IMAP', 'high', 'IMAP transmits credentials in cleartext.'),
        161: ('SNMP', 'high', 'SNMP v1/v2 use weak authentication.'),
        389: ('LDAP', 'high', 'Unencrypted LDAP can expose directory info.'),
        445: ('SMB', 'critical', 'SMB can be vulnerable to ransomware and attacks.'),
        512: ('rexec', 'critical', 'Remote execution without proper authentication.'),
        513: ('rlogin', 'critical', 'Insecure remote login protocol.'),
        514: ('rsh', 'critical', 'Remote shell without encryption.'),
        1433: ('MSSQL', 'high', 'Database exposed to network.'),
        1521: ('Oracle', 'high', 'Database exposed to network.'),
        2049: ('NFS', 'high', 'NFS can expose file systems.'),
        3306: ('MySQL', 'high', 'Database exposed to network.'),
        3389: ('RDP', 'high', 'RDP can be brute-forced and has vulnerabilities.'),
        5432: ('PostgreSQL', 'high', 'Database exposed to network.'),
        5900: ('VNC', 'high', 'VNC may have weak authentication.'),
        5901: ('VNC', 'high', 'VNC may have weak authentication.'),
        6379: ('Redis', 'critical', 'Redis often has no authentication.'),
        8080: ('HTTP Proxy', 'medium', 'HTTP proxy may be open.'),
        8443: ('HTTPS Alt', 'low', 'Alternative HTTPS port.'),
        9200: ('Elasticsearch', 'critical', 'Elasticsearch often has no authentication.'),
        27017: ('MongoDB', 'critical', 'MongoDB often has no authentication.'),
    }
    
    # Known default credentials to check
    DEFAULT_CREDS = {
        'ssh': [('root', 'root'), ('admin', 'admin'), ('root', 'toor'), ('admin', 'password')],
        'telnet': [('admin', 'admin'), ('root', 'root'), ('admin', ''), ('admin', 'password')],
        'ftp': [('anonymous', ''), ('ftp', 'ftp'), ('admin', 'admin')],
        'mysql': [('root', ''), ('root', 'root'), ('mysql', 'mysql')],
        'redis': [('', '')],  # Redis often has no auth
    }
    
    def __init__(self, timeout: float = 5.0, threads: int = 20):
        self.timeout = timeout
        self.threads = threads
        self.report = SecurityReport(
            scan_time=datetime.now().isoformat(),
            target_network="",
            total_hosts=0
        )
    
    def check_port(self, ip: str, port: int) -> bool:
        """Check if port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def check_ssl_cert(self, ip: str, port: int = 443) -> Optional[dict]:
        """Check SSL certificate"""
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with socket.create_connection((ip, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=ip) as ssock:
                    cert = ssock.getpeercert(binary_form=False)
                    if cert:
                        return cert
                    
                    # Get binary cert for basic info
                    der_cert = ssock.getpeercert(binary_form=True)
                    if der_cert:
                        return {'raw': True}
        except Exception as e:
            pass
        return None
    
    def check_http_headers(self, ip: str, port: int = 80) -> Dict[str, str]:
        """Check HTTP security headers"""
        try:
            import http.client
            
            if port == 443:
                conn = http.client.HTTPSConnection(ip, port, timeout=self.timeout)
            else:
                conn = http.client.HTTPConnection(ip, port, timeout=self.timeout)
            
            conn.request("HEAD", "/")
            response = conn.getresponse()
            
            headers = dict(response.getheaders())
            conn.close()
            return headers
        except:
            return {}
    
    def audit_host(self, ip: str, ports: List[int] = None, mac: str = "", vendor: str = "") -> List[SecurityFinding]:
        """Audit a single host"""
        findings = []
        
        # If no ports specified, scan common risky ports
        if not ports:
            ports = []
            for port in self.RISKY_PORTS.keys():
                if self.check_port(ip, port):
                    ports.append(port)
        
        # Check each open port
        for port in ports:
            if port in self.RISKY_PORTS:
                service, severity, desc = self.RISKY_PORTS[port]
                findings.append(SecurityFinding(
                    severity=severity,
                    category='open_ports',
                    title=f'{service} Service Open ({port})',
                    description=desc,
                    target=ip,
                    port=port,
                    recommendation=f'Review if {service} on port {port} is necessary. {desc}'
                ))
        
        # Check for SSL on 443
        if 443 in ports:
            cert = self.check_ssl_cert(ip, 443)
            if cert:
                # Check expiry if we have cert details
                if 'notAfter' in cert:
                    try:
                        from datetime import datetime
                        expiry = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                        if expiry < datetime.now():
                            findings.append(SecurityFinding(
                                severity='high',
                                category='services',
                                title='Expired SSL Certificate',
                                description=f'SSL certificate expired on {cert["notAfter"]}',
                                target=ip,
                                port=443,
                                recommendation='Renew the SSL certificate immediately.'
                            ))
                    except:
                        pass
        
        # Check HTTP headers
        if 80 in ports:
            headers = self.check_http_headers(ip, 80)
            missing_headers = []
            
            security_headers = [
                'X-Frame-Options',
                'X-Content-Type-Options',
                'Strict-Transport-Security',
                'Content-Security-Policy',
                'X-XSS-Protection'
            ]
            
            for header in security_headers:
                if header not in headers and header.lower() not in [h.lower() for h in headers]:
                    missing_headers.append(header)
            
            if missing_headers:
                findings.append(SecurityFinding(
                    severity='medium',
                    category='config',
                    title='Missing HTTP Security Headers',
                    description=f'Missing headers: {", ".join(missing_headers)}',
                    target=ip,
                    port=80,
                    recommendation='Add security headers to protect against common web attacks.'
                ))
        
        # Check for known vendor vulnerabilities
        vendor_lower = vendor.lower() if vendor else ""
        if 'hikvision' in vendor_lower or 'dahua' in vendor_lower:
            findings.append(SecurityFinding(
                severity='medium',
                category='services',
                title='IP Camera Detected',
                description=f'IP camera vendor: {vendor}. Many IP cameras have known vulnerabilities.',
                target=ip,
                recommendation='Ensure camera firmware is updated. Change default credentials. Consider network segmentation.'
            ))
        
        if 'tp-link' in vendor_lower or 'd-link' in vendor_lower or 'netgear' in vendor_lower:
            if 80 in ports or 443 in ports:
                findings.append(SecurityFinding(
                    severity='low',
                    category='services',
                    title='Router/AP Web Interface Exposed',
                    description=f'Router web interface accessible: {vendor}',
                    target=ip,
                    port=80 if 80 in ports else 443,
                    recommendation='Ensure admin credentials are changed from defaults.'
                ))
        
        return findings
    
    def audit_network(self, devices: List[dict], check_ports: bool = True) -> SecurityReport:
        """Audit entire network"""
        self.report = SecurityReport(
            scan_time=datetime.now().isoformat(),
            target_network="Local Network",
            total_hosts=len(devices)
        )
        
        all_findings = []
        
        # Audit each device
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {}
            for device in devices:
                ip = device.get('ip', '')
                if not ip:
                    continue
                
                ports = device.get('ports', device.get('open_ports', []))
                mac = device.get('mac', '')
                vendor = device.get('vendor', '')
                
                future = executor.submit(
                    self.audit_host, ip, ports, mac, vendor
                )
                futures[future] = ip
            
            for future in as_completed(futures):
                ip = futures[future]
                try:
                    findings = future.result()
                    all_findings.extend(findings)
                except Exception as e:
                    print(f"Error auditing {ip}: {e}", file=sys.stderr)
        
        self.report.findings = all_findings
        
        # Calculate risk summary
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
        for finding in all_findings:
            severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1
        self.report.risk_summary = severity_counts
        
        # Generate recommendations
        self.report.recommendations = self._generate_recommendations(all_findings)
        
        return self.report
    
    def _generate_recommendations(self, findings: List[SecurityFinding]) -> List[str]:
        """Generate overall security recommendations"""
        recommendations = []
        
        categories = set(f.category for f in findings)
        severities = [f.severity for f in findings]
        
        if 'critical' in severities:
            recommendations.append("⚠️ CRITICAL: Address critical findings immediately!")
        
        if any(f.port in [21, 23, 512, 513, 514] for f in findings):
            recommendations.append("🔒 Replace insecure protocols (Telnet, FTP, rsh) with encrypted alternatives (SSH, SFTP).")
        
        if any(f.port in [1433, 3306, 5432, 6379, 27017] for f in findings):
            recommendations.append("🗄️ Database services should not be exposed to the network. Use firewall rules.")
        
        if any(f.port == 445 for f in findings):
            recommendations.append("📁 SMB is exposed. Ensure proper access controls and patching against ransomware.")
        
        if any(f.port == 3389 for f in findings):
            recommendations.append("🖥️ RDP exposed. Use VPN or restrict access. Enable NLA and strong passwords.")
        
        if any('camera' in f.title.lower() for f in findings):
            recommendations.append("📹 IP cameras detected. Segment IoT devices on separate VLAN.")
        
        if 'config' in categories:
            recommendations.append("⚙️ Review web server configurations and enable security headers.")
        
        if not recommendations:
            recommendations.append("✅ No critical issues found. Continue monitoring for new vulnerabilities.")
        
        return recommendations
    
    def render_text(self) -> str:
        """Render report as text"""
        lines = []
        lines.append("")
        lines.append("=" * 70)
        lines.append("  NETWORK SECURITY AUDIT REPORT")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"  Scan Time: {self.report.scan_time[:19]}")
        lines.append(f"  Hosts Scanned: {self.report.total_hosts}")
        lines.append("")
        
        # Risk summary
        lines.append("-" * 70)
        lines.append("  RISK SUMMARY")
        lines.append("-" * 70)
        colors = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🔵',
            'info': '⚪'
        }
        for severity, count in self.report.risk_summary.items():
            if count > 0:
                lines.append(f"  {colors.get(severity, '⚪')} {severity.upper()}: {count}")
        lines.append("")
        
        # Findings by severity
        for severity in ['critical', 'high', 'medium', 'low']:
            sev_findings = [f for f in self.report.findings if f.severity == severity]
            if sev_findings:
                lines.append("-" * 70)
                lines.append(f"  {colors.get(severity, '')} {severity.upper()} FINDINGS ({len(sev_findings)})")
                lines.append("-" * 70)
                for f in sev_findings:
                    lines.append(f"")
                    lines.append(f"  [{f.target}:{f.port}] {f.title}")
                    lines.append(f"    {f.description}")
                    if f.recommendation:
                        lines.append(f"    → {f.recommendation}")
                lines.append("")
        
        # Recommendations
        if self.report.recommendations:
            lines.append("-" * 70)
            lines.append("  RECOMMENDATIONS")
            lines.append("-" * 70)
            for rec in self.report.recommendations:
                lines.append(f"  • {rec}")
            lines.append("")
        
        lines.append("=" * 70)
        
        return '\n'.join(lines)
    
    def render_html(self) -> str:
        """Render report as HTML"""
        severity_colors = {
            'critical': '#d32f2f',
            'high': '#f57c00',
            'medium': '#fbc02d',
            'low': '#1976d2',
            'info': '#757575'
        }
        
        findings_html = ""
        for severity in ['critical', 'high', 'medium', 'low', 'info']:
            sev_findings = [f for f in self.report.findings if f.severity == severity]
            if sev_findings:
                findings_html += f'<h3 style="color: {severity_colors[severity]}">{severity.upper()} ({len(sev_findings)})</h3>'
                findings_html += '<div class="findings-group">'
                for f in sev_findings:
                    findings_html += f'''
                    <div class="finding" style="border-left: 4px solid {severity_colors[severity]}">
                        <strong>{f.title}</strong> - {f.target}:{f.port}
                        <p>{f.description}</p>
                        <p class="recommendation">→ {f.recommendation}</p>
                    </div>
                    '''
                findings_html += '</div>'
        
        recs_html = "".join(f"<li>{r}</li>" for r in self.report.recommendations)
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <title>Security Audit Report - NetScan</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #d32f2f;
            border-bottom: 2px solid #d32f2f;
            padding-bottom: 10px;
        }}
        .meta {{
            color: #666;
            margin-bottom: 20px;
        }}
        .summary {{
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }}
        .summary-item {{
            padding: 15px 25px;
            border-radius: 8px;
            color: white;
            text-align: center;
        }}
        .summary-item .count {{
            font-size: 24px;
            font-weight: bold;
        }}
        .summary-item .label {{
            font-size: 12px;
            text-transform: uppercase;
        }}
        .finding {{
            padding: 15px;
            margin: 10px 0;
            background: #fafafa;
            border-radius: 4px;
        }}
        .finding p {{
            margin: 5px 0;
            color: #666;
        }}
        .recommendation {{
            color: #1976d2 !important;
            font-style: italic;
        }}
        .recommendations {{
            background: #e3f2fd;
            padding: 20px;
            border-radius: 8px;
            margin-top: 30px;
        }}
        .recommendations h2 {{
            margin-top: 0;
            color: #1976d2;
        }}
        .recommendations li {{
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔒 Network Security Audit Report</h1>
        <div class="meta">
            Scan Time: {self.report.scan_time[:19]} | 
            Hosts Scanned: {self.report.total_hosts}
        </div>
        
        <div class="summary">
            <div class="summary-item" style="background: {severity_colors['critical']}">
                <div class="count">{self.report.risk_summary.get('critical', 0)}</div>
                <div class="label">Critical</div>
            </div>
            <div class="summary-item" style="background: {severity_colors['high']}">
                <div class="count">{self.report.risk_summary.get('high', 0)}</div>
                <div class="label">High</div>
            </div>
            <div class="summary-item" style="background: {severity_colors['medium']}">
                <div class="count">{self.report.risk_summary.get('medium', 0)}</div>
                <div class="label">Medium</div>
            </div>
            <div class="summary-item" style="background: {severity_colors['low']}">
                <div class="count">{self.report.risk_summary.get('low', 0)}</div>
                <div class="label">Low</div>
            </div>
        </div>
        
        <h2>Findings</h2>
        {findings_html if findings_html else '<p>No security issues found.</p>'}
        
        <div class="recommendations">
            <h2>📋 Recommendations</h2>
            <ul>{recs_html}</ul>
        </div>
    </div>
</body>
</html>'''
        
        return html


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(
        description="NetScan Security Auditor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python security.py --input scan.json
  python security.py --input scan.json --html --output report.html
  python security.py --target 192.168.1.1
  python security.py --scan  # Quick network audit
        '''
    )
    
    # Input
    parser.add_argument('--input', '-i', metavar='FILE',
                       help='Input JSON file with scan results')
    parser.add_argument('--target', '-t', metavar='IP',
                       help='Single target IP to audit')
    parser.add_argument('--scan', '-s', action='store_true',
                       help='Perform network scan first')
    
    # Output
    parser.add_argument('--output', '-o', metavar='FILE',
                       help='Output file')
    parser.add_argument('--html', action='store_true',
                       help='Output as HTML')
    parser.add_argument('--json', '-j', action='store_true',
                       help='Output as JSON')
    
    # Options
    parser.add_argument('--no-port-scan', action='store_true',
                       help='Skip port scanning')
    parser.add_argument('--timeout', type=float, default=5.0,
                       help='Connection timeout (default: 5.0s)')
    parser.add_argument('--threads', type=int, default=20,
                       help='Max threads (default: 20)')
    
    args = parser.parse_args()
    
    auditor = SecurityAuditor(timeout=args.timeout, threads=args.threads)
    devices = []
    
    # Load or scan devices
    if args.input:
        try:
            with open(args.input) as f:
                data = json.load(f)
            devices = data.get('devices', data) if isinstance(data, dict) else data
            print(f"Loaded {len(devices)} devices from {args.input}", file=sys.stderr)
        except Exception as e:
            print(f"Error loading input: {e}", file=sys.stderr)
            return 1
    
    elif args.target:
        # Single target audit
        print(f"Auditing {args.target}...", file=sys.stderr)
        findings = auditor.audit_host(args.target)
        auditor.report.findings = findings
        auditor.report.total_hosts = 1
        auditor.report.risk_summary = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
        for f in findings:
            auditor.report.risk_summary[f.severity] += 1
        auditor.report.recommendations = auditor._generate_recommendations(findings)
    
    elif args.scan:
        # Quick network scan
        print("Scanning network...", file=sys.stderr)
        
        # Get local network
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
            s.close()
            base = '.'.join(local_ip.split('.')[:3])
        except:
            base = "192.168.1"
        
        # Ping sweep
        def ping(ip):
            try:
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', '1', ip],
                    capture_output=True, timeout=2
                )
                if result.returncode == 0:
                    return {'ip': ip}
            except:
                pass
            return None
        
        with ThreadPoolExecutor(max_workers=50) as executor:
            results = list(executor.map(ping, [f"{base}.{i}" for i in range(1, 255)]))
            devices = [r for r in results if r]
        
        print(f"Found {len(devices)} hosts", file=sys.stderr)
    
    else:
        parser.print_help()
        return 0
    
    # Run audit
    if devices:
        print("Running security audit...", file=sys.stderr)
        auditor.audit_network(devices, check_ports=not args.no_port_scan)
    
    # Generate output
    if args.html:
        output = auditor.render_html()
    elif args.json:
        output = json.dumps(auditor.report.to_dict(), indent=2)
    else:
        output = auditor.render_text()
    
    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Report saved to {args.output}", file=sys.stderr)
        
        if args.html:
            try:
                import webbrowser
                webbrowser.open(f"file://{os.path.abspath(args.output)}")
            except:
                pass
    else:
        print(output)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
