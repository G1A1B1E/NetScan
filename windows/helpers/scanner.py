#!/usr/bin/env python3
"""
NetScan Windows Scanner Module
Cross-platform network scanning with Windows-specific optimizations
"""

import subprocess
import re
import socket
import sys
import json
import os
import concurrent.futures
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Constants
MAC_REGEX = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$|^([0-9A-Fa-f]{2}-){5}([0-9A-Fa-f]{2})$')
IP_REGEX = re.compile(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')


def normalize_mac(mac: str) -> str:
    """Normalize MAC address to XX:XX:XX:XX:XX:XX format"""
    # Remove all separators and convert to uppercase
    clean = re.sub(r'[-:.]', '', mac.upper())
    if len(clean) != 12:
        return mac
    # Format with colons
    return ':'.join(clean[i:i+2] for i in range(0, 12, 2))


def get_arp_table() -> List[Dict[str, str]]:
    """Get ARP table from Windows using arp -a command"""
    results = []
    
    try:
        # Run arp -a command
        output = subprocess.check_output(
            ['arp', '-a'],
            stderr=subprocess.DEVNULL,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        
        # Parse Windows ARP output
        # Format: IP Address      Physical Address      Type
        #         192.168.1.1     00-11-22-33-44-55     dynamic
        
        current_interface = None
        for line in output.splitlines():
            line = line.strip()
            
            # Check for interface header
            if line.startswith('Interface:'):
                match = re.search(r'Interface:\s+([\d.]+)', line)
                if match:
                    current_interface = match.group(1)
                continue
            
            # Parse entry line
            parts = line.split()
            if len(parts) >= 2:
                ip = parts[0]
                mac = parts[1]
                entry_type = parts[2] if len(parts) > 2 else 'unknown'
                
                # Validate IP and MAC
                if IP_REGEX.match(ip) and MAC_REGEX.match(mac):
                    # Skip broadcast/multicast
                    if mac.lower() in ['ff-ff-ff-ff-ff-ff', 'ff:ff:ff:ff:ff:ff']:
                        continue
                    
                    results.append({
                        'ip': ip,
                        'mac': normalize_mac(mac),
                        'type': entry_type,
                        'interface': current_interface
                    })
    
    except subprocess.CalledProcessError as e:
        print(f"Error running arp command: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Error parsing ARP table: {e}", file=sys.stderr)
    
    return results


def get_local_ip() -> Optional[str]:
    """Get local IP address of this machine"""
    try:
        # Create a socket to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return None


def get_network_info() -> Dict:
    """Get network interface information on Windows"""
    info = {
        'local_ip': get_local_ip(),
        'interfaces': []
    }
    
    try:
        # Use ipconfig to get interface details
        output = subprocess.check_output(
            ['ipconfig', '/all'],
            stderr=subprocess.DEVNULL,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        
        current_interface = {}
        for line in output.splitlines():
            line = line.rstrip()
            
            # New adapter section
            if line and not line.startswith(' ') and ':' in line:
                if current_interface.get('name'):
                    info['interfaces'].append(current_interface)
                current_interface = {'name': line.rstrip(':')}
            
            # Parse adapter properties
            elif current_interface:
                if 'IPv4 Address' in line:
                    match = re.search(r':\s*([\d.]+)', line)
                    if match:
                        current_interface['ip'] = match.group(1).rstrip('(Preferred)')
                elif 'Physical Address' in line:
                    match = re.search(r':\s*([0-9A-Fa-f-]+)', line)
                    if match:
                        current_interface['mac'] = normalize_mac(match.group(1))
                elif 'Default Gateway' in line:
                    match = re.search(r':\s*([\d.]+)', line)
                    if match:
                        current_interface['gateway'] = match.group(1)
                elif 'Subnet Mask' in line:
                    match = re.search(r':\s*([\d.]+)', line)
                    if match:
                        current_interface['subnet'] = match.group(1)
        
        # Add last interface
        if current_interface.get('name'):
            info['interfaces'].append(current_interface)
        
        # Filter to only interfaces with IPs
        info['interfaces'] = [i for i in info['interfaces'] if i.get('ip')]
        
    except Exception as e:
        print(f"Error getting network info: {e}", file=sys.stderr)
    
    return info


def ping_host(ip: str, timeout: float = 1.0) -> bool:
    """Ping a single host to check if it's alive"""
    try:
        # Windows ping with timeout
        timeout_ms = int(timeout * 1000)
        result = subprocess.run(
            ['ping', '-n', '1', '-w', str(timeout_ms), ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        return result.returncode == 0
    except Exception:
        return False


def scan_network(target: Optional[str] = None, timeout: float = 2.0, threads: int = 50) -> List[Dict]:
    """
    Scan network for active hosts
    
    Args:
        target: IP range to scan (e.g., "192.168.1.0/24") or None for auto-detect
        timeout: Timeout per host in seconds
        threads: Number of concurrent threads
    
    Returns:
        List of discovered hosts with IP, MAC, and optional hostname
    """
    results = []
    
    # Check if nmap is available for better scanning
    nmap_available = check_nmap()
    
    if nmap_available and target:
        results = scan_with_nmap(target, timeout)
    else:
        # Use ARP table + ping sweep
        if not target:
            # Auto-detect target range
            local_ip = get_local_ip()
            if local_ip:
                # Assume /24 network
                parts = local_ip.split('.')
                target = f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
        
        if target:
            results = ping_sweep(target, timeout, threads)
        
        # Enrich with ARP data
        arp_table = {entry['ip']: entry for entry in get_arp_table()}
        for result in results:
            if result['ip'] in arp_table:
                result['mac'] = arp_table[result['ip']]['mac']
    
    return results


def ping_sweep(target: str, timeout: float = 1.0, threads: int = 50) -> List[Dict]:
    """Perform ping sweep on target range"""
    results = []
    
    # Parse CIDR notation
    if '/' in target:
        base_ip, cidr = target.split('/')
        cidr = int(cidr)
    else:
        base_ip = target
        cidr = 32
    
    # Calculate IP range
    parts = list(map(int, base_ip.split('.')))
    base_int = (parts[0] << 24) + (parts[1] << 16) + (parts[2] << 8) + parts[3]
    
    num_hosts = 2 ** (32 - cidr)
    network_int = base_int & (0xFFFFFFFF << (32 - cidr))
    
    ips_to_scan = []
    for i in range(1, num_hosts - 1):  # Skip network and broadcast
        ip_int = network_int + i
        ip = f"{(ip_int >> 24) & 0xFF}.{(ip_int >> 16) & 0xFF}.{(ip_int >> 8) & 0xFF}.{ip_int & 0xFF}"
        ips_to_scan.append(ip)
    
    # Parallel ping
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        future_to_ip = {executor.submit(ping_host, ip, timeout): ip for ip in ips_to_scan}
        
        for future in concurrent.futures.as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                if future.result():
                    hostname = resolve_hostname(ip)
                    results.append({
                        'ip': ip,
                        'mac': '',
                        'hostname': hostname,
                        'status': 'up'
                    })
            except Exception:
                pass
    
    return sorted(results, key=lambda x: list(map(int, x['ip'].split('.'))))


def check_nmap() -> bool:
    """Check if nmap is available"""
    try:
        subprocess.run(
            ['nmap', '--version'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        return True
    except Exception:
        return False


def scan_with_nmap(target: str, timeout: float = 30.0) -> List[Dict]:
    """Use nmap for network scanning"""
    results = []
    
    try:
        # nmap ping scan with MAC addresses
        output = subprocess.check_output(
            ['nmap', '-sn', '-T4', '--max-retries', '1', target],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        
        current_host = {}
        for line in output.splitlines():
            if 'Nmap scan report for' in line:
                if current_host.get('ip'):
                    results.append(current_host)
                
                # Parse IP and optional hostname
                match = re.search(r'for\s+(?:(\S+)\s+\()?([\d.]+)\)?', line)
                if match:
                    hostname = match.group(1) if match.group(1) else ''
                    ip = match.group(2)
                    current_host = {'ip': ip, 'hostname': hostname, 'mac': '', 'status': 'up'}
            
            elif 'MAC Address:' in line:
                match = re.search(r'MAC Address:\s*([0-9A-Fa-f:]+)', line)
                if match:
                    current_host['mac'] = normalize_mac(match.group(1))
        
        if current_host.get('ip'):
            results.append(current_host)
    
    except subprocess.TimeoutExpired:
        print("Nmap scan timed out", file=sys.stderr)
    except Exception as e:
        print(f"Nmap scan error: {e}", file=sys.stderr)
    
    return results


def resolve_hostname(ip: str) -> str:
    """Resolve IP to hostname"""
    try:
        hostname = socket.gethostbyaddr(ip)[0]
        return hostname
    except Exception:
        return ''


def scan_ports(target: str, ports: str = "22,80,443,3389,445,139") -> List[Dict]:
    """
    Scan ports on target host
    
    Args:
        target: IP address to scan
        ports: Comma-separated list of ports or range (e.g., "1-1000")
    
    Returns:
        List of open ports with service info
    """
    results = []
    
    # Parse port specification
    port_list = []
    for part in ports.split(','):
        if '-' in part:
            start, end = map(int, part.split('-'))
            port_list.extend(range(start, end + 1))
        else:
            port_list.append(int(part))
    
    # Check if nmap available for better results
    if check_nmap():
        return scan_ports_nmap(target, ports)
    
    # Native port scanning
    def check_port(port: int) -> Optional[Dict]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1.0)
            result = sock.connect_ex((target, port))
            sock.close()
            
            if result == 0:
                service = get_service_name(port)
                return {'port': port, 'state': 'open', 'service': service}
        except Exception:
            pass
        return None
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(check_port, port): port for port in port_list}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
    
    return sorted(results, key=lambda x: x['port'])


def scan_ports_nmap(target: str, ports: str) -> List[Dict]:
    """Use nmap for port scanning"""
    results = []
    
    try:
        output = subprocess.check_output(
            ['nmap', '-Pn', '-T4', '-p', ports, target],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=60,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        
        for line in output.splitlines():
            match = re.match(r'(\d+)/tcp\s+(\w+)\s+(.+)', line)
            if match:
                results.append({
                    'port': int(match.group(1)),
                    'state': match.group(2),
                    'service': match.group(3).strip()
                })
    
    except Exception as e:
        print(f"Nmap port scan error: {e}", file=sys.stderr)
    
    return results


def get_service_name(port: int) -> str:
    """Get common service name for port"""
    common_ports = {
        20: 'ftp-data', 21: 'ftp', 22: 'ssh', 23: 'telnet',
        25: 'smtp', 53: 'dns', 67: 'dhcp', 68: 'dhcp',
        80: 'http', 110: 'pop3', 119: 'nntp', 123: 'ntp',
        139: 'netbios', 143: 'imap', 161: 'snmp', 194: 'irc',
        443: 'https', 445: 'smb', 465: 'smtps', 514: 'syslog',
        587: 'submission', 631: 'ipp', 993: 'imaps', 995: 'pop3s',
        1433: 'mssql', 1521: 'oracle', 3306: 'mysql', 3389: 'rdp',
        5432: 'postgresql', 5900: 'vnc', 6379: 'redis', 8080: 'http-alt',
        8443: 'https-alt', 27017: 'mongodb'
    }
    return common_ports.get(port, 'unknown')


# CLI Interface
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='NetScan Network Scanner')
    parser.add_argument('--arp', action='store_true', help='Show ARP table')
    parser.add_argument('--scan', '-s', metavar='TARGET', nargs='?', const='auto',
                       help='Scan network (e.g., 192.168.1.0/24)')
    parser.add_argument('--ports', '-p', metavar='TARGET', help='Scan ports on target')
    parser.add_argument('--port-list', default='22,80,443,3389,445,139',
                       help='Ports to scan (default: common ports)')
    parser.add_argument('--info', action='store_true', help='Show network info')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')
    parser.add_argument('--timeout', '-t', type=float, default=2.0, help='Timeout in seconds')
    parser.add_argument('--threads', type=int, default=50, help='Number of threads')
    
    args = parser.parse_args()
    
    # Network info
    if args.info:
        info = get_network_info()
        if args.json:
            print(json.dumps(info, indent=2))
        else:
            print(f"\nLocal IP: {info['local_ip']}\n")
            print("Network Interfaces:")
            for iface in info['interfaces']:
                print(f"  {iface['name']}")
                if iface.get('ip'):
                    print(f"    IP: {iface['ip']}")
                if iface.get('mac'):
                    print(f"    MAC: {iface['mac']}")
                if iface.get('gateway'):
                    print(f"    Gateway: {iface['gateway']}")
        return
    
    # ARP table
    if args.arp:
        entries = get_arp_table()
        if args.json:
            print(json.dumps(entries, indent=2))
        else:
            print(f"\nARP Table ({len(entries)} entries):\n")
            print(f"{'IP Address':<16} {'MAC Address':<18} {'Type':<10}")
            print("-" * 46)
            for entry in entries:
                print(f"{entry['ip']:<16} {entry['mac']:<18} {entry['type']:<10}")
        return
    
    # Network scan
    if args.scan:
        target = None if args.scan == 'auto' else args.scan
        print(f"Scanning {'network' if not target else target}...", file=sys.stderr)
        
        results = scan_network(target, args.timeout, args.threads)
        
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"\nDiscovered {len(results)} hosts:\n")
            print(f"{'IP Address':<16} {'MAC Address':<18} {'Hostname':<30}")
            print("-" * 66)
            for host in results:
                print(f"{host['ip']:<16} {host.get('mac', 'N/A'):<18} {host.get('hostname', ''):<30}")
        return
    
    # Port scan
    if args.ports:
        print(f"Scanning ports on {args.ports}...", file=sys.stderr)
        results = scan_ports(args.ports, args.port_list)
        
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"\nOpen ports on {args.ports}:\n")
            print(f"{'Port':<8} {'State':<10} {'Service':<20}")
            print("-" * 40)
            for port in results:
                print(f"{port['port']:<8} {port['state']:<10} {port['service']:<20}")
        return
    
    # Default: show help
    parser.print_help()


if __name__ == '__main__':
    main()
