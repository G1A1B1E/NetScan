#!/usr/bin/env python3
"""
NetScan MAC Lookup Module
Cross-platform MAC address vendor lookup
"""

import os
import re
import sys
import json
import argparse
from typing import Optional, Dict, Tuple
from datetime import datetime

# Try to import requests for web lookup fallback
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class MACLookup:
    """MAC address vendor lookup class"""
    
    def __init__(self, oui_path: Optional[str] = None, cache_path: Optional[str] = None):
        """
        Initialize MAC lookup
        
        Args:
            oui_path: Path to OUI database file
            cache_path: Path to cache directory
        """
        self.oui_path = oui_path or self._find_oui_file()
        self.cache_path = cache_path
        self._oui_cache: Dict[str, str] = {}
        self._loaded = False
    
    def _find_oui_file(self) -> Optional[str]:
        """Find OUI file in common locations"""
        # Get script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        
        # Common locations
        locations = [
            os.path.join(parent_dir, 'data', 'oui.txt'),
            os.path.join(script_dir, 'oui.txt'),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'NetScan', 'data', 'oui.txt'),
            os.path.join(os.environ.get('PROGRAMFILES', ''), 'NetScan', 'data', 'oui.txt'),
            'C:\\NetScan\\data\\oui.txt',
        ]
        
        for path in locations:
            if path and os.path.isfile(path):
                return path
        
        return None
    
    def _load_oui_database(self) -> bool:
        """Load OUI database into memory"""
        if self._loaded:
            return True
        
        if not self.oui_path or not os.path.isfile(self.oui_path):
            return False
        
        try:
            with open(self.oui_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    # Format: XX-XX-XX   (hex)		Vendor Name
                    if '(hex)' in line:
                        match = re.match(r'([0-9A-Fa-f]{2}-[0-9A-Fa-f]{2}-[0-9A-Fa-f]{2})\s+\(hex\)\s+(.+)', line)
                        if match:
                            prefix = match.group(1).upper().replace('-', ':')
                            vendor = match.group(2).strip()
                            self._oui_cache[prefix] = vendor
            
            self._loaded = True
            return True
        
        except Exception as e:
            print(f"Error loading OUI database: {e}", file=sys.stderr)
            return False
    
    @staticmethod
    def normalize_mac(mac: str) -> str:
        """Normalize MAC address to XX:XX:XX:XX:XX:XX format"""
        # Remove all separators
        clean = re.sub(r'[-:.]', '', mac.upper())
        
        # Validate length
        if len(clean) != 12:
            return mac
        
        # Validate hex
        if not all(c in '0123456789ABCDEF' for c in clean):
            return mac
        
        # Format with colons
        return ':'.join(clean[i:i+2] for i in range(0, 12, 2))
    
    @staticmethod
    def validate_mac(mac: str) -> bool:
        """Validate MAC address format"""
        patterns = [
            r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$',  # XX:XX:XX:XX:XX:XX
            r'^([0-9A-Fa-f]{2}-){5}[0-9A-Fa-f]{2}$',  # XX-XX-XX-XX-XX-XX
            r'^[0-9A-Fa-f]{12}$',                       # XXXXXXXXXXXX
            r'^([0-9A-Fa-f]{4}\.){2}[0-9A-Fa-f]{4}$',  # XXXX.XXXX.XXXX
        ]
        return any(re.match(pattern, mac) for pattern in patterns)
    
    def get_prefix(self, mac: str) -> str:
        """Get OUI prefix (first 3 octets) from MAC address"""
        normalized = self.normalize_mac(mac)
        return normalized[:8] if len(normalized) >= 8 else normalized
    
    def lookup(self, mac: str) -> Dict[str, str]:
        """
        Look up vendor for MAC address
        
        Args:
            mac: MAC address in any format
        
        Returns:
            Dict with mac, prefix, vendor, source
        """
        result = {
            'mac': mac,
            'normalized': self.normalize_mac(mac),
            'prefix': '',
            'vendor': 'Unknown',
            'source': 'none'
        }
        
        if not self.validate_mac(mac):
            result['error'] = 'Invalid MAC address format'
            return result
        
        result['prefix'] = self.get_prefix(mac)
        
        # Try local database first
        if self._load_oui_database():
            if result['prefix'] in self._oui_cache:
                result['vendor'] = self._oui_cache[result['prefix']]
                result['source'] = 'local'
                return result
        
        # Try web lookup as fallback
        if HAS_REQUESTS:
            web_result = self._web_lookup(result['normalized'])
            if web_result:
                result['vendor'] = web_result
                result['source'] = 'web'
                return result
        
        return result
    
    def _web_lookup(self, mac: str) -> Optional[str]:
        """Look up vendor using web API"""
        try:
            # macvendors.com API
            url = f"https://api.macvendors.com/{mac}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                return response.text.strip()
        except Exception:
            pass
        
        return None
    
    def lookup_batch(self, macs: list) -> list:
        """Look up multiple MAC addresses"""
        return [self.lookup(mac) for mac in macs]
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        self._load_oui_database()
        return {
            'oui_path': self.oui_path,
            'oui_exists': os.path.isfile(self.oui_path) if self.oui_path else False,
            'entries_loaded': len(self._oui_cache),
            'cache_loaded': self._loaded
        }


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='MAC Address Vendor Lookup',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python mac_lookup.py 00:11:22:33:44:55
  python mac_lookup.py -j 00-11-22-33-44-55
  python mac_lookup.py --batch AA:BB:CC:DD:EE:FF 11:22:33:44:55:66
  python mac_lookup.py --validate 00:11:22:33:44:55
  python mac_lookup.py --stats
        '''
    )
    
    parser.add_argument('mac', nargs='?', help='MAC address to look up')
    parser.add_argument('-j', '--json', action='store_true', help='Output as JSON')
    parser.add_argument('-b', '--batch', nargs='+', metavar='MAC', help='Look up multiple MACs')
    parser.add_argument('-v', '--validate', metavar='MAC', help='Validate MAC format')
    parser.add_argument('-n', '--normalize', metavar='MAC', help='Normalize MAC format')
    parser.add_argument('-s', '--stats', action='store_true', help='Show database stats')
    parser.add_argument('-o', '--oui', metavar='PATH', help='Path to OUI database')
    
    args = parser.parse_args()
    
    # Initialize lookup
    lookup = MACLookup(oui_path=args.oui)
    
    # Stats
    if args.stats:
        stats = lookup.get_stats()
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            print("\nMAC Lookup Statistics:")
            print(f"  OUI Path: {stats['oui_path']}")
            print(f"  OUI Exists: {stats['oui_exists']}")
            print(f"  Entries Loaded: {stats['entries_loaded']:,}")
        return
    
    # Validate
    if args.validate:
        valid = lookup.validate_mac(args.validate)
        if args.json:
            print(json.dumps({'mac': args.validate, 'valid': valid}))
        else:
            print(f"Valid: {valid}")
        return
    
    # Normalize
    if args.normalize:
        normalized = lookup.normalize_mac(args.normalize)
        if args.json:
            print(json.dumps({'mac': args.normalize, 'normalized': normalized}))
        else:
            print(normalized)
        return
    
    # Batch lookup
    if args.batch:
        results = lookup.lookup_batch(args.batch)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"\n{'MAC Address':<20} {'Vendor':<40}")
            print("-" * 62)
            for r in results:
                print(f"{r['normalized']:<20} {r['vendor']:<40}")
        return
    
    # Single lookup
    if args.mac:
        result = lookup.lookup(args.mac)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\nMAC: {result['normalized']}")
            print(f"Prefix: {result['prefix']}")
            print(f"Vendor: {result['vendor']}")
            print(f"Source: {result['source']}")
        return
    
    # No arguments - show help
    parser.print_help()


if __name__ == '__main__':
    main()
