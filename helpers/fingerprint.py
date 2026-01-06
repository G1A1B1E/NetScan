#!/usr/bin/env python3
"""
NetScan Device Fingerprinting Module
Identify device types using MAC vendor, open ports, TTL, and behavioral analysis

Features:
- Device type classification (router, phone, laptop, IoT, printer, etc.)
- OS detection via TTL and port signatures
- Service identification
- Confidence scoring
"""

import re
import socket
import subprocess
import sys
import json
import argparse
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
from concurrent.futures import ThreadPoolExecutor, as_completed


@dataclass
class DeviceFingerprint:
    """Complete device fingerprint"""
    ip: str
    mac: str
    device_type: str = "unknown"
    device_subtype: str = ""
    os_family: str = ""
    os_version: str = ""
    manufacturer: str = ""
    model: str = ""
    services: List[str] = field(default_factory=list)
    open_ports: List[int] = field(default_factory=list)
    ttl: int = 0
    confidence: float = 0.0
    raw_data: Dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return asdict(self)


# Device type signatures based on open ports
PORT_SIGNATURES = {
    # Routers/Network Equipment
    'router': {
        'ports': [80, 443, 23, 22, 53, 67, 68],
        'required': [80],  # Must have at least one
        'weight': 0.6
    },
    'access_point': {
        'ports': [80, 443, 22],
        'required': [80],
        'weight': 0.5
    },
    'switch': {
        'ports': [80, 443, 22, 23, 161],
        'required': [161],  # SNMP common on managed switches
        'weight': 0.5
    },
    
    # Servers
    'web_server': {
        'ports': [80, 443, 8080, 8443],
        'required': [80, 443],
        'weight': 0.7
    },
    'file_server': {
        'ports': [445, 139, 21, 22, 2049],
        'required': [445],
        'weight': 0.6
    },
    'database_server': {
        'ports': [3306, 5432, 1433, 27017, 6379, 9200],
        'required': [],
        'weight': 0.8
    },
    'mail_server': {
        'ports': [25, 587, 993, 995, 143, 110],
        'required': [25],
        'weight': 0.8
    },
    
    # IoT/Smart Home
    'smart_tv': {
        'ports': [8008, 8443, 9000, 7000, 55000],
        'required': [8008],  # Chromecast port
        'weight': 0.7
    },
    'smart_speaker': {
        'ports': [8008, 8443, 10001],
        'required': [8008],
        'weight': 0.6
    },
    'ip_camera': {
        'ports': [80, 554, 8080, 8000],  # RTSP
        'required': [554],
        'weight': 0.8
    },
    'smart_plug': {
        'ports': [80, 9999],
        'required': [],
        'weight': 0.4
    },
    
    # Printers
    'printer': {
        'ports': [9100, 515, 631, 80],  # JetDirect, LPD, IPP
        'required': [9100],
        'weight': 0.9
    },
    
    # Gaming
    'gaming_console': {
        'ports': [3074, 3478, 3479, 3480],  # Xbox/PlayStation
        'required': [3074],
        'weight': 0.7
    },
    
    # Computers
    'windows_pc': {
        'ports': [135, 139, 445, 3389],
        'required': [445],
        'weight': 0.5
    },
    'linux_server': {
        'ports': [22],
        'required': [22],
        'weight': 0.3
    },
    'mac': {
        'ports': [22, 5900, 548, 88],  # SSH, VNC, AFP, Kerberos
        'required': [548],
        'weight': 0.6
    }
}

# TTL values for OS detection
TTL_SIGNATURES = {
    64: ['linux', 'macos', 'ios', 'android', 'freebsd'],
    128: ['windows'],
    255: ['cisco', 'network_device', 'solaris'],
    254: ['cisco', 'network_device'],
    63: ['linux'],  # Sometimes decremented
    127: ['windows'],  # Sometimes decremented
}

# Vendor-based device type hints
VENDOR_DEVICE_HINTS = {
    # Networking
    'cisco': 'network_device',
    'ubiquiti': 'network_device',
    'netgear': 'router',
    'tp-link': 'router',
    'linksys': 'router',
    'asus': 'router',
    'd-link': 'router',
    'mikrotik': 'router',
    'aruba': 'access_point',
    'ruckus': 'access_point',
    'meraki': 'network_device',
    'juniper': 'network_device',
    'fortinet': 'firewall',
    'palo alto': 'firewall',
    
    # Mobile
    'apple': 'apple_device',
    'samsung': 'mobile_device',
    'google': 'mobile_device',
    'huawei': 'mobile_device',
    'xiaomi': 'mobile_device',
    'oneplus': 'mobile_device',
    'oppo': 'mobile_device',
    'vivo': 'mobile_device',
    
    # IoT
    'amazon': 'smart_home',
    'ring': 'smart_home',
    'nest': 'smart_home',
    'philips': 'smart_home',
    'sonos': 'smart_speaker',
    'ecobee': 'thermostat',
    'wyze': 'ip_camera',
    'arlo': 'ip_camera',
    'hikvision': 'ip_camera',
    'dahua': 'ip_camera',
    
    # Computers
    'dell': 'computer',
    'hp': 'computer',
    'lenovo': 'computer',
    'intel': 'computer',
    'realtek': 'computer',
    'microsoft': 'computer',
    
    # Printers
    'canon': 'printer',
    'epson': 'printer',
    'brother': 'printer',
    'xerox': 'printer',
    'lexmark': 'printer',
    
    # Gaming
    'sony': 'gaming_console',
    'nintendo': 'gaming_console',
    'valve': 'gaming_device',
    
    # Smart TV
    'lg': 'smart_tv',
    'vizio': 'smart_tv',
    'roku': 'streaming_device',
    'tivo': 'streaming_device',
}


class DeviceFingerprinter:
    """Fingerprint devices to determine type and OS"""
    
    def __init__(self, timeout: float = 1.0, max_threads: int = 20):
        self.timeout = timeout
        self.max_threads = max_threads
    
    def get_ttl(self, ip: str) -> int:
        """Get TTL from ping response"""
        try:
            if sys.platform == 'win32':
                output = subprocess.check_output(
                    ['ping', '-n', '1', '-w', str(int(self.timeout * 1000)), ip],
                    stderr=subprocess.DEVNULL,
                    text=True,
                    timeout=self.timeout + 1
                )
                match = re.search(r'TTL[=:](\d+)', output, re.IGNORECASE)
            else:
                output = subprocess.check_output(
                    ['ping', '-c', '1', '-W', str(int(self.timeout)), ip],
                    stderr=subprocess.DEVNULL,
                    text=True,
                    timeout=self.timeout + 1
                )
                match = re.search(r'ttl[=:]?\s*(\d+)', output, re.IGNORECASE)
            
            if match:
                return int(match.group(1))
        except Exception:
            pass
        
        return 0
    
    def check_port(self, ip: str, port: int) -> bool:
        """Check if a port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def scan_common_ports(self, ip: str) -> List[int]:
        """Scan common ports for device identification"""
        common_ports = [
            21, 22, 23, 25, 53, 67, 68, 80, 110, 135, 139, 143, 443, 445,
            515, 548, 554, 587, 631, 993, 995, 1433, 1521, 2049, 3074,
            3306, 3389, 3478, 5432, 5900, 6379, 7000, 8000, 8008, 8080,
            8443, 9000, 9100, 9200, 9999, 10001, 27017, 55000
        ]
        
        open_ports = []
        
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = {executor.submit(self.check_port, ip, port): port for port in common_ports}
            
            for future in as_completed(futures):
                port = futures[future]
                try:
                    if future.result():
                        open_ports.append(port)
                except Exception:
                    pass
        
        return sorted(open_ports)
    
    def guess_os_from_ttl(self, ttl: int) -> Tuple[str, float]:
        """Guess OS family from TTL value"""
        # Normalize TTL to common starting values
        if ttl > 0:
            # Find the nearest starting TTL
            if ttl <= 64:
                normalized = 64
            elif ttl <= 128:
                normalized = 128
            else:
                normalized = 255
            
            os_list = TTL_SIGNATURES.get(normalized, [])
            if os_list:
                return os_list[0], 0.6
        
        return "", 0.0
    
    def match_port_signature(self, open_ports: List[int]) -> List[Tuple[str, float]]:
        """Match open ports against known signatures"""
        matches = []
        open_set = set(open_ports)
        
        for device_type, sig in PORT_SIGNATURES.items():
            sig_ports = set(sig['ports'])
            required = set(sig.get('required', []))
            weight = sig.get('weight', 0.5)
            
            # Check if required ports are present
            if required and not required.issubset(open_set):
                continue
            
            # Calculate match score
            matched = len(open_set & sig_ports)
            if matched > 0:
                score = (matched / len(sig_ports)) * weight
                matches.append((device_type, score))
        
        # Sort by score
        return sorted(matches, key=lambda x: x[1], reverse=True)
    
    def guess_from_vendor(self, vendor: str) -> Tuple[str, float]:
        """Guess device type from vendor name"""
        if not vendor:
            return "", 0.0
        
        vendor_lower = vendor.lower()
        
        for keyword, device_type in VENDOR_DEVICE_HINTS.items():
            if keyword in vendor_lower:
                return device_type, 0.4
        
        return "", 0.0
    
    def fingerprint(self, ip: str, mac: str = "", vendor: str = "", 
                   scan_ports: bool = True) -> DeviceFingerprint:
        """
        Generate complete fingerprint for a device
        
        Args:
            ip: Device IP address
            mac: MAC address (optional)
            vendor: Known vendor (optional)
            scan_ports: Whether to scan ports
        
        Returns:
            DeviceFingerprint with type, OS, and confidence
        """
        fp = DeviceFingerprint(ip=ip, mac=mac, manufacturer=vendor)
        
        # Get TTL
        fp.ttl = self.get_ttl(ip)
        
        # Scan ports if requested
        if scan_ports:
            fp.open_ports = self.scan_common_ports(ip)
        
        # Identify services from ports
        fp.services = self._identify_services(fp.open_ports)
        
        # Calculate scores from different sources
        scores: Dict[str, float] = {}
        
        # TTL-based OS guess
        os_guess, os_conf = self.guess_os_from_ttl(fp.ttl)
        if os_guess:
            fp.os_family = os_guess
            scores['os_ttl'] = os_conf
        
        # Port-based device type
        port_matches = self.match_port_signature(fp.open_ports)
        if port_matches:
            best_match, port_score = port_matches[0]
            scores['ports'] = port_score
            
            # Use port-based type if confident enough
            if port_score > 0.3:
                fp.device_type = best_match
        
        # Vendor-based hints
        vendor_type, vendor_score = self.guess_from_vendor(vendor)
        if vendor_type:
            scores['vendor'] = vendor_score
            
            # Override or confirm type
            if not fp.device_type or vendor_score > scores.get('ports', 0):
                fp.device_type = vendor_type
        
        # Refine device type based on OS
        fp.device_type = self._refine_type(fp)
        
        # Calculate overall confidence
        if scores:
            fp.confidence = min(sum(scores.values()) / len(scores) + 0.2, 1.0)
        else:
            fp.confidence = 0.1
        
        # Store raw data
        fp.raw_data = {
            'scores': scores,
            'port_matches': port_matches[:3] if port_matches else []
        }
        
        return fp
    
    def _identify_services(self, ports: List[int]) -> List[str]:
        """Identify services from port numbers"""
        port_services = {
            21: 'ftp', 22: 'ssh', 23: 'telnet', 25: 'smtp',
            53: 'dns', 67: 'dhcp', 80: 'http', 110: 'pop3',
            135: 'msrpc', 139: 'netbios', 143: 'imap', 443: 'https',
            445: 'smb', 515: 'lpd', 548: 'afp', 554: 'rtsp',
            631: 'ipp', 993: 'imaps', 995: 'pop3s', 1433: 'mssql',
            3306: 'mysql', 3389: 'rdp', 5432: 'postgresql',
            5900: 'vnc', 6379: 'redis', 8080: 'http-alt',
            9100: 'jetdirect', 27017: 'mongodb'
        }
        
        return [port_services.get(p, f'port-{p}') for p in ports if p in port_services]
    
    def _refine_type(self, fp: DeviceFingerprint) -> str:
        """Refine device type based on all available data"""
        device_type = fp.device_type or 'unknown'
        
        # Refine Apple devices
        if device_type == 'apple_device':
            if 548 in fp.open_ports:  # AFP
                return 'mac'
            elif fp.os_family == 'ios':
                return 'iphone'
            else:
                return 'apple_device'
        
        # Refine mobile devices
        if device_type == 'mobile_device':
            if fp.os_family == 'android':
                return 'android_phone'
            return 'mobile_device'
        
        # Refine computers
        if device_type == 'computer':
            if 3389 in fp.open_ports or 445 in fp.open_ports:
                return 'windows_pc'
            elif 22 in fp.open_ports and 548 not in fp.open_ports:
                return 'linux_pc'
            return 'computer'
        
        # Network devices with HTTP
        if device_type in ('router', 'network_device'):
            if 53 in fp.open_ports:
                return 'router'
            elif 161 in fp.open_ports:
                return 'managed_switch'
        
        return device_type
    
    def fingerprint_batch(self, devices: List[Dict], scan_ports: bool = True) -> List[DeviceFingerprint]:
        """
        Fingerprint multiple devices
        
        Args:
            devices: List of dicts with 'ip', 'mac', 'vendor' keys
            scan_ports: Whether to scan ports
        
        Returns:
            List of DeviceFingerprint objects
        """
        results = []
        
        for device in devices:
            fp = self.fingerprint(
                ip=device.get('ip', ''),
                mac=device.get('mac', ''),
                vendor=device.get('vendor', ''),
                scan_ports=scan_ports
            )
            results.append(fp)
        
        return results


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Device Fingerprinting - Identify device types and OS',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python fingerprint.py 192.168.1.1
  python fingerprint.py --target 192.168.1.1 --mac AA:BB:CC:DD:EE:FF --verbose
  python fingerprint.py --scan-network --verbose
  python fingerprint.py --input devices.json --output fingerprints.json
  python fingerprint.py --summary
  python fingerprint.py --export fingerprints.json
        '''
    )
    
    parser.add_argument('target', nargs='?', help='Target IP address (positional)')
    parser.add_argument('--target', dest='target_opt', help='Target IP address')
    parser.add_argument('--mac', '-m', help='MAC address')
    parser.add_argument('--vendor', help='Known vendor')
    parser.add_argument('--input', '-i', metavar='FILE',
                       help='Input JSON file with devices')
    parser.add_argument('--output', '-o', metavar='FILE',
                       help='Output file')
    parser.add_argument('--export', metavar='FILE',
                       help='Export fingerprint database to file')
    parser.add_argument('--scan-network', action='store_true',
                       help='Scan and fingerprint entire local network')
    parser.add_argument('--summary', action='store_true',
                       help='Show device type summary from database')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--no-ports', action='store_true',
                       help='Skip port scanning')
    parser.add_argument('--timeout', '-t', type=float, default=1.0,
                       help='Port scan timeout (default: 1.0s)')
    parser.add_argument('--json', '-j', action='store_true',
                       help='Output as JSON')
    parser.add_argument('--threads', type=int, default=20,
                       help='Max threads for port scanning')
    
    args = parser.parse_args()
    
    # Handle --target option (takes precedence over positional)
    target = args.target_opt or args.target
    
    fingerprinter = DeviceFingerprinter(
        timeout=args.timeout,
        max_threads=args.threads
    )
    
    results = []
    
    # Handle --summary option
    if args.summary:
        print("📊 Device Type Summary")
        print("=" * 50)
        print("(Run --scan-network to populate)")
        print("\nDevice type detection is performed on-demand.")
        print("Use --scan-network to scan and fingerprint all devices.")
        return 0
    
    # Handle --export option
    if args.export:
        output = {
            'fingerprints': [],
            'summary': {
                'note': 'Run --scan-network first to populate'
            }
        }
        with open(args.export, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"✅ Exported to {args.export}")
        return 0
    
    # Handle --scan-network option
    if args.scan_network:
        print("🔍 Scanning network for devices...", file=sys.stderr)
        
        # Get local network
        try:
            import netifaces
            gws = netifaces.gateways()
            default_iface = gws['default'][netifaces.AF_INET][1]
            addrs = netifaces.ifaddresses(default_iface)
            ip_info = addrs[netifaces.AF_INET][0]
            local_ip = ip_info['addr']
            netmask = ip_info['netmask']
            
            # Calculate network
            ip_parts = [int(x) for x in local_ip.split('.')]
            mask_parts = [int(x) for x in netmask.split('.')]
            network = '.'.join(str(ip_parts[i] & mask_parts[i]) for i in range(4))
            
            # Simple /24 scan
            base = '.'.join(network.split('.')[:3])
            targets = [f"{base}.{i}" for i in range(1, 255)]
        except:
            # Fallback to common network
            print("  Using fallback network 192.168.1.0/24", file=sys.stderr)
            targets = [f"192.168.1.{i}" for i in range(1, 255)]
        
        # Quick ping scan first
        live_hosts = []
        if args.verbose:
            print(f"  Pinging {len(targets)} hosts...", file=sys.stderr)
        
        def ping_host(ip):
            try:
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', '1', ip],
                    capture_output=True, timeout=2
                )
                return ip if result.returncode == 0 else None
            except:
                return None
        
        with ThreadPoolExecutor(max_workers=50) as executor:
            for result in executor.map(ping_host, targets):
                if result:
                    live_hosts.append(result)
        
        print(f"  Found {len(live_hosts)} live hosts", file=sys.stderr)
        
        # Fingerprint each
        for i, ip in enumerate(live_hosts):
            if args.verbose:
                print(f"  [{i+1}/{len(live_hosts)}] Fingerprinting {ip}...", file=sys.stderr)
            fp = fingerprinter.fingerprint(
                ip=ip,
                scan_ports=not args.no_ports
            )
            results.append(fp)
    
    elif args.input:
        # Batch mode from file
        with open(args.input, 'r') as f:
            data = json.load(f)
        
        devices = data.get('devices', data) if isinstance(data, dict) else data
        
        print(f"Fingerprinting {len(devices)} devices...", file=sys.stderr)
        
        for i, device in enumerate(devices):
            if args.verbose:
                print(f"  [{i+1}/{len(devices)}] {device.get('ip', 'unknown')}...", file=sys.stderr)
            fp = fingerprinter.fingerprint(
                ip=device.get('ip', ''),
                mac=device.get('mac', ''),
                vendor=device.get('vendor', ''),
                scan_ports=not args.no_ports
            )
            results.append(fp)
    
    elif target:
        # Single target
        if args.verbose:
            print(f"Fingerprinting {target}...", file=sys.stderr)
        fp = fingerprinter.fingerprint(
            ip=target,
            mac=args.mac or '',
            vendor=args.vendor or '',
            scan_ports=not args.no_ports
        )
        results.append(fp)
    
    else:
        parser.print_help()
        return 1
    
    # Output results
    if args.json or args.output:
        output = {
            'fingerprints': [fp.to_dict() for fp in results]
        }
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(output, f, indent=2)
            print(f"Results saved to {args.output}", file=sys.stderr)
        else:
            print(json.dumps(output, indent=2))
    
    else:
        # Pretty print
        for fp in results:
            print(f"\n{'='*60}")
            print(f"IP: {fp.ip}")
            if fp.mac:
                print(f"MAC: {fp.mac}")
            print(f"Device Type: {fp.device_type}")
            if fp.device_subtype:
                print(f"Subtype: {fp.device_subtype}")
            if fp.os_family:
                print(f"OS Family: {fp.os_family}")
            if fp.manufacturer:
                print(f"Manufacturer: {fp.manufacturer}")
            print(f"TTL: {fp.ttl}")
            if fp.open_ports:
                print(f"Open Ports: {', '.join(map(str, fp.open_ports))}")
            if fp.services:
                print(f"Services: {', '.join(fp.services)}")
            print(f"Confidence: {fp.confidence:.0%}")
            print('='*60)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
