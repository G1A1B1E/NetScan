#!/usr/bin/env python3
"""
MAC Address Normalizer - Fast MAC address format handling
Supports multiple input/output formats and batch processing
"""

import re
import sys
import argparse
from typing import Optional, List, Tuple

# MAC address patterns
MAC_PATTERNS = [
    # Colon separated (AA:BB:CC:DD:EE:FF)
    re.compile(r'^([0-9A-Fa-f]{2}):([0-9A-Fa-f]{2}):([0-9A-Fa-f]{2}):([0-9A-Fa-f]{2}):([0-9A-Fa-f]{2}):([0-9A-Fa-f]{2})$'),
    # Dash separated (AA-BB-CC-DD-EE-FF)
    re.compile(r'^([0-9A-Fa-f]{2})-([0-9A-Fa-f]{2})-([0-9A-Fa-f]{2})-([0-9A-Fa-f]{2})-([0-9A-Fa-f]{2})-([0-9A-Fa-f]{2})$'),
    # Dot separated Cisco style (AABB.CCDD.EEFF)
    re.compile(r'^([0-9A-Fa-f]{4})\.([0-9A-Fa-f]{4})\.([0-9A-Fa-f]{4})$'),
    # No separator (AABBCCDDEEFF)
    re.compile(r'^([0-9A-Fa-f]{12})$'),
    # Space separated (AA BB CC DD EE FF)
    re.compile(r'^([0-9A-Fa-f]{2}) ([0-9A-Fa-f]{2}) ([0-9A-Fa-f]{2}) ([0-9A-Fa-f]{2}) ([0-9A-Fa-f]{2}) ([0-9A-Fa-f]{2})$'),
]

# OUI prefixes for common virtual/special MACs
SPECIAL_OUIS = {
    '000000': 'Null/Invalid',
    'ffffffffffff': 'Broadcast',
    '01005e': 'IPv4 Multicast',
    '333300': 'IPv6 Multicast',
    '0050c2': 'IEEE Registration Authority',
    '005056': 'VMware',
    '000c29': 'VMware',
    '000569': 'VMware',
    '080027': 'VirtualBox',
    '0a0027': 'VirtualBox',
    '525400': 'QEMU/KVM',
    'fe5400': 'QEMU/KVM',
    '00163e': 'Xen',
    '001c42': 'Parallels',
    '00155d': 'Hyper-V',
    '0003ff': 'Microsoft Hyper-V',
    '020000': 'Locally Administered',
}


def extract_hex(mac: str) -> Optional[str]:
    """Extract pure hex digits from any MAC format"""
    for pattern in MAC_PATTERNS:
        match = pattern.match(mac.strip())
        if match:
            groups = match.groups()
            if len(groups) == 1:
                # No separator format
                return groups[0].lower()
            elif len(groups) == 3:
                # Cisco format
                return ''.join(groups).lower()
            else:
                # 6 group formats
                return ''.join(groups).lower()
    return None


def is_valid_mac(mac: str) -> bool:
    """Check if string is a valid MAC address"""
    return extract_hex(mac) is not None


def normalize(mac: str, format: str = 'colon', uppercase: bool = False) -> Optional[str]:
    """
    Normalize MAC address to specified format
    
    Formats:
        colon: AA:BB:CC:DD:EE:FF
        dash:  AA-BB-CC-DD-EE-FF
        cisco: AABB.CCDD.EEFF
        bare:  AABBCCDDEEFF
        space: AA BB CC DD EE FF
    """
    hex_mac = extract_hex(mac)
    if not hex_mac:
        return None
    
    # Split into pairs
    pairs = [hex_mac[i:i+2] for i in range(0, 12, 2)]
    
    if format == 'colon':
        result = ':'.join(pairs)
    elif format == 'dash':
        result = '-'.join(pairs)
    elif format == 'cisco':
        result = f"{hex_mac[0:4]}.{hex_mac[4:8]}.{hex_mac[8:12]}"
    elif format == 'bare':
        result = hex_mac
    elif format == 'space':
        result = ' '.join(pairs)
    else:
        result = ':'.join(pairs)  # Default to colon
    
    return result.upper() if uppercase else result.lower()


def get_oui(mac: str) -> Optional[str]:
    """Extract OUI (first 3 bytes) from MAC address"""
    hex_mac = extract_hex(mac)
    if hex_mac:
        return hex_mac[:6]
    return None


def get_nic(mac: str) -> Optional[str]:
    """Extract NIC-specific part (last 3 bytes) from MAC address"""
    hex_mac = extract_hex(mac)
    if hex_mac:
        return hex_mac[6:]
    return None


def is_unicast(mac: str) -> bool:
    """Check if MAC is unicast (not multicast/broadcast)"""
    hex_mac = extract_hex(mac)
    if not hex_mac:
        return False
    # First byte, LSB determines unicast (0) vs multicast (1)
    first_byte = int(hex_mac[:2], 16)
    return (first_byte & 0x01) == 0


def is_multicast(mac: str) -> bool:
    """Check if MAC is multicast"""
    return not is_unicast(mac)


def is_local(mac: str) -> bool:
    """Check if MAC is locally administered (vs globally unique)"""
    hex_mac = extract_hex(mac)
    if not hex_mac:
        return False
    # Second bit of first byte determines local (1) vs global (0)
    first_byte = int(hex_mac[:2], 16)
    return (first_byte & 0x02) != 0


def is_global(mac: str) -> bool:
    """Check if MAC is globally administered (has real OUI)"""
    return not is_local(mac)


def is_special(mac: str) -> Tuple[bool, Optional[str]]:
    """Check if MAC is a special/virtual address"""
    hex_mac = extract_hex(mac)
    if not hex_mac:
        return False, None
    
    # Check full MAC first (broadcast)
    if hex_mac in SPECIAL_OUIS:
        return True, SPECIAL_OUIS[hex_mac]
    
    # Check OUI
    oui = hex_mac[:6]
    if oui in SPECIAL_OUIS:
        return True, SPECIAL_OUIS[oui]
    
    return False, None


def analyze(mac: str) -> dict:
    """Perform complete analysis of a MAC address"""
    hex_mac = extract_hex(mac)
    if not hex_mac:
        return {'valid': False, 'input': mac}
    
    is_sp, sp_type = is_special(mac)
    
    return {
        'valid': True,
        'input': mac,
        'normalized': normalize(mac, 'colon'),
        'oui': get_oui(mac),
        'nic': get_nic(mac),
        'unicast': is_unicast(mac),
        'multicast': is_multicast(mac),
        'local': is_local(mac),
        'global': is_global(mac),
        'special': is_sp,
        'special_type': sp_type,
        'formats': {
            'colon': normalize(mac, 'colon'),
            'dash': normalize(mac, 'dash'),
            'cisco': normalize(mac, 'cisco'),
            'bare': normalize(mac, 'bare'),
            'upper': normalize(mac, 'colon', uppercase=True),
        }
    }


def batch_normalize(macs: List[str], format: str = 'colon', uppercase: bool = False) -> List[Tuple[str, Optional[str]]]:
    """Normalize multiple MAC addresses at once"""
    return [(mac, normalize(mac, format, uppercase)) for mac in macs]


def find_macs_in_text(text: str) -> List[str]:
    """Find all MAC addresses in arbitrary text"""
    results = []
    
    # Try to find MAC patterns in the text
    # Colon format
    results.extend(re.findall(r'[0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){5}', text))
    # Dash format
    results.extend(re.findall(r'[0-9A-Fa-f]{2}(?:-[0-9A-Fa-f]{2}){5}', text))
    # Cisco format
    results.extend(re.findall(r'[0-9A-Fa-f]{4}(?:\.[0-9A-Fa-f]{4}){2}', text))
    
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for mac in results:
        hex_mac = extract_hex(mac)
        if hex_mac and hex_mac not in seen:
            seen.add(hex_mac)
            unique.append(mac)
    
    return unique


def main():
    parser = argparse.ArgumentParser(
        description='MAC Address Normalizer - Fast MAC address format handling',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s AA:BB:CC:DD:EE:FF                    # Normalize single MAC
  %(prog)s -f dash AA:BB:CC:DD:EE:FF            # Convert to dash format
  %(prog)s -u AA:BB:CC:DD:EE:FF                 # Uppercase output
  %(prog)s --analyze AA:BB:CC:DD:EE:FF          # Full analysis
  %(prog)s --validate AA:BB:CC:DD:EE:FF         # Validate MAC
  %(prog)s --batch < macs.txt                   # Batch process from stdin
  %(prog)s --find-in-text < logfile.txt         # Extract MACs from text

Formats:
  colon  AA:BB:CC:DD:EE:FF  (default)
  dash   AA-BB-CC-DD-EE-FF
  cisco  AABB.CCDD.EEFF
  bare   AABBCCDDEEFF
  space  AA BB CC DD EE FF
        """
    )
    
    parser.add_argument('mac', nargs='?', help='MAC address to process')
    parser.add_argument('-f', '--format', choices=['colon', 'dash', 'cisco', 'bare', 'space'],
                        default='colon', help='Output format (default: colon)')
    parser.add_argument('-u', '--uppercase', action='store_true',
                        help='Output in uppercase')
    parser.add_argument('--analyze', action='store_true',
                        help='Show detailed analysis')
    parser.add_argument('--validate', action='store_true',
                        help='Only validate (exit 0 if valid, 1 if invalid)')
    parser.add_argument('--oui', action='store_true',
                        help='Extract OUI only')
    parser.add_argument('--batch', action='store_true',
                        help='Process multiple MACs from stdin')
    parser.add_argument('--find-in-text', action='store_true',
                        help='Find and extract MAC addresses from text on stdin')
    parser.add_argument('--json', action='store_true',
                        help='Output in JSON format')
    parser.add_argument('--help-formats', action='store_true',
                        help='Show supported input formats')
    
    args = parser.parse_args()
    
    if args.help_formats:
        print("Supported input formats:")
        print("  Colon:    AA:BB:CC:DD:EE:FF")
        print("  Dash:     AA-BB-CC-DD-EE-FF")
        print("  Cisco:    AABB.CCDD.EEFF")
        print("  Bare:     AABBCCDDEEFF")
        print("  Space:    AA BB CC DD EE FF")
        print("\nCase insensitive, leading/trailing whitespace ignored")
        return 0
    
    # Find MACs in text mode
    if args.find_in_text:
        text = sys.stdin.read()
        macs = find_macs_in_text(text)
        for mac in macs:
            print(normalize(mac, args.format, args.uppercase))
        return 0
    
    # Batch processing mode
    if args.batch:
        import json
        results = []
        for line in sys.stdin:
            mac = line.strip()
            if not mac:
                continue
            
            if args.analyze:
                result = analyze(mac)
            else:
                normalized = normalize(mac, args.format, args.uppercase)
                result = {'input': mac, 'output': normalized, 'valid': normalized is not None}
            
            if args.json:
                results.append(result)
            else:
                if args.analyze:
                    print(f"{mac} -> {result}")
                elif result['valid']:
                    print(result['output'])
                else:
                    print(f"INVALID: {mac}", file=sys.stderr)
        
        if args.json:
            print(json.dumps(results, indent=2))
        return 0
    
    # Single MAC processing
    if not args.mac:
        parser.print_help()
        return 1
    
    mac = args.mac.strip()
    
    # Validation only
    if args.validate:
        return 0 if is_valid_mac(mac) else 1
    
    # OUI extraction
    if args.oui:
        oui = get_oui(mac)
        if oui:
            print(oui if not args.uppercase else oui.upper())
            return 0
        else:
            print("Invalid MAC address", file=sys.stderr)
            return 1
    
    # Full analysis
    if args.analyze:
        import json
        result = analyze(mac)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if not result['valid']:
                print(f"Invalid MAC address: {mac}", file=sys.stderr)
                return 1
            
            print(f"Input:      {result['input']}")
            print(f"Normalized: {result['normalized']}")
            print(f"OUI:        {result['oui']}")
            print(f"NIC:        {result['nic']}")
            print(f"Type:       {'Unicast' if result['unicast'] else 'Multicast'}")
            print(f"Admin:      {'Locally administered' if result['local'] else 'Globally unique'}")
            if result['special']:
                print(f"Special:    {result['special_type']}")
            print(f"\nAll formats:")
            for fmt, val in result['formats'].items():
                print(f"  {fmt}: {val}")
        return 0
    
    # Simple normalization
    result = normalize(mac, args.format, args.uppercase)
    if result:
        print(result)
        return 0
    else:
        print(f"Invalid MAC address: {mac}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
