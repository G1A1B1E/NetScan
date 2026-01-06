#!/usr/bin/env python3
"""
Network Monitor - Real-time network monitoring with device tracking
Watches for new devices, alerts on changes, tracks device history
"""

import asyncio
import json
import sys
import argparse
import sqlite3
import os
import signal
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import subprocess
import re
import time

# Import our async scanner
try:
    from async_scanner import AsyncScanner, Device
except ImportError:
    # If running standalone, add parent to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from async_scanner import AsyncScanner, Device


@dataclass
class DeviceChange:
    """Represents a change in device status"""
    change_type: str  # 'new', 'returned', 'gone', 'changed'
    device: Device
    previous_state: Optional[Dict] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        return {
            'change_type': self.change_type,
            'device': self.device.to_dict() if isinstance(self.device, Device) else self.device,
            'previous_state': self.previous_state,
            'timestamp': self.timestamp
        }


class DeviceDatabase:
    """SQLite database for device tracking"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS devices (
                    mac TEXT PRIMARY KEY,
                    ip TEXT,
                    hostname TEXT,
                    vendor TEXT,
                    first_seen TEXT,
                    last_seen TEXT,
                    is_known INTEGER DEFAULT 0,
                    is_trusted INTEGER DEFAULT 0,
                    notes TEXT,
                    custom_name TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS device_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mac TEXT,
                    ip TEXT,
                    event_type TEXT,
                    timestamp TEXT,
                    details TEXT,
                    FOREIGN KEY (mac) REFERENCES devices(mac)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scan_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    device_count INTEGER,
                    new_devices INTEGER,
                    gone_devices INTEGER,
                    scan_type TEXT
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_history_mac ON device_history(mac)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_history_time ON device_history(timestamp)
            """)
            
            conn.commit()
    
    def get_device(self, mac: str) -> Optional[Dict]:
        """Get device by MAC address"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM devices WHERE mac = ?",
                (mac.lower(),)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_devices(self) -> List[Dict]:
        """Get all known devices"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM devices ORDER BY last_seen DESC")
            return [dict(row) for row in cursor.fetchall()]
    
    def get_active_devices(self, since_hours: int = 24) -> List[Dict]:
        """Get devices seen in the last N hours"""
        cutoff = (datetime.now() - timedelta(hours=since_hours)).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM devices WHERE last_seen > ? ORDER BY last_seen DESC",
                (cutoff,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def upsert_device(self, device: Device) -> bool:
        """Insert or update device, returns True if new"""
        mac = device.mac.lower()
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            existing = self.get_device(mac)
            
            if existing:
                # Update existing device
                conn.execute("""
                    UPDATE devices 
                    SET ip = ?, hostname = COALESCE(?, hostname), 
                        vendor = COALESCE(?, vendor), last_seen = ?
                    WHERE mac = ?
                """, (device.ip, device.hostname or None, 
                      device.vendor or None, now, mac))
                conn.commit()
                return False
            else:
                # Insert new device
                conn.execute("""
                    INSERT INTO devices (mac, ip, hostname, vendor, first_seen, last_seen)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (mac, device.ip, device.hostname, device.vendor, now, now))
                conn.commit()
                return True
    
    def log_event(self, mac: str, event_type: str, ip: str = "", details: str = ""):
        """Log a device event"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO device_history (mac, ip, event_type, timestamp, details)
                VALUES (?, ?, ?, ?, ?)
            """, (mac.lower(), ip, event_type, datetime.now().isoformat(), details))
            conn.commit()
    
    def log_scan(self, device_count: int, new_devices: int, gone_devices: int, 
                 scan_type: str = "monitor"):
        """Log a scan event"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO scan_history (timestamp, device_count, new_devices, gone_devices, scan_type)
                VALUES (?, ?, ?, ?, ?)
            """, (datetime.now().isoformat(), device_count, new_devices, gone_devices, scan_type))
            conn.commit()
    
    def mark_known(self, mac: str, is_known: bool = True):
        """Mark device as known (expected on network)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE devices SET is_known = ? WHERE mac = ?",
                (1 if is_known else 0, mac.lower())
            )
            conn.commit()
    
    def mark_trusted(self, mac: str, is_trusted: bool = True):
        """Mark device as trusted"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE devices SET is_trusted = ? WHERE mac = ?",
                (1 if is_trusted else 0, mac.lower())
            )
            conn.commit()
    
    def set_custom_name(self, mac: str, name: str):
        """Set custom name for device"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE devices SET custom_name = ? WHERE mac = ?",
                (name, mac.lower())
            )
            conn.commit()
    
    def get_device_history(self, mac: str, limit: int = 100) -> List[Dict]:
        """Get history for a device"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM device_history 
                WHERE mac = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (mac.lower(), limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_unknown_devices(self) -> List[Dict]:
        """Get devices not marked as known"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM devices WHERE is_known = 0 ORDER BY first_seen DESC"
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM devices").fetchone()[0]
            known = conn.execute("SELECT COUNT(*) FROM devices WHERE is_known = 1").fetchone()[0]
            trusted = conn.execute("SELECT COUNT(*) FROM devices WHERE is_trusted = 1").fetchone()[0]
            
            # Active in last 24 hours
            cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
            active = conn.execute(
                "SELECT COUNT(*) FROM devices WHERE last_seen > ?",
                (cutoff,)
            ).fetchone()[0]
            
            # Recent events
            events = conn.execute(
                "SELECT COUNT(*) FROM device_history WHERE timestamp > ?",
                (cutoff,)
            ).fetchone()[0]
            
            return {
                'total_devices': total,
                'known_devices': known,
                'unknown_devices': total - known,
                'trusted_devices': trusted,
                'active_24h': active,
                'events_24h': events
            }


class NetworkMonitor:
    """Real-time network monitoring"""
    
    def __init__(self, db_path: str = None, scan_interval: int = 60,
                 verbose: bool = False):
        if db_path is None:
            # Default to cache directory
            cache_dir = os.path.join(os.path.dirname(__file__), '..', 'cache')
            os.makedirs(cache_dir, exist_ok=True)
            db_path = os.path.join(cache_dir, 'devices.db')
        
        self.db = DeviceDatabase(db_path)
        self.scanner = AsyncScanner(verbose=verbose)
        self.scan_interval = scan_interval
        self.verbose = verbose
        self.running = False
        self.callbacks: List[Callable[[DeviceChange], None]] = []
        self._current_devices: Dict[str, Device] = {}
        self._last_scan_devices: Set[str] = set()
    
    def log(self, message: str):
        """Print log message"""
        if self.verbose:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def add_callback(self, callback: Callable[[DeviceChange], None]):
        """Add callback for device changes"""
        self.callbacks.append(callback)
    
    def _notify(self, change: DeviceChange):
        """Notify all callbacks of a change"""
        for callback in self.callbacks:
            try:
                callback(change)
            except Exception as e:
                self.log(f"Callback error: {e}")
    
    async def scan_network(self, target: str = None) -> List[DeviceChange]:
        """Perform a network scan and detect changes"""
        changes = []
        
        # Get current ARP table
        devices = self.scanner.get_arp_table()
        
        # Optionally do a ping sweep for more thorough scan
        if target:
            targets = self.scanner.expand_cidr(target)
            ping_results = await self.scanner.ping_sweep(targets)
            
            # Merge results
            known_ips = {d.ip for d in devices}
            for d in ping_results:
                if d.ip not in known_ips:
                    devices.append(d)
        
        # Resolve hostnames and vendors
        devices = await self.scanner.resolve_hostnames(devices)
        devices = await self.scanner.lookup_vendors(devices)
        
        # Track current devices by MAC
        current_macs = set()
        new_count = 0
        
        for device in devices:
            if not device.mac:
                continue
            
            mac = device.mac.lower()
            current_macs.add(mac)
            self._current_devices[mac] = device
            
            # Check if new or returning
            existing = self.db.get_device(mac)
            is_new = self.db.upsert_device(device)
            
            if is_new:
                # Brand new device
                new_count += 1
                change = DeviceChange(
                    change_type='new',
                    device=device
                )
                changes.append(change)
                self._notify(change)
                self.db.log_event(mac, 'new', device.ip, 
                                 f"New device: {device.hostname or 'unknown'}")
                self.log(f"🆕 NEW: {device.ip} ({device.mac}) - {device.vendor or 'Unknown vendor'}")
            
            elif mac not in self._last_scan_devices and existing:
                # Returning device
                change = DeviceChange(
                    change_type='returned',
                    device=device,
                    previous_state=existing
                )
                changes.append(change)
                self._notify(change)
                self.db.log_event(mac, 'returned', device.ip)
                self.log(f"↩️  RETURNED: {device.ip} ({device.mac})")
            
            elif existing and existing['ip'] != device.ip:
                # IP changed
                change = DeviceChange(
                    change_type='changed',
                    device=device,
                    previous_state=existing
                )
                changes.append(change)
                self._notify(change)
                self.db.log_event(mac, 'ip_changed', device.ip, 
                                 f"IP changed from {existing['ip']}")
                self.log(f"📝 CHANGED: {device.mac} IP {existing['ip']} -> {device.ip}")
        
        # Check for gone devices
        gone_count = 0
        for mac in self._last_scan_devices:
            if mac not in current_macs:
                gone_count += 1
                existing = self.db.get_device(mac)
                if existing:
                    device = Device(
                        ip=existing['ip'],
                        mac=mac,
                        hostname=existing.get('hostname', ''),
                        vendor=existing.get('vendor', '')
                    )
                    change = DeviceChange(
                        change_type='gone',
                        device=device
                    )
                    changes.append(change)
                    self._notify(change)
                    self.db.log_event(mac, 'gone', existing['ip'])
                    self.log(f"👋 GONE: {existing['ip']} ({mac})")
        
        # Update tracking
        self._last_scan_devices = current_macs
        
        # Log scan
        self.db.log_scan(len(devices), new_count, gone_count)
        
        return changes
    
    async def monitor_loop(self, target: str = None):
        """Main monitoring loop"""
        self.running = True
        self.log(f"Starting network monitor (interval: {self.scan_interval}s)")
        
        # Initial scan
        await self.scan_network(target)
        self.log(f"Initial scan complete: {len(self._current_devices)} devices")
        
        while self.running:
            try:
                await asyncio.sleep(self.scan_interval)
                changes = await self.scan_network(target)
                
                if changes:
                    self.log(f"Scan complete: {len(changes)} changes detected")
                else:
                    self.log(f"Scan complete: no changes")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.log(f"Scan error: {e}")
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
    
    def get_current_devices(self) -> List[Dict]:
        """Get currently active devices"""
        return [d.to_dict() for d in self._current_devices.values()]
    
    def get_unknown_devices(self) -> List[Dict]:
        """Get unknown devices from current scan"""
        unknown = []
        for mac, device in self._current_devices.items():
            db_device = self.db.get_device(mac)
            if db_device and not db_device.get('is_known'):
                unknown.append(device.to_dict())
        return unknown


# =============================================================================
# Alert Handlers
# =============================================================================

def console_alert(change: DeviceChange):
    """Print alert to console"""
    icons = {
        'new': '🚨',
        'returned': '📱',
        'gone': '👋',
        'changed': '📝'
    }
    icon = icons.get(change.change_type, '❓')
    device = change.device
    
    if isinstance(device, dict):
        ip = device.get('ip', 'unknown')
        mac = device.get('mac', 'unknown')
        vendor = device.get('vendor', '')
    else:
        ip = device.ip
        mac = device.mac
        vendor = device.vendor
    
    print(f"\n{icon} [{change.change_type.upper()}] {ip} ({mac})")
    if vendor:
        print(f"   Vendor: {vendor}")


def json_alert(change: DeviceChange):
    """Output alert as JSON"""
    print(json.dumps(change.to_dict()))


def webhook_alert_factory(url: str):
    """Create a webhook alert handler"""
    def webhook_alert(change: DeviceChange):
        try:
            import requests
            requests.post(url, json=change.to_dict(), timeout=5)
        except Exception as e:
            print(f"Webhook error: {e}", file=sys.stderr)
    return webhook_alert


def sound_alert(change: DeviceChange):
    """Play system sound for alerts"""
    if change.change_type == 'new':
        # macOS
        if sys.platform == 'darwin':
            os.system('afplay /System/Library/Sounds/Glass.aiff &')


def desktop_notify(change: DeviceChange):
    """Send desktop notification for alerts"""
    device = change.device
    if isinstance(device, dict):
        ip = device.get('ip', 'unknown')
        mac = device.get('mac', 'unknown')
        vendor = device.get('vendor', 'Unknown device')
    else:
        ip = device.ip
        mac = device.mac
        vendor = device.vendor or 'Unknown device'
    
    titles = {
        'new': '🚨 New Device Detected',
        'returned': '📱 Device Returned',
        'gone': '👋 Device Left',
        'changed': '📝 Device Changed'
    }
    title = titles.get(change.change_type, 'Network Alert')
    message = f"{vendor}\n{ip} ({mac})"
    
    try:
        if sys.platform == 'darwin':  # macOS
            script = f'display notification "{message}" with title "{title}" sound name "Glass"'
            subprocess.run(['osascript', '-e', script], capture_output=True)
        
        elif sys.platform == 'win32':  # Windows
            try:
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast(title, message, duration=5, threaded=True)
            except ImportError:
                # Fallback to PowerShell
                ps_script = f'''
                Add-Type -AssemblyName System.Windows.Forms
                $notify = New-Object System.Windows.Forms.NotifyIcon
                $notify.Icon = [System.Drawing.SystemIcons]::Information
                $notify.Visible = $true
                $notify.ShowBalloonTip(5000, "{title}", "{message}", [System.Windows.Forms.ToolTipIcon]::Info)
                '''
                subprocess.run(['powershell', '-Command', ps_script], capture_output=True)
        
        else:  # Linux
            subprocess.run([
                'notify-send',
                '-u', 'critical' if change.change_type == 'new' else 'normal',
                '-a', 'NetScan',
                '-i', 'network-wireless',
                title,
                message
            ], capture_output=True)
    
    except Exception as e:
        print(f"Desktop notification failed: {e}", file=sys.stderr)


# =============================================================================
# CLI Interface
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Network Monitor - Real-time device tracking',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Start monitoring
  %(prog)s -i 30                              # Scan every 30 seconds
  %(prog)s --target 192.168.1.0/24            # Include ping sweep
  %(prog)s --list                             # List known devices
  %(prog)s --unknown                          # List unknown devices
  %(prog)s --history AA:BB:CC:DD:EE:FF        # Device history
  %(prog)s --mark-known AA:BB:CC:DD:EE:FF     # Mark as known
  %(prog)s --stats                            # Show statistics
        """
    )
    
    parser.add_argument('--target', '-t', metavar='CIDR',
                        help='Target network for ping sweep')
    parser.add_argument('--interval', '-i', type=int, default=60,
                        help='Scan interval in seconds (default: 60)')
    parser.add_argument('--db', metavar='PATH',
                        help='Database file path')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    
    # Query options
    parser.add_argument('--list', '-l', action='store_true',
                        help='List all known devices')
    parser.add_argument('--active', action='store_true',
                        help='List devices active in last 24h')
    parser.add_argument('--unknown', '-u', action='store_true',
                        help='List unknown devices')
    parser.add_argument('--history', metavar='MAC',
                        help='Show history for device')
    parser.add_argument('--stats', '-s', action='store_true',
                        help='Show statistics')
    
    # Management options
    parser.add_argument('--mark-known', metavar='MAC',
                        help='Mark device as known')
    parser.add_argument('--mark-unknown', metavar='MAC',
                        help='Mark device as unknown')
    parser.add_argument('--mark-trusted', metavar='MAC',
                        help='Mark device as trusted')
    parser.add_argument('--set-name', nargs=2, metavar=('MAC', 'NAME'),
                        help='Set custom name for device')
    
    # Alert options
    parser.add_argument('--json', '-j', action='store_true',
                        help='Output as JSON')
    parser.add_argument('--webhook', metavar='URL',
                        help='Webhook URL for alerts')
    parser.add_argument('--sound', action='store_true',
                        help='Play sound for new devices')
    parser.add_argument('--notify', '-n', action='store_true',
                        help='Enable desktop notifications')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Suppress console alerts')
    
    # Single scan
    parser.add_argument('--once', '-1', action='store_true',
                        help='Single scan then exit')
    
    args = parser.parse_args()
    
    # Initialize monitor
    monitor = NetworkMonitor(
        db_path=args.db,
        scan_interval=args.interval,
        verbose=args.verbose
    )
    
    # Query operations
    if args.list:
        devices = monitor.db.get_all_devices()
        if args.json:
            print(json.dumps(devices, indent=2))
        else:
            print(f"\n{'MAC Address':<18} {'IP Address':<16} {'Hostname':<20} {'Vendor':<25} {'Last Seen':<20}")
            print("-" * 100)
            for d in devices:
                print(f"{d['mac']:<18} {d['ip']:<16} {(d.get('hostname') or '')[:19]:<20} "
                      f"{(d.get('vendor') or '')[:24]:<25} {d['last_seen'][:19]:<20}")
            print(f"\nTotal: {len(devices)} devices")
        return 0
    
    if args.active:
        devices = monitor.db.get_active_devices()
        if args.json:
            print(json.dumps(devices, indent=2))
        else:
            print(f"\nActive devices (last 24h): {len(devices)}")
            for d in devices:
                known = "✓" if d.get('is_known') else " "
                print(f"  [{known}] {d['ip']:<16} {d['mac']:<18} {d.get('hostname') or ''}")
        return 0
    
    if args.unknown:
        devices = monitor.db.get_unknown_devices()
        if args.json:
            print(json.dumps(devices, indent=2))
        else:
            print(f"\n⚠️  Unknown devices: {len(devices)}")
            for d in devices:
                print(f"  {d['ip']:<16} {d['mac']:<18} {d.get('vendor') or 'Unknown vendor'}")
                print(f"     First seen: {d['first_seen']}")
        return 0
    
    if args.history:
        history = monitor.db.get_device_history(args.history)
        device = monitor.db.get_device(args.history)
        if args.json:
            print(json.dumps({'device': device, 'history': history}, indent=2))
        else:
            if device:
                print(f"\nDevice: {args.history}")
                print(f"  IP: {device['ip']}")
                print(f"  Hostname: {device.get('hostname') or 'N/A'}")
                print(f"  Vendor: {device.get('vendor') or 'Unknown'}")
                print(f"  First seen: {device['first_seen']}")
                print(f"  Last seen: {device['last_seen']}")
                print(f"  Known: {'Yes' if device.get('is_known') else 'No'}")
                print(f"\nHistory ({len(history)} events):")
                for h in history[:20]:
                    print(f"  {h['timestamp'][:19]} - {h['event_type']}: {h.get('details', '')}")
            else:
                print(f"Device not found: {args.history}")
        return 0
    
    if args.stats:
        stats = monitor.db.get_stats()
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            print("\n📊 Network Monitor Statistics")
            print("=" * 40)
            print(f"Total devices:    {stats['total_devices']}")
            print(f"Known devices:    {stats['known_devices']}")
            print(f"Unknown devices:  {stats['unknown_devices']}")
            print(f"Trusted devices:  {stats['trusted_devices']}")
            print(f"Active (24h):     {stats['active_24h']}")
            print(f"Events (24h):     {stats['events_24h']}")
        return 0
    
    # Management operations
    if args.mark_known:
        monitor.db.mark_known(args.mark_known, True)
        print(f"✓ Marked {args.mark_known} as known")
        return 0
    
    if args.mark_unknown:
        monitor.db.mark_known(args.mark_unknown, False)
        print(f"✓ Marked {args.mark_unknown} as unknown")
        return 0
    
    if args.mark_trusted:
        monitor.db.mark_trusted(args.mark_trusted, True)
        monitor.db.mark_known(args.mark_trusted, True)
        print(f"✓ Marked {args.mark_trusted} as trusted")
        return 0
    
    if args.set_name:
        mac, name = args.set_name
        monitor.db.set_custom_name(mac, name)
        print(f"✓ Set name for {mac}: {name}")
        return 0
    
    # Set up alert handlers
    if not args.quiet:
        if args.json:
            monitor.add_callback(json_alert)
        else:
            monitor.add_callback(console_alert)
    
    if args.webhook:
        monitor.add_callback(webhook_alert_factory(args.webhook))
    
    if args.sound:
        monitor.add_callback(sound_alert)
    
    if args.notify:
        monitor.add_callback(desktop_notify)
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\n\nStopping monitor...")
        monitor.stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Run monitor
    if args.once:
        # Single scan
        changes = asyncio.run(monitor.scan_network(args.target))
        if not args.quiet and not args.json:
            print(f"\nScan complete: {len(monitor._current_devices)} devices, {len(changes)} changes")
    else:
        # Continuous monitoring
        print(f"🔍 Starting network monitor...")
        print(f"   Interval: {args.interval}s")
        if args.target:
            print(f"   Target: {args.target}")
        print(f"   Press Ctrl+C to stop\n")
        
        try:
            asyncio.run(monitor.monitor_loop(args.target))
        except KeyboardInterrupt:
            pass
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
