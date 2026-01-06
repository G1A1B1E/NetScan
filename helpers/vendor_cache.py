#!/usr/bin/env python3
"""
MAC Vendor Lookup Cache - Fast vendor lookups with local caching
Reduces API calls by caching results in SQLite database
"""

import sys
import os
import sqlite3
import json
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

# Cache configuration
CACHE_DIR = Path(__file__).parent.parent / "cache"
CACHE_DB = CACHE_DIR / "vendor_cache.db"
CACHE_EXPIRY_DAYS = 30
API_URL = "https://api.macvendors.com/{}"
API_RATE_LIMIT = 0.5  # seconds between requests

class VendorCache:
    """SQLite-backed cache for MAC vendor lookups"""
    
    def __init__(self, db_path: Path = CACHE_DB):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize the database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS vendor_cache (
                    mac_prefix TEXT PRIMARY KEY,
                    vendor TEXT NOT NULL,
                    timestamp INTEGER NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON vendor_cache(timestamp)
            """)
    
    def _normalize_mac(self, mac: str) -> str:
        """Normalize MAC address to prefix (first 3 octets)"""
        mac = mac.upper().replace("-", ":").replace(".", "")
        # Handle different formats
        if ":" not in mac and len(mac) >= 6:
            mac = ":".join([mac[i:i+2] for i in range(0, min(len(mac), 12), 2)])
        parts = mac.split(":")
        if len(parts) >= 3:
            return ":".join(parts[:3])
        return mac
    
    def get(self, mac: str) -> Optional[str]:
        """Get vendor from cache if not expired"""
        prefix = self._normalize_mac(mac)
        expiry_time = int(time.time()) - (CACHE_EXPIRY_DAYS * 86400)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT vendor FROM vendor_cache WHERE mac_prefix = ? AND timestamp > ?",
                (prefix, expiry_time)
            )
            row = cursor.fetchone()
            return row[0] if row else None
    
    def set(self, mac: str, vendor: str):
        """Store vendor in cache"""
        prefix = self._normalize_mac(mac)
        timestamp = int(time.time())
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO vendor_cache (mac_prefix, vendor, timestamp) VALUES (?, ?, ?)",
                (prefix, vendor, timestamp)
            )
    
    def get_many(self, macs: List[str]) -> Dict[str, Optional[str]]:
        """Batch get vendors from cache"""
        results = {}
        for mac in macs:
            results[mac] = self.get(mac)
        return results
    
    def cleanup_expired(self):
        """Remove expired entries"""
        expiry_time = int(time.time()) - (CACHE_EXPIRY_DAYS * 86400)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM vendor_cache WHERE timestamp < ?", (expiry_time,))
    
    def stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM vendor_cache").fetchone()[0]
            expiry_time = int(time.time()) - (CACHE_EXPIRY_DAYS * 86400)
            valid = conn.execute(
                "SELECT COUNT(*) FROM vendor_cache WHERE timestamp > ?",
                (expiry_time,)
            ).fetchone()[0]
            return {"total": total, "valid": valid, "expired": total - valid}


def lookup_vendor_api(mac: str) -> str:
    """Lookup vendor from API"""
    try:
        url = API_URL.format(mac)
        req = urllib.request.Request(url, headers={"User-Agent": "NetScan/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            vendor = response.read().decode("utf-8").strip()
            if vendor and "Not Found" not in vendor:
                return vendor
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return "Unknown"
        elif e.code == 429:
            return "Rate Limited"
    except Exception:
        pass
    return "Unknown"


def lookup_single(mac: str, use_cache: bool = True) -> str:
    """Lookup a single MAC address"""
    cache = VendorCache()
    
    if use_cache:
        cached = cache.get(mac)
        if cached:
            return cached
    
    vendor = lookup_vendor_api(mac)
    
    if vendor not in ("Rate Limited", "Unknown"):
        cache.set(mac, vendor)
    
    return vendor


def lookup_batch(macs: List[str], max_workers: int = 3) -> Dict[str, str]:
    """Lookup multiple MAC addresses with caching and rate limiting"""
    cache = VendorCache()
    results = {}
    to_lookup = []
    
    # Check cache first
    for mac in macs:
        cached = cache.get(mac)
        if cached:
            results[mac] = cached
        else:
            to_lookup.append(mac)
    
    # Lookup remaining with rate limiting
    for i, mac in enumerate(to_lookup):
        if i > 0:
            time.sleep(API_RATE_LIMIT)
        vendor = lookup_vendor_api(mac)
        results[mac] = vendor
        if vendor not in ("Rate Limited", "Unknown"):
            cache.set(mac, vendor)
    
    return results


def main():
    """CLI interface for vendor lookups"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MAC Vendor Lookup with Caching")
    parser.add_argument("mac", nargs="*", help="MAC address(es) to lookup")
    parser.add_argument("-f", "--file", help="File with MAC addresses (one per line)")
    parser.add_argument("--no-cache", action="store_true", help="Skip cache")
    parser.add_argument("--stats", action="store_true", help="Show cache statistics")
    parser.add_argument("--cleanup", action="store_true", help="Cleanup expired cache entries")
    parser.add_argument("-j", "--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    cache = VendorCache()
    
    if args.stats:
        stats = cache.stats()
        if args.json:
            print(json.dumps(stats))
        else:
            print(f"Cache entries: {stats['total']}")
            print(f"Valid: {stats['valid']}")
            print(f"Expired: {stats['expired']}")
        return
    
    if args.cleanup:
        cache.cleanup_expired()
        print("Cache cleaned up")
        return
    
    macs = list(args.mac) if args.mac else []
    
    if args.file:
        with open(args.file) as f:
            macs.extend(line.strip() for line in f if line.strip())
    
    if not macs:
        parser.print_help()
        sys.exit(1)
    
    if len(macs) == 1:
        vendor = lookup_single(macs[0], use_cache=not args.no_cache)
        if args.json:
            print(json.dumps({"mac": macs[0], "vendor": vendor}))
        else:
            print(vendor)
    else:
        results = lookup_batch(macs)
        if args.json:
            print(json.dumps(results))
        else:
            for mac, vendor in results.items():
                print(f"{mac}|{vendor}")


if __name__ == "__main__":
    main()
