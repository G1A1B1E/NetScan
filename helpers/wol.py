#!/usr/bin/env python3
"""
NetScan Wake-on-LAN Module
Wake devices remotely using magic packets

Features:
- Send WoL magic packets
- Support multiple MAC formats
- Broadcast and directed wake
- Favorite devices management
- Bulk wake operations
"""

import socket
import struct
import re
import json
import os
import sys
import argparse
import time
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class WoLDevice:
    """A saved Wake-on-LAN device"""
    name: str
    mac: str
    ip: str = ""
    broadcast: str = "255.255.255.255"
    port: int = 9
    last_wake: str = ""
    notes: str = ""
    
    def to_dict(self) -> dict:
        return asdict(self)


class WakeOnLAN:
    """Wake-on-LAN implementation"""
    
    # Default WoL ports
    DEFAULT_PORT = 9
    ALT_PORT = 7
    
    def __init__(self, favorites_file: str = None):
        """
        Initialize WoL
        
        Args:
            favorites_file: Path to favorites JSON file
        """
        if favorites_file:
            self.favorites_file = Path(favorites_file)
        else:
            # Default location
            cache_dir = Path(__file__).parent.parent / 'cache'
            cache_dir.mkdir(exist_ok=True)
            self.favorites_file = cache_dir / 'wol_favorites.json'
        
        self.favorites: Dict[str, WoLDevice] = {}
        self._load_favorites()
    
    @staticmethod
    def normalize_mac(mac: str) -> str:
        """
        Normalize MAC address to consistent format
        
        Args:
            mac: MAC in any format (00:11:22:33:44:55, 00-11-22-33-44-55, etc.)
        
        Returns:
            Normalized MAC (lowercase, no separators)
        """
        # Remove all separators and convert to lowercase
        clean = re.sub(r'[-:.]', '', mac.lower())
        
        if len(clean) != 12:
            raise ValueError(f"Invalid MAC address: {mac}")
        
        # Validate hex
        try:
            int(clean, 16)
        except ValueError:
            raise ValueError(f"Invalid MAC address: {mac}")
        
        return clean
    
    @staticmethod
    def format_mac(mac: str, separator: str = ':') -> str:
        """Format MAC address with separator"""
        clean = WakeOnLAN.normalize_mac(mac)
        return separator.join(clean[i:i+2] for i in range(0, 12, 2))
    
    @staticmethod
    def create_magic_packet(mac: str) -> bytes:
        """
        Create a Wake-on-LAN magic packet
        
        The magic packet consists of:
        - 6 bytes of 0xFF
        - The target MAC address repeated 16 times
        
        Args:
            mac: Target MAC address
        
        Returns:
            Magic packet as bytes
        """
        # Normalize MAC
        clean_mac = WakeOnLAN.normalize_mac(mac)
        
        # Convert to bytes
        mac_bytes = bytes.fromhex(clean_mac)
        
        # Create magic packet
        # 6 bytes of 0xFF followed by MAC repeated 16 times
        magic_packet = b'\xff' * 6 + mac_bytes * 16
        
        return magic_packet
    
    def wake(self, mac: str, ip: str = "255.255.255.255", 
             port: int = DEFAULT_PORT, interface: str = None) -> bool:
        """
        Send Wake-on-LAN magic packet
        
        Args:
            mac: Target MAC address
            ip: Broadcast IP (default: 255.255.255.255)
            port: UDP port (default: 9)
            interface: Network interface to use (optional)
        
        Returns:
            True if packet was sent successfully
        """
        try:
            # Create magic packet
            packet = self.create_magic_packet(mac)
            
            # Create UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            # Bind to specific interface if requested
            if interface:
                try:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, 
                                   interface.encode())
                except (AttributeError, OSError):
                    # SO_BINDTODEVICE not available on all platforms
                    pass
            
            # Send packet
            sock.sendto(packet, (ip, port))
            
            # Also try alternate port
            if port == self.DEFAULT_PORT:
                sock.sendto(packet, (ip, self.ALT_PORT))
            
            sock.close()
            return True
        
        except Exception as e:
            print(f"Error sending WoL packet: {e}", file=sys.stderr)
            return False
    
    def wake_multiple(self, macs: List[str], **kwargs) -> Dict[str, bool]:
        """
        Wake multiple devices
        
        Args:
            macs: List of MAC addresses
            **kwargs: Additional arguments for wake()
        
        Returns:
            Dict mapping MAC to success status
        """
        results = {}
        for mac in macs:
            results[mac] = self.wake(mac, **kwargs)
            time.sleep(0.1)  # Small delay between packets
        return results
    
    def wake_by_name(self, name: str) -> bool:
        """
        Wake a device by its saved name
        
        Args:
            name: Favorite device name
        
        Returns:
            True if successful
        """
        if name not in self.favorites:
            print(f"Unknown device: {name}", file=sys.stderr)
            return False
        
        device = self.favorites[name]
        success = self.wake(device.mac, device.broadcast, device.port)
        
        if success:
            # Update last wake time
            from datetime import datetime
            device.last_wake = datetime.now().isoformat()
            self._save_favorites()
        
        return success
    
    # Favorites management
    
    def _load_favorites(self):
        """Load favorites from file"""
        if self.favorites_file.exists():
            try:
                with open(self.favorites_file, 'r') as f:
                    data = json.load(f)
                
                for name, device_data in data.items():
                    self.favorites[name] = WoLDevice(**device_data)
            
            except Exception as e:
                print(f"Error loading favorites: {e}", file=sys.stderr)
    
    def _save_favorites(self):
        """Save favorites to file"""
        try:
            data = {name: device.to_dict() for name, device in self.favorites.items()}
            
            with open(self.favorites_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        except Exception as e:
            print(f"Error saving favorites: {e}", file=sys.stderr)
    
    def add_favorite(self, name: str, mac: str, ip: str = "", 
                    broadcast: str = "255.255.255.255", port: int = DEFAULT_PORT,
                    notes: str = "") -> WoLDevice:
        """
        Add a device to favorites
        
        Args:
            name: Friendly name for device
            mac: MAC address
            ip: IP address (optional, for reference)
            broadcast: Broadcast address
            port: WoL port
            notes: Optional notes
        
        Returns:
            Created WoLDevice
        """
        device = WoLDevice(
            name=name,
            mac=self.format_mac(mac),
            ip=ip,
            broadcast=broadcast,
            port=port,
            notes=notes
        )
        
        self.favorites[name] = device
        self._save_favorites()
        
        return device
    
    def remove_favorite(self, name: str) -> bool:
        """Remove a device from favorites"""
        if name in self.favorites:
            del self.favorites[name]
            self._save_favorites()
            return True
        return False
    
    def list_favorites(self) -> List[WoLDevice]:
        """Get list of all favorites"""
        return list(self.favorites.values())
    
    def get_favorite(self, name: str) -> Optional[WoLDevice]:
        """Get a favorite by name"""
        return self.favorites.get(name)


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Wake-on-LAN - Wake devices remotely',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Wake by MAC address
  python wol.py 00:11:22:33:44:55
  python wol.py 00-11-22-33-44-55
  
  # Wake with specific broadcast
  python wol.py AA:BB:CC:DD:EE:FF -b 192.168.1.255
  
  # Wake multiple devices
  python wol.py MAC1 MAC2 MAC3
  
  # Manage favorites
  python wol.py --add "Desktop" 00:11:22:33:44:55
  python wol.py --wake "Desktop"
  python wol.py --list
  python wol.py --remove "Desktop"
        '''
    )
    
    # Wake options
    parser.add_argument('mac', nargs='*', help='MAC address(es) to wake')
    parser.add_argument('--mac', dest='mac_opt', metavar='MAC',
                       help='MAC address to wake (alternative)')
    parser.add_argument('-b', '--broadcast', default='255.255.255.255',
                       help='Broadcast address (default: 255.255.255.255)')
    parser.add_argument('-p', '--port', type=int, default=9,
                       help='WoL port (default: 9)')
    parser.add_argument('-i', '--interface', help='Network interface')
    
    # Favorites (with aliases for shell integration)
    parser.add_argument('--add', nargs=2, metavar=('NAME', 'MAC'),
                       help='Add device to favorites')
    parser.add_argument('--add-favorite', nargs='+', metavar='ARG',
                       help='Add device to favorites (name mac [--description desc])')
    parser.add_argument('--remove', metavar='NAME',
                       help='Remove device from favorites')
    parser.add_argument('--remove-favorite', metavar='NAME',
                       help='Remove device from favorites')
    parser.add_argument('--wake', '-w', metavar='NAME',
                       help='Wake device by name')
    parser.add_argument('--wake-favorite', metavar='NAME',
                       help='Wake device by name')
    parser.add_argument('--wake-all', action='store_true',
                       help='Wake all favorites')
    parser.add_argument('--list', '-l', action='store_true',
                       help='List favorite devices')
    parser.add_argument('--list-favorites', action='store_true',
                       help='List favorite devices')
    parser.add_argument('--json', '-j', action='store_true',
                       help='Output as JSON')
    parser.add_argument('--description', metavar='DESC',
                       help='Description for add-favorite')
    
    # Info
    parser.add_argument('--test', action='store_true',
                       help='Test mode - show packet without sending')
    
    args = parser.parse_args()
    
    wol = WakeOnLAN()
    
    # Combine mac arguments
    macs = args.mac or []
    if args.mac_opt:
        macs.append(args.mac_opt)
    
    # List favorites (both flags)
    if args.list or args.list_favorites:
        favorites = wol.list_favorites()
        
        if args.json:
            print(json.dumps([f.to_dict() for f in favorites], indent=2))
        else:
            if not favorites:
                print("No favorite devices saved.")
            else:
                print(f"\n{'Name':<20} {'MAC Address':<20} {'IP':<16} {'Last Wake':<20}")
                print("-" * 76)
                for f in favorites:
                    last_wake = f.last_wake[:19] if f.last_wake else 'Never'
                    print(f"{f.name:<20} {f.mac:<20} {f.ip or 'N/A':<16} {last_wake:<20}")
        return 0
    
    # Add favorite (both --add and --add-favorite)
    if args.add:
        name, mac = args.add
        device = wol.add_favorite(
            name=name,
            mac=mac,
            broadcast=args.broadcast,
            port=args.port
        )
        print(f"✓ Added: {name} ({device.mac})")
        return 0
    
    if args.add_favorite:
        if len(args.add_favorite) >= 2:
            name = args.add_favorite[0]
            mac = args.add_favorite[1]
            desc = args.description or (args.add_favorite[2] if len(args.add_favorite) > 2 else None)
            device = wol.add_favorite(
                name=name,
                mac=mac,
                description=desc,
                broadcast=args.broadcast,
                port=args.port
            )
            print(f"✓ Added: {name} ({device.mac})")
        else:
            print("Usage: --add-favorite NAME MAC [--description DESC]")
            return 1
        return 0
    
    # Remove favorite (both --remove and --remove-favorite)
    if args.remove or args.remove_favorite:
        name = args.remove or args.remove_favorite
        if wol.remove_favorite(name):
            print(f"✓ Removed: {name}")
        else:
            print(f"✗ Not found: {name}")
            return 1
        return 0
    
    # Wake all favorites
    if args.wake_all:
        favorites = wol.list_favorites()
        if not favorites:
            print("No favorites to wake.")
            return 0
        print(f"Waking {len(favorites)} devices...")
        results = wol.wake_multiple([f.mac for f in favorites])
        for mac, success in results:
            status = "✓" if success else "✗"
            name = next((f.name for f in favorites if f.mac.lower().replace(':', '').replace('-', '') == 
                        mac.lower().replace(':', '').replace('-', '')), mac)
            print(f"  {status} {name}")
        return 0
    
    # Wake by name (both --wake and --wake-favorite)
    if args.wake or args.wake_favorite:
        name = args.wake or args.wake_favorite
        print(f"Waking {name}...")
        if wol.wake_by_name(name):
            print(f"✓ Magic packet sent to {name}")
        else:
            return 1
        return 0
    
    # Wake by MAC
    if macs:
        for mac in macs:
            # Check if it's a favorite name
            favorite = wol.get_favorite(mac)
            if favorite:
                target_mac = favorite.mac
                broadcast = favorite.broadcast
                port = favorite.port
                print(f"Waking {mac} ({target_mac})...")
            else:
                target_mac = mac
                broadcast = args.broadcast
                port = args.port
                print(f"Waking {mac}...")
            
            if args.test:
                # Show packet hex
                packet = WakeOnLAN.create_magic_packet(target_mac)
                print(f"  Packet ({len(packet)} bytes): {packet.hex()}")
                print(f"  Target: {broadcast}:{port}")
            else:
                if wol.wake(target_mac, broadcast, port, args.interface):
                    print(f"✓ Magic packet sent")
                else:
                    print(f"✗ Failed to send packet")
                    return 1
        return 0
    
    # No arguments
    parser.print_help()
    return 0


if __name__ == '__main__':
    sys.exit(main())
