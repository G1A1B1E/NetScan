#!/usr/bin/env python3
"""
Fast Core Functions - Uses Rust when available, falls back to Python

This module provides high-performance implementations for:
- MAC address normalization
- OUI/vendor lookup
- IP address utilities  
- File parsing

If the Rust module (netscan_core) is compiled and available,
it will be used for 10-100x performance improvement.
Otherwise, pure Python implementations are used.
"""

import re
import ipaddress
from typing import List, Dict, Optional, Tuple
from pathlib import Path

# Try to import Rust module
try:
    import netscan_core as _rust
    HAS_RUST = True
except ImportError:
    HAS_RUST = False
    _rust = None


# =============================================================================
# MAC Address Functions
# =============================================================================

def _py_normalize_mac(mac: str) -> str:
    """Pure Python MAC normalization"""
    if not mac:
        return ""
    
    # Remove all separators
    clean = re.sub(r'[:\-.]', '', mac.upper())
    
    if not re.match(r'^[0-9A-F]+$', clean):
        return mac.upper()
    
    if len(clean) >= 12:
        return ':'.join(clean[i:i+2] for i in range(0, 12, 2))
    
    return mac.upper()


def normalize_mac(mac: str) -> str:
    """Normalize MAC address to XX:XX:XX:XX:XX:XX format"""
    if HAS_RUST:
        return _rust.normalize_mac(mac)
    return _py_normalize_mac(mac)


def normalize_macs(macs: List[str]) -> List[str]:
    """Batch normalize MAC addresses"""
    if HAS_RUST:
        return _rust.normalize_macs(macs)
    return [_py_normalize_mac(mac) for mac in macs]


def extract_oui(mac: str) -> str:
    """Extract OUI prefix from MAC address"""
    if HAS_RUST:
        return _rust.extract_oui(mac)
    normalized = normalize_mac(mac)
    return normalized[:8] if len(normalized) >= 8 else normalized


# =============================================================================
# OUI Database Functions
# =============================================================================

def _py_parse_oui_file(filepath: str) -> Dict[str, str]:
    """Pure Python OUI file parser"""
    oui_db = {}
    pattern = re.compile(r'^([0-9A-Fa-f]{2}[:\-]?[0-9A-Fa-f]{2}[:\-]?[0-9A-Fa-f]{2})\s+\(hex\)\s+(.+)$')
    
    with open(filepath, 'r', errors='ignore') as f:
        for line in f:
            match = pattern.match(line)
            if match:
                prefix = match.group(1).upper().replace('-', ':')
                vendor = match.group(2).strip()
                oui_db[prefix] = vendor
    
    return oui_db


def parse_oui_file(filepath: str) -> Dict[str, str]:
    """Parse OUI database file"""
    if HAS_RUST:
        return _rust.parse_oui_file(filepath)
    return _py_parse_oui_file(filepath)


def lookup_oui(oui_db: Dict[str, str], mac: str) -> Optional[str]:
    """Lookup vendor from OUI database"""
    if HAS_RUST:
        return _rust.lookup_oui(oui_db, mac)
    prefix = extract_oui(mac)
    return oui_db.get(prefix)


def lookup_ouis(oui_db: Dict[str, str], macs: List[str]) -> Dict[str, str]:
    """Batch lookup vendors from OUI database"""
    if HAS_RUST:
        return _rust.lookup_ouis(oui_db, macs)
    return {mac: lookup_oui(oui_db, mac) for mac in macs if lookup_oui(oui_db, mac)}


# =============================================================================
# IP Address Functions
# =============================================================================

def _py_expand_cidr(cidr: str) -> List[str]:
    """Pure Python CIDR expansion"""
    network = ipaddress.ip_network(cidr, strict=False)
    return [str(ip) for ip in network]


def _py_expand_cidr_hosts(cidr: str) -> List[str]:
    """Pure Python CIDR expansion (hosts only)"""
    network = ipaddress.ip_network(cidr, strict=False)
    return [str(ip) for ip in network.hosts()]


def expand_cidr(cidr: str) -> List[str]:
    """Expand CIDR notation to list of IP addresses"""
    if HAS_RUST:
        return _rust.expand_cidr(cidr)
    return _py_expand_cidr(cidr)


def expand_cidr_hosts(cidr: str) -> List[str]:
    """Expand CIDR to hosts only (excludes network/broadcast)"""
    if HAS_RUST:
        return _rust.expand_cidr_hosts(cidr)
    return _py_expand_cidr_hosts(cidr)


def expand_ip_range(start: str, end: str) -> List[str]:
    """Expand IP range to list of addresses"""
    if HAS_RUST:
        return _rust.expand_ip_range(start, end)
    
    start_ip = ipaddress.ip_address(start)
    end_ip = ipaddress.ip_address(end)
    return [str(ipaddress.ip_address(ip)) for ip in range(int(start_ip), int(end_ip) + 1)]


def is_private_ip(ip: str) -> bool:
    """Check if IP is private/local"""
    if HAS_RUST:
        return _rust.is_private_ip(ip)
    try:
        addr = ipaddress.ip_address(ip)
        return addr.is_private or addr.is_loopback or addr.is_link_local
    except ValueError:
        return False


def sort_ips(ips: List[str]) -> List[str]:
    """Sort IP addresses numerically"""
    if HAS_RUST:
        return _rust.sort_ips(ips)
    return sorted(ips, key=lambda ip: int(ipaddress.ip_address(ip)))


# =============================================================================
# Parsing Functions
# =============================================================================

def _py_parse_arp_output(output: str) -> List[Tuple[str, str, str]]:
    """Pure Python ARP output parser"""
    pattern = re.compile(r'^(\S+)\s+\((\d+\.\d+\.\d+\.\d+)\)\s+at\s+([0-9a-fA-F:]+)')
    results = []
    for line in output.split('\n'):
        match = pattern.match(line)
        if match:
            results.append((
                match.group(2),  # IP
                normalize_mac(match.group(3)),  # MAC
                match.group(1),  # Hostname
            ))
    return results


def parse_arp_output(output: str) -> List[Tuple[str, str, str]]:
    """Parse ARP table output"""
    if HAS_RUST:
        return _rust.parse_arp_output(output)
    return _py_parse_arp_output(output)


def parse_pipe_file(filepath: str) -> List[Dict[str, str]]:
    """Parse pipe-delimited file"""
    if HAS_RUST:
        return _rust.parse_pipe_file(filepath)
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    if not lines:
        return []
    
    headers = lines[0].strip().split('|')
    results = []
    for line in lines[1:]:
        values = line.strip().split('|')
        results.append(dict(zip(headers, values)))
    return results


def dedupe_devices(devices: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Deduplicate devices by IP"""
    if HAS_RUST:
        return _rust.dedupe_devices(devices)
    
    deduped = {}
    for device in devices:
        ip = device.get('ip', '')
        if not ip:
            continue
        
        if ip in deduped:
            # Merge non-empty fields
            for k, v in device.items():
                if v and not deduped[ip].get(k):
                    deduped[ip][k] = v
        else:
            deduped[ip] = device.copy()
    
    return list(deduped.values())


# =============================================================================
# Status
# =============================================================================

def get_backend_info() -> Dict[str, any]:
    """Get information about the backend being used"""
    return {
        "rust_available": HAS_RUST,
        "backend": "rust" if HAS_RUST else "python",
        "version": getattr(_rust, "__version__", "unknown") if HAS_RUST else "pure-python",
    }


def print_backend_status():
    """Print backend status"""
    info = get_backend_info()
    if info["rust_available"]:
        print(f"✓ Using Rust backend (10-100x faster)")
    else:
        print(f"! Using Python fallback (consider compiling Rust module)")


if __name__ == "__main__":
    import sys
    
    print_backend_status()
    print()
    
    # Run some benchmarks
    import time
    
    # Test MAC normalization
    test_macs = ["00:11:22:33:44:55", "00-11-22-33-44-55", "001122334455", "0:1:2:3:4:5"] * 1000
    
    start = time.time()
    results = normalize_macs(test_macs)
    elapsed = time.time() - start
    
    print(f"Normalized {len(test_macs)} MACs in {elapsed*1000:.2f}ms")
    print(f"  Rate: {len(test_macs)/elapsed:.0f} MACs/sec")
    print()
    
    # Test CIDR expansion
    start = time.time()
    ips = expand_cidr_hosts("192.168.1.0/24")
    elapsed = time.time() - start
    
    print(f"Expanded /24 to {len(ips)} hosts in {elapsed*1000:.2f}ms")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test-oui":
        oui_file = sys.argv[2] if len(sys.argv) > 2 else "/usr/share/nmap/nmap-mac-prefixes"
        if Path(oui_file).exists():
            start = time.time()
            db = parse_oui_file(oui_file)
            elapsed = time.time() - start
            print(f"\nParsed OUI file with {len(db)} entries in {elapsed*1000:.2f}ms")
