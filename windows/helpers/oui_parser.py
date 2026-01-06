#!/usr/bin/env python3
"""
NetScan OUI Parser Module
Parses IEEE OUI database for MAC vendor lookups
"""

import os
import re
import sys
from typing import Dict, Optional, Iterator, Tuple


class OUIParser:
    """IEEE OUI Database Parser"""
    
    def __init__(self, oui_path: Optional[str] = None):
        """
        Initialize OUI parser
        
        Args:
            oui_path: Path to OUI database file
        """
        self.oui_path = oui_path
        self._cache: Dict[str, str] = {}
        self._loaded = False
    
    def load(self, path: Optional[str] = None) -> bool:
        """
        Load OUI database from file
        
        Args:
            path: Path to OUI file (uses self.oui_path if not provided)
        
        Returns:
            True if loaded successfully
        """
        path = path or self.oui_path
        
        if not path or not os.path.isfile(path):
            return False
        
        try:
            self._cache.clear()
            
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    entry = self._parse_line(line)
                    if entry:
                        self._cache[entry[0]] = entry[1]
            
            self.oui_path = path
            self._loaded = True
            return True
        
        except Exception as e:
            print(f"Error loading OUI database: {e}", file=sys.stderr)
            return False
    
    def _parse_line(self, line: str) -> Optional[Tuple[str, str]]:
        """
        Parse a single line from OUI database
        
        Args:
            line: Line from OUI file
        
        Returns:
            Tuple of (prefix, vendor) or None
        """
        # Format: XX-XX-XX   (hex)		Vendor Name
        if '(hex)' in line:
            match = re.match(
                r'([0-9A-Fa-f]{2})-([0-9A-Fa-f]{2})-([0-9A-Fa-f]{2})\s+\(hex\)\s+(.+)',
                line.strip()
            )
            if match:
                prefix = f"{match.group(1)}:{match.group(2)}:{match.group(3)}".upper()
                vendor = match.group(4).strip()
                return (prefix, vendor)
        
        return None
    
    def lookup(self, prefix: str) -> Optional[str]:
        """
        Look up vendor by OUI prefix
        
        Args:
            prefix: OUI prefix (XX:XX:XX)
        
        Returns:
            Vendor name or None
        """
        if not self._loaded:
            self.load()
        
        # Normalize prefix
        normalized = prefix.upper().replace('-', ':')
        if len(normalized) > 8:
            normalized = normalized[:8]
        
        return self._cache.get(normalized)
    
    def lookup_mac(self, mac: str) -> Optional[str]:
        """
        Look up vendor by full MAC address
        
        Args:
            mac: Full MAC address
        
        Returns:
            Vendor name or None
        """
        # Normalize MAC
        clean = re.sub(r'[-:.]', '', mac.upper())
        if len(clean) < 6:
            return None
        
        # Extract prefix
        prefix = f"{clean[0:2]}:{clean[2:4]}:{clean[4:6]}"
        return self.lookup(prefix)
    
    def search(self, query: str) -> Iterator[Tuple[str, str]]:
        """
        Search vendors by name
        
        Args:
            query: Search query (case-insensitive)
        
        Yields:
            Tuples of (prefix, vendor)
        """
        if not self._loaded:
            self.load()
        
        query_lower = query.lower()
        for prefix, vendor in self._cache.items():
            if query_lower in vendor.lower():
                yield (prefix, vendor)
    
    def get_all(self) -> Dict[str, str]:
        """Get all OUI entries"""
        if not self._loaded:
            self.load()
        return self._cache.copy()
    
    def count(self) -> int:
        """Get number of entries"""
        if not self._loaded:
            self.load()
        return len(self._cache)
    
    def is_loaded(self) -> bool:
        """Check if database is loaded"""
        return self._loaded
    
    @staticmethod
    def find_oui_file() -> Optional[str]:
        """Find OUI file in common locations"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        
        locations = [
            os.path.join(parent_dir, 'data', 'oui.txt'),
            os.path.join(script_dir, 'oui.txt'),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'NetScan', 'data', 'oui.txt'),
            os.path.join(os.environ.get('PROGRAMFILES', ''), 'NetScan', 'data', 'oui.txt'),
        ]
        
        for path in locations:
            if path and os.path.isfile(path):
                return path
        
        return None


def main():
    """CLI entry point"""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description='OUI Database Parser')
    parser.add_argument('query', nargs='?', help='MAC or prefix to look up, or vendor to search')
    parser.add_argument('-f', '--file', metavar='PATH', help='Path to OUI database')
    parser.add_argument('-s', '--search', action='store_true', help='Search by vendor name')
    parser.add_argument('-c', '--count', action='store_true', help='Show entry count')
    parser.add_argument('-j', '--json', action='store_true', help='Output as JSON')
    parser.add_argument('--find', action='store_true', help='Find OUI file location')
    
    args = parser.parse_args()
    
    # Find OUI file
    if args.find:
        path = OUIParser.find_oui_file()
        if path:
            print(f"Found: {path}")
        else:
            print("OUI file not found")
        return
    
    # Initialize parser
    oui_path = args.file or OUIParser.find_oui_file()
    parser_obj = OUIParser(oui_path)
    
    # Count
    if args.count:
        count = parser_obj.count()
        if args.json:
            print(json.dumps({'count': count, 'path': oui_path}))
        else:
            print(f"Entries: {count:,}")
            print(f"Path: {oui_path}")
        return
    
    # Search
    if args.search and args.query:
        results = list(parser_obj.search(args.query))
        if args.json:
            print(json.dumps([{'prefix': p, 'vendor': v} for p, v in results], indent=2))
        else:
            print(f"\nFound {len(results)} matches for '{args.query}':\n")
            for prefix, vendor in results[:50]:  # Limit output
                print(f"  {prefix}  {vendor}")
            if len(results) > 50:
                print(f"\n  ... and {len(results) - 50} more")
        return
    
    # Lookup
    if args.query:
        vendor = parser_obj.lookup_mac(args.query)
        if args.json:
            print(json.dumps({'query': args.query, 'vendor': vendor}))
        else:
            print(vendor or "Unknown")
        return
    
    # No arguments
    parser.print_help()


if __name__ == '__main__':
    main()
