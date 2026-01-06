#!/usr/bin/env python3
"""
Async Network Scanner - High-performance network discovery
Uses asyncio for concurrent scanning with multiple methods
"""

import asyncio
import subprocess
import sys
import argparse
import json
import ipaddress
import socket
import struct
import time
import re
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import os

# Try to import optional dependencies
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


@dataclass
class Device:
    """Represents a discovered network device"""
    ip: str
    mac: str = ""
    hostname: str = ""
    vendor: str = ""
    status: str = "up"
    response_time: float = 0.0
    discovery_method: str = ""
    first_seen: str = ""
    last_seen: str = ""
    ports: List[int] = None
    os_guess: str = ""
    
    def __post_init__(self):
        if self.ports is None:
            self.ports = []
        if not self.first_seen:
            self.first_seen = datetime.now().isoformat()
        if not self.last_seen:
            self.last_seen = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        return asdict(self)


class AsyncScanner:
    """Async network scanner with multiple discovery methods"""
    
    def __init__(self, timeout: float = 1.0, max_concurrent: int = 100, 
                 vendor_lookup: bool = True, verbose: bool = False):
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self.vendor_lookup = vendor_lookup
        self.verbose = verbose
        self.devices: Dict[str, Device] = {}
        self.semaphore = None
        self._vendor_cache: Dict[str, str] = {}
        self._executor = ThreadPoolExecutor(max_workers=20)
    
    def log(self, message: str):
        """Print verbose messages"""
        if self.verbose:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}", file=sys.stderr)
    
    # =========================================================================
    # CIDR Expansion
    # =========================================================================
    
    def expand_cidr(self, cidr: str, hosts_only: bool = True) -> List[str]:
        """Expand CIDR notation to list of IP addresses"""
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            if hosts_only:
                return [str(ip) for ip in network.hosts()]
            return [str(ip) for ip in network]
        except ValueError as e:
            self.log(f"Invalid CIDR: {cidr} - {e}")
            return []
    
    def expand_range(self, start_ip: str, end_ip: str) -> List[str]:
        """Expand IP range to list of addresses"""
        try:
            start = ipaddress.ip_address(start_ip)
            end = ipaddress.ip_address(end_ip)
            return [str(ipaddress.ip_address(ip)) 
                    for ip in range(int(start), int(end) + 1)]
        except ValueError as e:
            self.log(f"Invalid IP range: {e}")
            return []
    
    # =========================================================================
    # Ping Methods
    # =========================================================================
    
    async def ping_host(self, ip: str) -> Optional[Device]:
        """Ping a single host using system ping"""
        try:
            # Use system ping command
            if sys.platform == "darwin":
                cmd = ["ping", "-c", "1", "-W", str(int(self.timeout * 1000)), ip]
            else:
                cmd = ["ping", "-c", "1", "-W", str(int(self.timeout)), ip]
            
            async with self.semaphore:
                start_time = time.time()
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, _ = await asyncio.wait_for(
                    proc.communicate(), 
                    timeout=self.timeout + 1
                )
                response_time = (time.time() - start_time) * 1000
                
                if proc.returncode == 0:
                    return Device(
                        ip=ip,
                        status="up",
                        response_time=round(response_time, 2),
                        discovery_method="ping"
                    )
        except (asyncio.TimeoutError, Exception) as e:
            self.log(f"Ping failed for {ip}: {e}")
        return None
    
    async def ping_sweep(self, targets: List[str]) -> List[Device]:
        """Perform async ping sweep on multiple targets"""
        self.log(f"Starting ping sweep on {len(targets)} hosts...")
        self.semaphore = asyncio.Semaphore(self.max_concurrent)
        
        tasks = [self.ping_host(ip) for ip in targets]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        devices = []
        for result in results:
            if isinstance(result, Device):
                devices.append(result)
                self.devices[result.ip] = result
        
        self.log(f"Ping sweep complete: {len(devices)}/{len(targets)} hosts up")
        return devices
    
    # =========================================================================
    # ARP Methods
    # =========================================================================
    
    def get_arp_table(self) -> List[Device]:
        """Read current ARP table"""
        devices = []
        try:
            result = subprocess.run(
                ["arp", "-a"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Parse ARP output
            # Format: hostname (ip) at mac on interface
            pattern = r'(\S+)\s+\((\d+\.\d+\.\d+\.\d+)\)\s+at\s+([0-9a-fA-F:]+)'
            
            for line in result.stdout.splitlines():
                match = re.search(pattern, line)
                if match:
                    hostname, ip, mac = match.groups()
                    if mac != "(incomplete)" and mac != "ff:ff:ff:ff:ff:ff":
                        device = Device(
                            ip=ip,
                            mac=mac.lower(),
                            hostname=hostname if hostname != "?" else "",
                            discovery_method="arp"
                        )
                        devices.append(device)
                        self.devices[ip] = device
            
            self.log(f"Found {len(devices)} devices in ARP table")
        except Exception as e:
            self.log(f"ARP table read failed: {e}")
        
        return devices
    
    async def arp_scan(self, interface: str = None, targets: List[str] = None) -> List[Device]:
        """Use arp-scan if available for faster discovery"""
        devices = []
        
        # Check if arp-scan is available
        try:
            subprocess.run(["which", "arp-scan"], capture_output=True, check=True)
        except subprocess.CalledProcessError:
            self.log("arp-scan not available, falling back to ARP table")
            return self.get_arp_table()
        
        try:
            cmd = ["sudo", "arp-scan", "--localnet", "--quiet"]
            if interface:
                cmd.extend(["--interface", interface])
            
            self.log(f"Running arp-scan...")
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            
            # Parse arp-scan output
            # Format: IP\tMAC\tVendor
            for line in stdout.decode().splitlines():
                parts = line.split('\t')
                if len(parts) >= 2:
                    ip, mac = parts[0], parts[1]
                    if re.match(r'\d+\.\d+\.\d+\.\d+', ip):
                        vendor = parts[2] if len(parts) > 2 else ""
                        device = Device(
                            ip=ip,
                            mac=mac.lower(),
                            vendor=vendor,
                            discovery_method="arp-scan"
                        )
                        devices.append(device)
                        self.devices[ip] = device
            
            self.log(f"arp-scan found {len(devices)} devices")
        except Exception as e:
            self.log(f"arp-scan failed: {e}")
            return self.get_arp_table()
        
        return devices
    
    # =========================================================================
    # Port Scanning
    # =========================================================================
    
    async def check_port(self, ip: str, port: int) -> bool:
        """Check if a port is open"""
        try:
            async with self.semaphore:
                _, writer = await asyncio.wait_for(
                    asyncio.open_connection(ip, port),
                    timeout=self.timeout
                )
                writer.close()
                await writer.wait_closed()
                return True
        except:
            return False
    
    async def scan_ports(self, ip: str, ports: List[int]) -> List[int]:
        """Scan multiple ports on a host"""
        tasks = [self.check_port(ip, port) for port in ports]
        results = await asyncio.gather(*tasks)
        return [port for port, is_open in zip(ports, results) if is_open]
    
    async def service_discovery(self, targets: List[str], 
                                ports: List[int] = None) -> Dict[str, List[int]]:
        """Discover services on multiple hosts"""
        if ports is None:
            # Common ports
            ports = [22, 23, 25, 53, 80, 110, 143, 443, 445, 993, 995, 
                     3389, 5900, 8080, 8443]
        
        self.semaphore = asyncio.Semaphore(self.max_concurrent)
        self.log(f"Scanning {len(ports)} ports on {len(targets)} hosts...")
        
        results = {}
        for ip in targets:
            open_ports = await self.scan_ports(ip, ports)
            if open_ports:
                results[ip] = open_ports
                if ip in self.devices:
                    self.devices[ip].ports = open_ports
        
        self.log(f"Service discovery complete")
        return results
    
    # =========================================================================
    # Hostname Resolution
    # =========================================================================
    
    async def resolve_hostname(self, ip: str) -> str:
        """Resolve IP to hostname"""
        try:
            loop = asyncio.get_event_loop()
            hostname = await loop.run_in_executor(
                self._executor,
                lambda: socket.gethostbyaddr(ip)[0]
            )
            return hostname
        except:
            return ""
    
    async def resolve_hostnames(self, devices: List[Device]) -> List[Device]:
        """Resolve hostnames for multiple devices"""
        self.log(f"Resolving hostnames for {len(devices)} devices...")
        
        tasks = [self.resolve_hostname(d.ip) for d in devices]
        hostnames = await asyncio.gather(*tasks)
        
        for device, hostname in zip(devices, hostnames):
            if hostname and not device.hostname:
                device.hostname = hostname
        
        return devices
    
    # =========================================================================
    # Vendor Lookup
    # =========================================================================
    
    def lookup_vendor_sync(self, mac: str) -> str:
        """Synchronous vendor lookup"""
        if not mac or not HAS_REQUESTS:
            return ""
        
        # Check cache first
        oui = mac.replace(":", "").replace("-", "")[:6].lower()
        if oui in self._vendor_cache:
            return self._vendor_cache[oui]
        
        try:
            response = requests.get(
                f"https://api.macvendors.com/{mac}",
                timeout=2
            )
            if response.status_code == 200:
                vendor = response.text
                self._vendor_cache[oui] = vendor
                return vendor
        except:
            pass
        
        return ""
    
    async def lookup_vendor(self, mac: str) -> str:
        """Async vendor lookup"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self.lookup_vendor_sync,
            mac
        )
    
    async def lookup_vendors(self, devices: List[Device]) -> List[Device]:
        """Lookup vendors for multiple devices"""
        if not self.vendor_lookup:
            return devices
        
        self.log(f"Looking up vendors for {len(devices)} devices...")
        
        # Only lookup devices with MAC but no vendor
        devices_to_lookup = [d for d in devices if d.mac and not d.vendor]
        
        tasks = [self.lookup_vendor(d.mac) for d in devices_to_lookup]
        vendors = await asyncio.gather(*tasks)
        
        for device, vendor in zip(devices_to_lookup, vendors):
            if vendor:
                device.vendor = vendor
        
        return devices
    
    # =========================================================================
    # Full Scan Methods
    # =========================================================================
    
    async def quick_scan(self, cidr: str) -> List[Device]:
        """Quick scan using ARP and ping"""
        targets = self.expand_cidr(cidr)
        
        # Start with ARP table
        devices = self.get_arp_table()
        known_ips = {d.ip for d in devices}
        
        # Ping unknown hosts
        unknown_targets = [ip for ip in targets if ip not in known_ips]
        if unknown_targets:
            ping_results = await self.ping_sweep(unknown_targets)
            devices.extend(ping_results)
        
        # Resolve hostnames and vendors
        devices = await self.resolve_hostnames(devices)
        devices = await self.lookup_vendors(devices)
        
        return devices
    
    async def full_scan(self, cidr: str, ports: List[int] = None) -> List[Device]:
        """Full scan with service discovery"""
        # Start with quick scan
        devices = await self.quick_scan(cidr)
        
        # Service discovery
        if ports:
            await self.service_discovery([d.ip for d in devices], ports)
        
        return list(self.devices.values())
    
    async def stealth_scan(self, cidr: str) -> List[Device]:
        """Slower, less detectable scan"""
        targets = self.expand_cidr(cidr)
        
        # Reduce concurrency and add delays
        old_concurrent = self.max_concurrent
        self.max_concurrent = 10
        self.semaphore = asyncio.Semaphore(self.max_concurrent)
        
        devices = []
        for i, ip in enumerate(targets):
            if i > 0 and i % 10 == 0:
                await asyncio.sleep(1)  # Pause every 10 hosts
            
            result = await self.ping_host(ip)
            if result:
                devices.append(result)
                self.devices[ip] = result
        
        self.max_concurrent = old_concurrent
        
        # Resolve hostnames and vendors
        devices = await self.resolve_hostnames(devices)
        devices = await self.lookup_vendors(devices)
        
        return devices
    
    # =========================================================================
    # Output Methods
    # =========================================================================
    
    def get_results(self) -> List[Dict]:
        """Get all discovered devices as list of dicts"""
        return [d.to_dict() for d in self.devices.values()]
    
    def get_results_json(self, pretty: bool = True) -> str:
        """Get results as JSON string"""
        indent = 2 if pretty else None
        return json.dumps(self.get_results(), indent=indent, default=str)
    
    def get_summary(self) -> Dict:
        """Get scan summary"""
        devices = list(self.devices.values())
        vendors = {}
        for d in devices:
            v = d.vendor or "Unknown"
            vendors[v] = vendors.get(v, 0) + 1
        
        return {
            "total_devices": len(devices),
            "with_mac": sum(1 for d in devices if d.mac),
            "with_hostname": sum(1 for d in devices if d.hostname),
            "with_vendor": sum(1 for d in devices if d.vendor),
            "vendors": vendors,
            "scan_time": datetime.now().isoformat()
        }


# =============================================================================
# CLI Interface
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Async Network Scanner - High-performance network discovery',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s 192.168.1.0/24                    # Quick scan
  %(prog)s 192.168.1.0/24 --full             # Full scan with services
  %(prog)s 192.168.1.0/24 --stealth          # Slow stealth scan
  %(prog)s --arp                              # Just read ARP table
  %(prog)s 192.168.1.0/24 --expand           # Just expand CIDR
  %(prog)s 192.168.1.1-192.168.1.50 --ping   # Ping range
        """
    )
    
    parser.add_argument('target', nargs='?', help='Target CIDR, IP, or range')
    parser.add_argument('--full', '-f', action='store_true',
                        help='Full scan with service discovery')
    parser.add_argument('--stealth', '-s', action='store_true',
                        help='Stealth scan (slower, less detectable)')
    parser.add_argument('--ping', '-p', action='store_true',
                        help='Ping sweep only')
    parser.add_argument('--arp', '-a', action='store_true',
                        help='Read ARP table only')
    parser.add_argument('--expand', '-e', action='store_true',
                        help='Just expand CIDR to IP list')
    parser.add_argument('--ports', metavar='PORTS',
                        help='Ports to scan (comma-separated)')
    parser.add_argument('--timeout', '-t', type=float, default=1.0,
                        help='Timeout in seconds (default: 1.0)')
    parser.add_argument('--concurrent', '-c', type=int, default=100,
                        help='Max concurrent scans (default: 100)')
    parser.add_argument('--no-vendor', action='store_true',
                        help='Skip vendor lookup')
    parser.add_argument('--json', '-j', action='store_true',
                        help='Output as JSON')
    parser.add_argument('--summary', action='store_true',
                        help='Show scan summary')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    
    args = parser.parse_args()
    
    # Just expand CIDR
    if args.expand and args.target:
        scanner = AsyncScanner()
        if '-' in args.target and '/' not in args.target:
            # IP range
            start, end = args.target.split('-')
            if '.' not in end:
                # Short form: 192.168.1.1-50
                base = '.'.join(start.split('.')[:-1])
                end = f"{base}.{end}"
            ips = scanner.expand_range(start, end)
        else:
            ips = scanner.expand_cidr(args.target)
        
        for ip in ips:
            print(ip)
        return 0
    
    # Create scanner
    scanner = AsyncScanner(
        timeout=args.timeout,
        max_concurrent=args.concurrent,
        vendor_lookup=not args.no_vendor,
        verbose=args.verbose
    )
    
    # Parse ports
    ports = None
    if args.ports:
        ports = [int(p.strip()) for p in args.ports.split(',')]
    
    # Run scan
    async def run_scan():
        if args.arp:
            return scanner.get_arp_table()
        
        if not args.target:
            parser.print_help()
            return []
        
        # Parse target
        if '-' in args.target and '/' not in args.target:
            # IP range
            start, end = args.target.split('-')
            if '.' not in end:
                base = '.'.join(start.split('.')[:-1])
                end = f"{base}.{end}"
            targets = scanner.expand_range(start, end)
        else:
            targets = scanner.expand_cidr(args.target)
        
        if args.ping:
            devices = await scanner.ping_sweep(targets)
            devices = await scanner.resolve_hostnames(devices)
            devices = await scanner.lookup_vendors(devices)
            return devices
        elif args.stealth:
            return await scanner.stealth_scan(args.target)
        elif args.full:
            return await scanner.full_scan(args.target, ports)
        else:
            return await scanner.quick_scan(args.target)
    
    # Run async scan
    devices = asyncio.run(run_scan())
    
    # Output results
    if args.summary:
        summary = scanner.get_summary()
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print(f"\nScan Summary")
            print(f"============")
            print(f"Total devices: {summary['total_devices']}")
            print(f"With MAC:      {summary['with_mac']}")
            print(f"With hostname: {summary['with_hostname']}")
            print(f"With vendor:   {summary['with_vendor']}")
            print(f"\nVendors:")
            for vendor, count in sorted(summary['vendors'].items(), 
                                        key=lambda x: x[1], reverse=True):
                print(f"  {vendor}: {count}")
    elif args.json:
        print(scanner.get_results_json())
    else:
        # Table output
        if not devices:
            print("No devices found")
            return 1
        
        print(f"\n{'IP Address':<16} {'MAC Address':<18} {'Hostname':<25} {'Vendor':<30}")
        print("-" * 90)
        for device in sorted(devices, key=lambda d: tuple(map(int, d.ip.split('.')))):
            print(f"{device.ip:<16} {device.mac or 'N/A':<18} "
                  f"{(device.hostname or '')[:24]:<25} {(device.vendor or '')[:29]:<30}")
        print(f"\nTotal: {len(devices)} devices")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
