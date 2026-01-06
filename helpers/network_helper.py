#!/usr/bin/env python3
"""
Network Helper - Fast network operations for IP/CIDR handling
Provides IP validation, CIDR expansion, subnet calculations
"""

import sys
import argparse
import ipaddress
from typing import List, Optional, Tuple, Iterator
import json


def is_valid_ip(ip: str) -> bool:
    """Check if string is a valid IP address (v4 or v6)"""
    try:
        ipaddress.ip_address(ip.strip())
        return True
    except ValueError:
        return False


def is_valid_ipv4(ip: str) -> bool:
    """Check if string is a valid IPv4 address"""
    try:
        addr = ipaddress.ip_address(ip.strip())
        return isinstance(addr, ipaddress.IPv4Address)
    except ValueError:
        return False


def is_valid_ipv6(ip: str) -> bool:
    """Check if string is a valid IPv6 address"""
    try:
        addr = ipaddress.ip_address(ip.strip())
        return isinstance(addr, ipaddress.IPv6Address)
    except ValueError:
        return False


def is_valid_cidr(cidr: str) -> bool:
    """Check if string is a valid CIDR notation"""
    try:
        ipaddress.ip_network(cidr.strip(), strict=False)
        return True
    except ValueError:
        return False


def parse_cidr(cidr: str) -> Optional[dict]:
    """Parse CIDR notation and return network info"""
    try:
        network = ipaddress.ip_network(cidr.strip(), strict=False)
        return {
            'network': str(network.network_address),
            'broadcast': str(network.broadcast_address) if hasattr(network, 'broadcast_address') else None,
            'netmask': str(network.netmask),
            'hostmask': str(network.hostmask),
            'prefix_length': network.prefixlen,
            'num_addresses': network.num_addresses,
            'first_host': str(list(network.hosts())[0]) if network.num_addresses > 2 else None,
            'last_host': str(list(network.hosts())[-1]) if network.num_addresses > 2 else None,
            'is_private': network.is_private,
            'is_global': network.is_global,
            'is_multicast': network.is_multicast,
            'is_loopback': network.is_loopback,
            'version': network.version,
        }
    except ValueError:
        return None


def expand_cidr(cidr: str, hosts_only: bool = True) -> Iterator[str]:
    """
    Expand CIDR notation to list of IP addresses
    
    Args:
        cidr: CIDR notation (e.g., 192.168.1.0/24)
        hosts_only: If True, exclude network and broadcast addresses
    
    Yields:
        IP addresses in the network
    """
    try:
        network = ipaddress.ip_network(cidr.strip(), strict=False)
        if hosts_only:
            for host in network.hosts():
                yield str(host)
        else:
            for addr in network:
                yield str(addr)
    except ValueError:
        pass


def get_network_for_ip(ip: str, prefix: int = 24) -> Optional[str]:
    """Get network address for an IP with given prefix length"""
    try:
        addr = ipaddress.ip_address(ip.strip())
        network = ipaddress.ip_network(f"{ip}/{prefix}", strict=False)
        return str(network)
    except ValueError:
        return None


def ip_in_network(ip: str, cidr: str) -> bool:
    """Check if IP address is within a CIDR network"""
    try:
        addr = ipaddress.ip_address(ip.strip())
        network = ipaddress.ip_network(cidr.strip(), strict=False)
        return addr in network
    except ValueError:
        return False


def calculate_subnet(base_network: str, new_prefix: int) -> List[str]:
    """Calculate subnets from a base network"""
    try:
        network = ipaddress.ip_network(base_network.strip(), strict=False)
        return [str(subnet) for subnet in network.subnets(new_prefix=new_prefix)]
    except ValueError:
        return []


def summarize_networks(networks: List[str]) -> List[str]:
    """Summarize multiple networks into smallest possible list"""
    try:
        parsed = [ipaddress.ip_network(n.strip(), strict=False) for n in networks]
        collapsed = list(ipaddress.collapse_addresses(parsed))
        return [str(net) for net in collapsed]
    except ValueError:
        return networks


def ip_range_to_cidr(start_ip: str, end_ip: str) -> List[str]:
    """Convert IP range to list of CIDR networks"""
    try:
        start = ipaddress.ip_address(start_ip.strip())
        end = ipaddress.ip_address(end_ip.strip())
        return [str(net) for net in ipaddress.summarize_address_range(start, end)]
    except ValueError:
        return []


def get_ip_type(ip: str) -> dict:
    """Get detailed type information for an IP address"""
    try:
        addr = ipaddress.ip_address(ip.strip())
        return {
            'ip': str(addr),
            'version': addr.version,
            'is_private': addr.is_private,
            'is_global': addr.is_global,
            'is_multicast': addr.is_multicast,
            'is_loopback': addr.is_loopback,
            'is_link_local': addr.is_link_local,
            'is_reserved': addr.is_reserved,
            'is_unspecified': addr.is_unspecified,
        }
    except ValueError:
        return {'ip': ip, 'valid': False}


def compare_ips(ip1: str, ip2: str) -> int:
    """
    Compare two IP addresses
    Returns: -1 if ip1 < ip2, 0 if equal, 1 if ip1 > ip2
    """
    try:
        addr1 = ipaddress.ip_address(ip1.strip())
        addr2 = ipaddress.ip_address(ip2.strip())
        if addr1 < addr2:
            return -1
        elif addr1 > addr2:
            return 1
        return 0
    except ValueError:
        return 0


def sort_ips(ips: List[str]) -> List[str]:
    """Sort list of IP addresses"""
    valid = []
    invalid = []
    
    for ip in ips:
        try:
            valid.append((ipaddress.ip_address(ip.strip()), ip))
        except ValueError:
            invalid.append(ip)
    
    valid.sort(key=lambda x: x[0])
    return [ip for _, ip in valid] + invalid


def generate_ip_range(start: str, end: str) -> Iterator[str]:
    """Generate all IPs between start and end (inclusive)"""
    try:
        start_addr = ipaddress.ip_address(start.strip())
        end_addr = ipaddress.ip_address(end.strip())
        
        current = int(start_addr)
        end_int = int(end_addr)
        
        while current <= end_int:
            if start_addr.version == 4:
                yield str(ipaddress.IPv4Address(current))
            else:
                yield str(ipaddress.IPv6Address(current))
            current += 1
    except ValueError:
        pass


def get_common_private_ranges() -> List[dict]:
    """Get common private network ranges"""
    return [
        {'name': 'Class A Private', 'cidr': '10.0.0.0/8', 'range': '10.0.0.0 - 10.255.255.255'},
        {'name': 'Class B Private', 'cidr': '172.16.0.0/12', 'range': '172.16.0.0 - 172.31.255.255'},
        {'name': 'Class C Private', 'cidr': '192.168.0.0/16', 'range': '192.168.0.0 - 192.168.255.255'},
        {'name': 'Link Local', 'cidr': '169.254.0.0/16', 'range': '169.254.0.0 - 169.254.255.255'},
        {'name': 'Loopback', 'cidr': '127.0.0.0/8', 'range': '127.0.0.0 - 127.255.255.255'},
        {'name': 'CGNAT', 'cidr': '100.64.0.0/10', 'range': '100.64.0.0 - 100.127.255.255'},
    ]


def detect_network_from_ips(ips: List[str]) -> Optional[dict]:
    """Detect the common network from a list of IPs"""
    valid_ips = []
    for ip in ips:
        try:
            valid_ips.append(ipaddress.ip_address(ip.strip()))
        except ValueError:
            continue
    
    if not valid_ips:
        return None
    
    # Try to find smallest network containing all IPs
    for prefix in range(32, 0, -1):
        networks = set()
        for ip in valid_ips:
            net = ipaddress.ip_network(f"{ip}/{prefix}", strict=False)
            networks.add(str(net))
        
        if len(networks) == 1:
            return parse_cidr(list(networks)[0])
    
    return None


def main():
    parser = argparse.ArgumentParser(
        description='Network Helper - Fast IP/CIDR operations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --validate 192.168.1.1              # Validate IP
  %(prog)s --info 192.168.1.0/24               # Get network info
  %(prog)s --expand 192.168.1.0/29             # List all IPs in network
  %(prog)s --contains 192.168.1.100 192.168.1.0/24  # Check if IP in network
  %(prog)s --range 192.168.1.1 192.168.1.10    # Generate IP range
  %(prog)s --sort < ips.txt                    # Sort IPs from stdin
  %(prog)s --summarize 10.0.0.0/24 10.0.1.0/24 # Summarize networks
        """
    )
    
    parser.add_argument('args', nargs='*', help='IP addresses or CIDR notations')
    parser.add_argument('--validate', '-v', action='store_true',
                        help='Validate IP/CIDR (exit 0=valid, 1=invalid)')
    parser.add_argument('--info', '-i', action='store_true',
                        help='Show detailed network/IP info')
    parser.add_argument('--expand', '-e', action='store_true',
                        help='Expand CIDR to list of IPs')
    parser.add_argument('--hosts-only', action='store_true', default=True,
                        help='Exclude network/broadcast in expansion (default)')
    parser.add_argument('--all-addresses', action='store_true',
                        help='Include network/broadcast in expansion')
    parser.add_argument('--contains', '-c', action='store_true',
                        help='Check if first IP is in second CIDR')
    parser.add_argument('--range', '-r', action='store_true',
                        help='Generate IPs between two addresses')
    parser.add_argument('--sort', '-s', action='store_true',
                        help='Sort IPs from stdin')
    parser.add_argument('--summarize', action='store_true',
                        help='Summarize/collapse networks')
    parser.add_argument('--subnet', metavar='PREFIX',
                        help='Subnet network with new prefix')
    parser.add_argument('--json', '-j', action='store_true',
                        help='Output in JSON format')
    parser.add_argument('--private-ranges', action='store_true',
                        help='Show common private network ranges')
    parser.add_argument('--detect-network', action='store_true',
                        help='Detect common network from list of IPs')
    
    args = parser.parse_args()
    
    # Show private ranges
    if args.private_ranges:
        ranges = get_common_private_ranges()
        if args.json:
            print(json.dumps(ranges, indent=2))
        else:
            for r in ranges:
                print(f"{r['name']}: {r['cidr']} ({r['range']})")
        return 0
    
    # Sort IPs from stdin
    if args.sort:
        ips = [line.strip() for line in sys.stdin if line.strip()]
        sorted_ips = sort_ips(ips)
        for ip in sorted_ips:
            print(ip)
        return 0
    
    # Detect network from IPs
    if args.detect_network:
        ips = args.args if args.args else [line.strip() for line in sys.stdin if line.strip()]
        result = detect_network_from_ips(ips)
        if result:
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"Detected network: {result['network']}/{result['prefix_length']}")
        else:
            print("Could not detect common network", file=sys.stderr)
            return 1
        return 0
    
    # Check for required arguments
    if not args.args:
        parser.print_help()
        return 1
    
    # Validate
    if args.validate:
        target = args.args[0]
        if is_valid_ip(target) or is_valid_cidr(target):
            if not args.json:
                print("Valid")
            return 0
        else:
            if not args.json:
                print("Invalid", file=sys.stderr)
            return 1
    
    # Network/IP info
    if args.info:
        target = args.args[0]
        if '/' in target:
            result = parse_cidr(target)
        else:
            result = get_ip_type(target)
        
        if result:
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                for key, value in result.items():
                    print(f"{key}: {value}")
        else:
            print("Invalid input", file=sys.stderr)
            return 1
        return 0
    
    # Expand CIDR
    if args.expand:
        cidr = args.args[0]
        hosts_only = not args.all_addresses
        
        ips = list(expand_cidr(cidr, hosts_only))
        if args.json:
            print(json.dumps(ips))
        else:
            for ip in ips:
                print(ip)
        return 0
    
    # Check containment
    if args.contains:
        if len(args.args) < 2:
            print("Need IP and CIDR", file=sys.stderr)
            return 1
        
        ip, cidr = args.args[0], args.args[1]
        result = ip_in_network(ip, cidr)
        
        if args.json:
            print(json.dumps({'ip': ip, 'network': cidr, 'contains': result}))
        else:
            print("Yes" if result else "No")
        return 0 if result else 1
    
    # Generate range
    if args.range:
        if len(args.args) < 2:
            print("Need start and end IP", file=sys.stderr)
            return 1
        
        start, end = args.args[0], args.args[1]
        ips = list(generate_ip_range(start, end))
        
        if args.json:
            print(json.dumps(ips))
        else:
            for ip in ips:
                print(ip)
        return 0
    
    # Summarize networks
    if args.summarize:
        networks = args.args
        result = summarize_networks(networks)
        
        if args.json:
            print(json.dumps(result))
        else:
            for net in result:
                print(net)
        return 0
    
    # Subnet
    if args.subnet:
        base = args.args[0]
        new_prefix = int(args.subnet)
        result = calculate_subnet(base, new_prefix)
        
        if args.json:
            print(json.dumps(result))
        else:
            for subnet in result:
                print(subnet)
        return 0
    
    # Default: show info
    target = args.args[0]
    if '/' in target:
        result = parse_cidr(target)
    else:
        result = get_ip_type(target)
    
    if result:
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            for key, value in result.items():
                print(f"{key}: {value}")
    else:
        print("Invalid input", file=sys.stderr)
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
