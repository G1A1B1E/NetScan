#!/usr/bin/env python3
"""
Fast File Parser - High-performance parsing for large files
Significantly faster than awk for files with 1000+ entries
"""

import sys
import re
import json
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Optional, Generator
from dataclasses import dataclass, asdict


@dataclass
class Device:
    """Network device record"""
    ip: str
    mac: str = ""
    hostname: str = ""
    vendor: str = ""
    
    def to_pipe(self) -> str:
        """Output as pipe-delimited string"""
        return f"{self.ip}|{self.mac}|{self.hostname}|{self.vendor}"
    
    def to_dict(self) -> dict:
        return asdict(self)


class MACNormalizer:
    """Normalize MAC addresses to consistent format"""
    
    @staticmethod
    def normalize(mac: str) -> str:
        """Convert MAC to uppercase colon-separated format"""
        if not mac:
            return ""
        
        # Remove all separators and convert to uppercase
        clean = re.sub(r'[:\-.]', '', mac.upper())
        
        # Validate hex characters
        if not re.match(r'^[0-9A-F]+$', clean):
            return mac.upper()
        
        # Pad to 12 characters if needed
        if len(clean) < 12:
            # Try to pad individual octets
            parts = re.split(r'[:\-.]', mac.upper())
            if len(parts) == 6:
                clean = ''.join(p.zfill(2) for p in parts)
        
        # Format as XX:XX:XX:XX:XX:XX
        if len(clean) >= 12:
            return ':'.join(clean[i:i+2] for i in range(0, 12, 2))
        
        return mac.upper()


class XMLParser:
    """Parse nmap XML output"""
    
    @staticmethod
    def parse(filepath: Path) -> Generator[Device, None, None]:
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            
            for host in root.findall('.//host'):
                ip = ""
                mac = ""
                hostname = ""
                
                # Get addresses
                for addr in host.findall('address'):
                    addr_type = addr.get('addrtype', '')
                    if addr_type == 'ipv4':
                        ip = addr.get('addr', '')
                    elif addr_type == 'mac':
                        mac = MACNormalizer.normalize(addr.get('addr', ''))
                
                # Get hostname
                hostnames = host.find('hostnames')
                if hostnames is not None:
                    hostname_elem = hostnames.find('hostname')
                    if hostname_elem is not None:
                        hostname = hostname_elem.get('name', '')
                
                if ip:
                    yield Device(ip=ip, mac=mac, hostname=hostname)
        except ET.ParseError as e:
            print(f"XML parse error: {e}", file=sys.stderr)


class ARPParser:
    """Parse ARP table output (arp -a)"""
    
    # Pattern: hostname (ip) at mac on interface
    PATTERN = re.compile(
        r'^(\S+)\s+\((\d+\.\d+\.\d+\.\d+)\)\s+at\s+([0-9a-fA-F:]+)',
        re.MULTILINE
    )
    
    @staticmethod
    def parse(filepath: Path) -> Generator[Device, None, None]:
        content = filepath.read_text()
        
        for match in ARPParser.PATTERN.finditer(content):
            hostname = match.group(1)
            ip = match.group(2)
            mac = MACNormalizer.normalize(match.group(3))
            
            # Skip special entries
            if hostname == '?':
                hostname = ''
            if 'incomplete' in mac.lower() or mac == 'FF:FF:FF:FF:FF:FF':
                continue
            
            if ip and mac:
                yield Device(ip=ip, mac=mac, hostname=hostname)


class CSVParser:
    """Parse CSV files with flexible column detection"""
    
    IP_HEADERS = {'ip', 'ipaddress', 'ip_address', 'address'}
    MAC_HEADERS = {'mac', 'macaddress', 'mac_address', 'physical', 'hardware', 'hwaddress'}
    HOST_HEADERS = {'host', 'hostname', 'name', 'device', 'devicename'}
    
    @staticmethod
    def parse(filepath: Path) -> Generator[Device, None, None]:
        import csv
        
        with open(filepath, newline='', encoding='utf-8-sig') as f:
            # Detect delimiter
            sample = f.read(4096)
            f.seek(0)
            
            try:
                dialect = csv.Sniffer().sniff(sample)
            except csv.Error:
                dialect = csv.excel
            
            reader = csv.DictReader(f, dialect=dialect)
            
            if not reader.fieldnames:
                return
            
            # Find column mappings
            headers = {h.lower().strip(): h for h in reader.fieldnames}
            ip_col = next((headers[h] for h in CSVParser.IP_HEADERS if h in headers), None)
            mac_col = next((headers[h] for h in CSVParser.MAC_HEADERS if h in headers), None)
            host_col = next((headers[h] for h in CSVParser.HOST_HEADERS if h in headers), None)
            
            if not ip_col:
                # Try first column that looks like IP
                return
            
            for row in reader:
                ip = row.get(ip_col, '').strip()
                mac = MACNormalizer.normalize(row.get(mac_col, '')) if mac_col else ''
                hostname = row.get(host_col, '').strip() if host_col else ''
                
                if ip and re.match(r'^\d+\.\d+\.\d+\.\d+$', ip):
                    yield Device(ip=ip, mac=mac, hostname=hostname)


class JSONParser:
    """Parse JSON device lists"""
    
    IP_KEYS = ['ip', 'ipAddress', 'ip_address', 'IP', 'address']
    MAC_KEYS = ['mac', 'macAddress', 'mac_address', 'MAC', 'hwaddr']
    HOST_KEYS = ['hostname', 'host', 'name', 'deviceName', 'device_name']
    
    @staticmethod
    def _find_key(obj: dict, keys: List[str]) -> str:
        for key in keys:
            if key in obj:
                val = obj[key]
                return str(val) if val else ''
        return ''
    
    @staticmethod
    def parse(filepath: Path) -> Generator[Device, None, None]:
        try:
            data = json.loads(filepath.read_text())
            
            # Handle both array and single object
            items = data if isinstance(data, list) else [data]
            
            for item in items:
                if not isinstance(item, dict):
                    continue
                
                ip = JSONParser._find_key(item, JSONParser.IP_KEYS)
                mac = MACNormalizer.normalize(JSONParser._find_key(item, JSONParser.MAC_KEYS))
                hostname = JSONParser._find_key(item, JSONParser.HOST_KEYS)
                
                if ip and re.match(r'^\d+\.\d+\.\d+\.\d+$', ip):
                    yield Device(ip=ip, mac=mac, hostname=hostname)
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}", file=sys.stderr)


class PlainTextParser:
    """Parse plain text with IP/MAC patterns"""
    
    IP_PATTERN = re.compile(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b')
    MAC_PATTERNS = [
        re.compile(r'\b([0-9a-fA-F]{1,2}(?:[:\-][0-9a-fA-F]{1,2}){5})\b'),  # XX:XX:XX:XX:XX:XX
        re.compile(r'\b([0-9a-fA-F]{4}(?:\.[0-9a-fA-F]{4}){2})\b'),  # XXXX.XXXX.XXXX
    ]
    
    @staticmethod
    def parse(filepath: Path) -> Generator[Device, None, None]:
        seen_ips = set()
        
        for line in filepath.read_text().splitlines():
            ip_match = PlainTextParser.IP_PATTERN.search(line)
            if not ip_match:
                continue
            
            ip = ip_match.group(1)
            if ip in seen_ips:
                continue
            seen_ips.add(ip)
            
            mac = ''
            for pattern in PlainTextParser.MAC_PATTERNS:
                mac_match = pattern.search(line)
                if mac_match:
                    mac = MACNormalizer.normalize(mac_match.group(1))
                    break
            
            if mac:
                yield Device(ip=ip, mac=mac)


def detect_format(filepath: Path) -> str:
    """Auto-detect file format"""
    content = filepath.read_text(errors='ignore')[:4096]
    
    if '<?xml' in content or '<nmaprun' in content.lower():
        return 'xml'
    
    if content.strip().startswith(('[', '{')):
        return 'json'
    
    first_line = content.split('\n')[0].lower()
    if any(h in first_line for h in ('ip,', 'mac,', 'host,', 'address,')):
        return 'csv'
    
    if re.search(r'\(\d+\.\d+\.\d+\.\d+\)\s+at\s+[0-9a-fA-F:]', content):
        return 'arp'
    
    return 'text'


def parse_file(filepath: Path, format: str = 'auto') -> List[Device]:
    """Parse file and return list of devices"""
    if format == 'auto':
        format = detect_format(filepath)
    
    parsers = {
        'xml': XMLParser.parse,
        'arp': ARPParser.parse,
        'csv': CSVParser.parse,
        'json': JSONParser.parse,
        'text': PlainTextParser.parse,
    }
    
    parser = parsers.get(format, PlainTextParser.parse)
    return list(parser(filepath))


def main():
    parser = argparse.ArgumentParser(description="Fast network file parser")
    parser.add_argument("file", help="File to parse")
    parser.add_argument("-f", "--format", choices=['auto', 'xml', 'arp', 'csv', 'json', 'text'],
                        default='auto', help="File format")
    parser.add_argument("-o", "--output", choices=['pipe', 'json', 'csv'],
                        default='pipe', help="Output format")
    parser.add_argument("--detect", action="store_true", help="Only detect format")
    
    args = parser.parse_args()
    filepath = Path(args.file)
    
    if not filepath.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    
    if args.detect:
        print(detect_format(filepath))
        return
    
    devices = parse_file(filepath, args.format)
    
    if args.output == 'json':
        print(json.dumps([d.to_dict() for d in devices], indent=2))
    elif args.output == 'csv':
        print("ip,mac,hostname,vendor")
        for d in devices:
            print(f"{d.ip},{d.mac},{d.hostname},{d.vendor}")
    else:
        for d in devices:
            print(d.to_pipe())


if __name__ == "__main__":
    main()
