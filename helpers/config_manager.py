#!/usr/bin/env python3
"""
Configuration Manager - User preferences, custom OUIs, and device management
Handles all configuration for NetScan
"""

import sys
import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime
import re
import shutil


# Default configuration
DEFAULT_CONFIG = {
    "general": {
        "default_export_format": "csv",
        "auto_vendor_lookup": True,
        "verbose_mode": False,
        "color_output": True,
        "log_level": "info"
    },
    "scanning": {
        "default_timeout": 1.0,
        "max_concurrent": 100,
        "default_ports": [22, 80, 443, 8080],
        "ping_count": 1,
        "arp_cache_first": True,
        "auto_resolve_hostnames": True
    },
    "monitoring": {
        "scan_interval": 60,
        "alert_on_new": True,
        "alert_on_gone": True,
        "alert_sound": False,
        "webhook_url": "",
        "known_devices_file": ""
    },
    "export": {
        "default_directory": "exports",
        "include_timestamp": True,
        "csv_delimiter": ",",
        "json_pretty": True
    },
    "web": {
        "enabled": False,
        "host": "127.0.0.1",
        "port": 8080,
        "auto_open_browser": True
    },
    "custom_ouis": {},
    "excluded_macs": [],
    "excluded_ips": [],
    "known_devices": {},
    "device_names": {}
}


@dataclass
class KnownDevice:
    """Represents a known/expected device"""
    mac: str
    name: str
    description: str = ""
    expected_ip: str = ""
    device_type: str = ""  # router, printer, phone, computer, iot, etc.
    is_trusted: bool = False
    owner: str = ""
    notes: str = ""
    added_date: str = ""
    
    def __post_init__(self):
        self.mac = self.mac.lower().replace('-', ':')
        if not self.added_date:
            self.added_date = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        return asdict(self)


class ConfigManager:
    """Manage NetScan configuration"""
    
    def __init__(self, config_dir: str = None):
        if config_dir is None:
            # Default to ~/.config/netscan or script's config dir
            home_config = os.path.expanduser("~/.config/netscan")
            script_config = os.path.join(os.path.dirname(__file__), '..', 'config')
            
            # Prefer home config if it exists, otherwise use script dir
            if os.path.exists(home_config):
                config_dir = home_config
            elif os.path.exists(script_config):
                config_dir = script_config
            else:
                # Create in home
                config_dir = home_config
        
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "config.json"
        self.oui_file = self.config_dir / "custom_oui.json"
        self.known_devices_file = self.config_dir / "known_devices.json"
        self.exclude_file = self.config_dir / "exclude.json"
        
        self._config: Dict = {}
        self._custom_ouis: Dict[str, str] = {}
        self._known_devices: Dict[str, KnownDevice] = {}
        self._excluded_macs: List[str] = []
        self._excluded_ips: List[str] = []
        
        self._ensure_config_dir()
        self.load()
    
    def _ensure_config_dir(self):
        """Ensure config directory exists"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    # =========================================================================
    # Load/Save
    # =========================================================================
    
    def load(self):
        """Load all configuration files"""
        self._load_config()
        self._load_custom_ouis()
        self._load_known_devices()
        self._load_excludes()
    
    def _load_config(self):
        """Load main config file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self._config = json.load(f)
            except json.JSONDecodeError:
                self._config = {}
        
        # Merge with defaults
        self._config = self._merge_dicts(DEFAULT_CONFIG.copy(), self._config)
    
    def _load_custom_ouis(self):
        """Load custom OUI definitions"""
        if self.oui_file.exists():
            try:
                with open(self.oui_file, 'r') as f:
                    self._custom_ouis = json.load(f)
            except json.JSONDecodeError:
                self._custom_ouis = {}
        
        # Also load from main config
        self._custom_ouis.update(self._config.get('custom_ouis', {}))
    
    def _load_known_devices(self):
        """Load known devices"""
        if self.known_devices_file.exists():
            try:
                with open(self.known_devices_file, 'r') as f:
                    data = json.load(f)
                    for mac, device_data in data.items():
                        if isinstance(device_data, dict):
                            self._known_devices[mac.lower()] = KnownDevice(**device_data)
                        else:
                            # Simple format: just name
                            self._known_devices[mac.lower()] = KnownDevice(mac=mac, name=device_data)
            except json.JSONDecodeError:
                self._known_devices = {}
        
        # Also load from main config
        for mac, device_data in self._config.get('known_devices', {}).items():
            if isinstance(device_data, dict):
                self._known_devices[mac.lower()] = KnownDevice(**device_data)
            else:
                self._known_devices[mac.lower()] = KnownDevice(mac=mac, name=device_data)
    
    def _load_excludes(self):
        """Load exclusion lists"""
        if self.exclude_file.exists():
            try:
                with open(self.exclude_file, 'r') as f:
                    data = json.load(f)
                    self._excluded_macs = [m.lower() for m in data.get('macs', [])]
                    self._excluded_ips = data.get('ips', [])
            except json.JSONDecodeError:
                pass
        
        # Also load from main config
        self._excluded_macs.extend([m.lower() for m in self._config.get('excluded_macs', [])])
        self._excluded_ips.extend(self._config.get('excluded_ips', []))
    
    def save(self):
        """Save all configuration"""
        self._save_config()
        self._save_custom_ouis()
        self._save_known_devices()
        self._save_excludes()
    
    def _save_config(self):
        """Save main config"""
        with open(self.config_file, 'w') as f:
            json.dump(self._config, f, indent=2)
    
    def _save_custom_ouis(self):
        """Save custom OUIs"""
        with open(self.oui_file, 'w') as f:
            json.dump(self._custom_ouis, f, indent=2)
    
    def _save_known_devices(self):
        """Save known devices"""
        data = {mac: device.to_dict() for mac, device in self._known_devices.items()}
        with open(self.known_devices_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _save_excludes(self):
        """Save exclusion lists"""
        data = {
            'macs': list(set(self._excluded_macs)),
            'ips': list(set(self._excluded_ips))
        }
        with open(self.exclude_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _merge_dicts(self, base: dict, override: dict) -> dict:
        """Deep merge two dictionaries"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_dicts(result[key], value)
            else:
                result[key] = value
        return result
    
    # =========================================================================
    # Config Access
    # =========================================================================
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get config value using dot notation (e.g., 'scanning.timeout')"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def set(self, key: str, value: Any):
        """Set config value using dot notation"""
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self._save_config()
    
    def get_all(self) -> Dict:
        """Get entire configuration"""
        return self._config.copy()
    
    # =========================================================================
    # Custom OUI Management
    # =========================================================================
    
    def add_oui(self, oui: str, vendor: str):
        """Add custom OUI definition"""
        # Normalize OUI (first 6 hex chars)
        oui = re.sub(r'[^0-9a-fA-F]', '', oui)[:6].lower()
        self._custom_ouis[oui] = vendor
        self._save_custom_ouis()
    
    def remove_oui(self, oui: str):
        """Remove custom OUI"""
        oui = re.sub(r'[^0-9a-fA-F]', '', oui)[:6].lower()
        if oui in self._custom_ouis:
            del self._custom_ouis[oui]
            self._save_custom_ouis()
    
    def get_custom_vendor(self, mac: str) -> Optional[str]:
        """Get custom vendor for MAC address"""
        oui = re.sub(r'[^0-9a-fA-F]', '', mac)[:6].lower()
        return self._custom_ouis.get(oui)
    
    def list_custom_ouis(self) -> Dict[str, str]:
        """List all custom OUIs"""
        return self._custom_ouis.copy()
    
    # =========================================================================
    # Known Device Management
    # =========================================================================
    
    def add_known_device(self, mac: str, name: str, **kwargs) -> KnownDevice:
        """Add or update a known device"""
        mac = mac.lower().replace('-', ':')
        device = KnownDevice(mac=mac, name=name, **kwargs)
        self._known_devices[mac] = device
        self._save_known_devices()
        return device
    
    def remove_known_device(self, mac: str):
        """Remove a known device"""
        mac = mac.lower().replace('-', ':')
        if mac in self._known_devices:
            del self._known_devices[mac]
            self._save_known_devices()
    
    def get_known_device(self, mac: str) -> Optional[KnownDevice]:
        """Get known device by MAC"""
        mac = mac.lower().replace('-', ':')
        return self._known_devices.get(mac)
    
    def is_known_device(self, mac: str) -> bool:
        """Check if device is known"""
        mac = mac.lower().replace('-', ':')
        return mac in self._known_devices
    
    def list_known_devices(self) -> List[KnownDevice]:
        """List all known devices"""
        return list(self._known_devices.values())
    
    def get_device_name(self, mac: str) -> Optional[str]:
        """Get custom name for device"""
        device = self.get_known_device(mac)
        return device.name if device else None
    
    # =========================================================================
    # Exclusion Management
    # =========================================================================
    
    def exclude_mac(self, mac: str):
        """Add MAC to exclusion list"""
        mac = mac.lower().replace('-', ':')
        if mac not in self._excluded_macs:
            self._excluded_macs.append(mac)
            self._save_excludes()
    
    def include_mac(self, mac: str):
        """Remove MAC from exclusion list"""
        mac = mac.lower().replace('-', ':')
        if mac in self._excluded_macs:
            self._excluded_macs.remove(mac)
            self._save_excludes()
    
    def is_excluded_mac(self, mac: str) -> bool:
        """Check if MAC is excluded"""
        mac = mac.lower().replace('-', ':')
        return mac in self._excluded_macs
    
    def exclude_ip(self, ip: str):
        """Add IP to exclusion list"""
        if ip not in self._excluded_ips:
            self._excluded_ips.append(ip)
            self._save_excludes()
    
    def include_ip(self, ip: str):
        """Remove IP from exclusion list"""
        if ip in self._excluded_ips:
            self._excluded_ips.remove(ip)
            self._save_excludes()
    
    def is_excluded_ip(self, ip: str) -> bool:
        """Check if IP is excluded"""
        return ip in self._excluded_ips
    
    def list_exclusions(self) -> Dict:
        """List all exclusions"""
        return {
            'macs': self._excluded_macs.copy(),
            'ips': self._excluded_ips.copy()
        }
    
    # =========================================================================
    # Import/Export
    # =========================================================================
    
    def export_config(self, filepath: str):
        """Export full configuration to file"""
        full_config = {
            'config': self._config,
            'custom_ouis': self._custom_ouis,
            'known_devices': {m: d.to_dict() for m, d in self._known_devices.items()},
            'exclusions': {
                'macs': self._excluded_macs,
                'ips': self._excluded_ips
            },
            'exported_at': datetime.now().isoformat()
        }
        with open(filepath, 'w') as f:
            json.dump(full_config, f, indent=2)
    
    def import_config(self, filepath: str, merge: bool = True):
        """Import configuration from file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        if merge:
            # Merge with existing
            if 'config' in data:
                self._config = self._merge_dicts(self._config, data['config'])
            if 'custom_ouis' in data:
                self._custom_ouis.update(data['custom_ouis'])
            if 'known_devices' in data:
                for mac, device_data in data['known_devices'].items():
                    self._known_devices[mac.lower()] = KnownDevice(**device_data)
            if 'exclusions' in data:
                self._excluded_macs.extend(data['exclusions'].get('macs', []))
                self._excluded_ips.extend(data['exclusions'].get('ips', []))
        else:
            # Replace entirely
            if 'config' in data:
                self._config = self._merge_dicts(DEFAULT_CONFIG.copy(), data['config'])
            if 'custom_ouis' in data:
                self._custom_ouis = data['custom_ouis']
            if 'known_devices' in data:
                self._known_devices = {
                    m.lower(): KnownDevice(**d) for m, d in data['known_devices'].items()
                }
            if 'exclusions' in data:
                self._excluded_macs = data['exclusions'].get('macs', [])
                self._excluded_ips = data['exclusions'].get('ips', [])
        
        self.save()
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self._config = DEFAULT_CONFIG.copy()
        self._custom_ouis = {}
        self._known_devices = {}
        self._excluded_macs = []
        self._excluded_ips = []
        self.save()
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def filter_devices(self, devices: List[Dict]) -> List[Dict]:
        """Filter devices based on exclusion lists"""
        filtered = []
        for device in devices:
            mac = device.get('mac', '').lower().replace('-', ':')
            ip = device.get('ip', '')
            
            if self.is_excluded_mac(mac):
                continue
            if self.is_excluded_ip(ip):
                continue
            
            filtered.append(device)
        
        return filtered
    
    def enrich_device(self, device: Dict) -> Dict:
        """Enrich device with custom data"""
        enriched = device.copy()
        mac = device.get('mac', '').lower().replace('-', ':')
        
        # Add custom vendor if available
        custom_vendor = self.get_custom_vendor(mac)
        if custom_vendor:
            enriched['vendor'] = custom_vendor
            enriched['vendor_source'] = 'custom'
        
        # Add known device info
        known = self.get_known_device(mac)
        if known:
            enriched['known_name'] = known.name
            enriched['is_known'] = True
            enriched['is_trusted'] = known.is_trusted
            enriched['device_type'] = known.device_type
            if known.description:
                enriched['description'] = known.description
        else:
            enriched['is_known'] = False
            enriched['is_trusted'] = False
        
        return enriched
    
    def enrich_devices(self, devices: List[Dict]) -> List[Dict]:
        """Enrich multiple devices"""
        return [self.enrich_device(d) for d in devices]


# =============================================================================
# CLI Interface
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Configuration Manager - NetScan settings and device management',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --show                              # Show current config
  %(prog)s --set scanning.timeout 2.0          # Set config value
  %(prog)s --get scanning.timeout              # Get config value
  
  %(prog)s --add-device AA:BB:CC:DD:EE:FF "My Router"
  %(prog)s --add-device AA:BB:CC:DD:EE:FF "My Router" --type router --trusted
  %(prog)s --list-devices                      # List known devices
  %(prog)s --remove-device AA:BB:CC:DD:EE:FF
  
  %(prog)s --add-oui AABBCC "My Company"       # Add custom OUI
  %(prog)s --list-ouis                         # List custom OUIs
  
  %(prog)s --exclude-mac AA:BB:CC:DD:EE:FF     # Exclude device
  %(prog)s --list-exclusions
  
  %(prog)s --export config_backup.json         # Export config
  %(prog)s --import config_backup.json         # Import config
  %(prog)s --reset                             # Reset to defaults
        """
    )
    
    parser.add_argument('--config-dir', metavar='DIR', help='Configuration directory')
    
    # Show/get/set
    parser.add_argument('--show', '-s', action='store_true', help='Show full configuration')
    parser.add_argument('--get', metavar='KEY', help='Get config value')
    parser.add_argument('--set', nargs=2, metavar=('KEY', 'VALUE'), help='Set config value')
    
    # Device management
    parser.add_argument('--add-device', nargs=2, metavar=('MAC', 'NAME'),
                        help='Add known device')
    parser.add_argument('--type', metavar='TYPE', help='Device type (with --add-device)')
    parser.add_argument('--trusted', action='store_true', help='Mark as trusted (with --add-device)')
    parser.add_argument('--remove-device', metavar='MAC', help='Remove known device')
    parser.add_argument('--list-devices', '-d', action='store_true', help='List known devices')
    
    # OUI management
    parser.add_argument('--add-oui', nargs=2, metavar=('OUI', 'VENDOR'),
                        help='Add custom OUI')
    parser.add_argument('--remove-oui', metavar='OUI', help='Remove custom OUI')
    parser.add_argument('--list-ouis', '-o', action='store_true', help='List custom OUIs')
    
    # Exclusions
    parser.add_argument('--exclude-mac', metavar='MAC', help='Exclude MAC address')
    parser.add_argument('--include-mac', metavar='MAC', help='Remove MAC from exclusions')
    parser.add_argument('--exclude-ip', metavar='IP', help='Exclude IP address')
    parser.add_argument('--include-ip', metavar='IP', help='Remove IP from exclusions')
    parser.add_argument('--list-exclusions', '-e', action='store_true', help='List exclusions')
    
    # Import/Export
    parser.add_argument('--export', metavar='FILE', help='Export configuration')
    parser.add_argument('--import', dest='import_file', metavar='FILE',
                        help='Import configuration')
    parser.add_argument('--no-merge', action='store_true', 
                        help='Replace instead of merge (with --import)')
    parser.add_argument('--reset', action='store_true', help='Reset to defaults')
    
    # Output
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    # Initialize config manager
    config = ConfigManager(config_dir=args.config_dir)
    
    # Show full config
    if args.show:
        if args.json:
            print(json.dumps(config.get_all(), indent=2))
        else:
            print("NetScan Configuration")
            print("=" * 50)
            print(f"Config directory: {config.config_dir}")
            print("")
            
            def print_dict(d, indent=0):
                for key, value in d.items():
                    if isinstance(value, dict):
                        print("  " * indent + f"{key}:")
                        print_dict(value, indent + 1)
                    else:
                        print("  " * indent + f"{key}: {value}")
            
            print_dict(config.get_all())
        return 0
    
    # Get config value
    if args.get:
        value = config.get(args.get)
        if args.json:
            print(json.dumps({'key': args.get, 'value': value}))
        else:
            print(f"{args.get} = {value}")
        return 0
    
    # Set config value
    if args.set:
        key, value = args.set
        # Try to parse value as JSON
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            # Keep as string
            pass
        config.set(key, value)
        print(f"✓ Set {key} = {value}")
        return 0
    
    # Add device
    if args.add_device:
        mac, name = args.add_device
        device = config.add_known_device(
            mac, name,
            device_type=args.type or "",
            is_trusted=args.trusted
        )
        print(f"✓ Added device: {device.mac} ({device.name})")
        return 0
    
    # Remove device
    if args.remove_device:
        config.remove_known_device(args.remove_device)
        print(f"✓ Removed device: {args.remove_device}")
        return 0
    
    # List devices
    if args.list_devices:
        devices = config.list_known_devices()
        if args.json:
            print(json.dumps([d.to_dict() for d in devices], indent=2))
        else:
            print(f"\nKnown Devices ({len(devices)}):")
            print("-" * 70)
            for d in devices:
                trusted = "✓" if d.is_trusted else " "
                dtype = f"[{d.device_type}]" if d.device_type else ""
                print(f"  [{trusted}] {d.mac}  {d.name} {dtype}")
        return 0
    
    # OUI management
    if args.add_oui:
        oui, vendor = args.add_oui
        config.add_oui(oui, vendor)
        print(f"✓ Added OUI: {oui} -> {vendor}")
        return 0
    
    if args.remove_oui:
        config.remove_oui(args.remove_oui)
        print(f"✓ Removed OUI: {args.remove_oui}")
        return 0
    
    if args.list_ouis:
        ouis = config.list_custom_ouis()
        if args.json:
            print(json.dumps(ouis, indent=2))
        else:
            print(f"\nCustom OUIs ({len(ouis)}):")
            print("-" * 50)
            for oui, vendor in ouis.items():
                print(f"  {oui}  {vendor}")
        return 0
    
    # Exclusions
    if args.exclude_mac:
        config.exclude_mac(args.exclude_mac)
        print(f"✓ Excluded MAC: {args.exclude_mac}")
        return 0
    
    if args.include_mac:
        config.include_mac(args.include_mac)
        print(f"✓ Removed MAC from exclusions: {args.include_mac}")
        return 0
    
    if args.exclude_ip:
        config.exclude_ip(args.exclude_ip)
        print(f"✓ Excluded IP: {args.exclude_ip}")
        return 0
    
    if args.include_ip:
        config.include_ip(args.include_ip)
        print(f"✓ Removed IP from exclusions: {args.include_ip}")
        return 0
    
    if args.list_exclusions:
        exclusions = config.list_exclusions()
        if args.json:
            print(json.dumps(exclusions, indent=2))
        else:
            print("\nExcluded MACs:")
            for mac in exclusions['macs']:
                print(f"  {mac}")
            print("\nExcluded IPs:")
            for ip in exclusions['ips']:
                print(f"  {ip}")
        return 0
    
    # Import/Export
    if args.export:
        config.export_config(args.export)
        print(f"✓ Exported configuration to: {args.export}")
        return 0
    
    if args.import_file:
        config.import_config(args.import_file, merge=not args.no_merge)
        print(f"✓ Imported configuration from: {args.import_file}")
        return 0
    
    if args.reset:
        config.reset_to_defaults()
        print("✓ Reset configuration to defaults")
        return 0
    
    # Default: show help
    parser.print_help()
    return 0


if __name__ == '__main__':
    sys.exit(main())
