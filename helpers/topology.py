#!/usr/bin/env python3
"""
NetScan Network Topology Module
Visualize network topology as ASCII art, DOT graphs, or JSON

Features:
- Gateway/router detection
- Network segment mapping
- Device relationship inference
- Multiple output formats (ASCII, DOT/Graphviz, JSON, HTML)
"""

import os
import sys
import json
import argparse
import subprocess
import socket
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict, field
from collections import defaultdict
from pathlib import Path


@dataclass
class NetworkNode:
    """A node in the network topology"""
    ip: str
    mac: str = ""
    hostname: str = ""
    vendor: str = ""
    node_type: str = "host"  # gateway, router, switch, host, unknown
    ports: List[int] = field(default_factory=list)
    connections: List[str] = field(default_factory=list)  # Connected IPs
    is_gateway: bool = False
    subnet: str = ""
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass 
class NetworkTopology:
    """Complete network topology"""
    gateway: Optional[NetworkNode] = None
    nodes: Dict[str, NetworkNode] = field(default_factory=dict)
    subnets: Dict[str, List[str]] = field(default_factory=dict)
    scan_time: str = ""
    
    def to_dict(self) -> dict:
        return {
            'gateway': self.gateway.to_dict() if self.gateway else None,
            'nodes': {ip: node.to_dict() for ip, node in self.nodes.items()},
            'subnets': self.subnets,
            'scan_time': self.scan_time
        }


class TopologyMapper:
    """Map network topology"""
    
    # Port signatures for device type detection
    ROUTER_PORTS = {22, 23, 53, 67, 80, 443, 8080}
    SWITCH_PORTS = {22, 23, 80, 161}  # SNMP common on switches
    
    def __init__(self):
        self.topology = NetworkTopology()
        self._local_ip = ""
        self._gateway_ip = ""
    
    def get_local_network_info(self) -> Tuple[str, str, str]:
        """Get local IP, gateway IP, and subnet"""
        try:
            # Get default gateway
            if sys.platform == "darwin":
                result = subprocess.run(
                    ['route', '-n', 'get', 'default'],
                    capture_output=True, text=True
                )
                for line in result.stdout.split('\n'):
                    if 'gateway:' in line:
                        self._gateway_ip = line.split(':')[1].strip()
                        break
            else:
                result = subprocess.run(
                    ['ip', 'route', 'show', 'default'],
                    capture_output=True, text=True
                )
                parts = result.stdout.split()
                if 'via' in parts:
                    self._gateway_ip = parts[parts.index('via') + 1]
            
            # Get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(('8.8.8.8', 80))
                self._local_ip = s.getsockname()[0]
            finally:
                s.close()
            
            # Calculate subnet
            parts = self._local_ip.split('.')
            subnet = f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
            
            return self._local_ip, self._gateway_ip, subnet
            
        except Exception as e:
            print(f"Warning: Could not get network info: {e}", file=sys.stderr)
            return "192.168.1.1", "192.168.1.1", "192.168.1.0/24"
    
    def get_mac_for_ip(self, ip: str) -> str:
        """Get MAC address for an IP using ARP"""
        try:
            if sys.platform == "darwin":
                result = subprocess.run(
                    ['arp', '-n', ip],
                    capture_output=True, text=True
                )
                for line in result.stdout.split('\n'):
                    if ip in line:
                        parts = line.split()
                        for part in parts:
                            if ':' in part and len(part) == 17:
                                return part.upper()
            else:
                result = subprocess.run(
                    ['arp', '-n', ip],
                    capture_output=True, text=True
                )
                for line in result.stdout.split('\n'):
                    if ip in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            return parts[2].upper()
        except:
            pass
        return ""
    
    def detect_device_type(self, node: NetworkNode) -> str:
        """Detect device type based on ports and characteristics"""
        if node.is_gateway:
            return "gateway"
        
        ports_set = set(node.ports)
        
        # Check for router characteristics
        if ports_set & self.ROUTER_PORTS:
            if 53 in ports_set or 67 in ports_set:  # DNS or DHCP
                return "router"
        
        # Check for switch (SNMP)
        if 161 in ports_set and not (80 in ports_set and 443 in ports_set):
            return "switch"
        
        # Check vendor for hints
        vendor_lower = node.vendor.lower()
        if any(x in vendor_lower for x in ['cisco', 'juniper', 'netgear', 'ubiquiti', 'mikrotik']):
            if 80 in ports_set or 443 in ports_set:
                return "router"
        
        return "host"
    
    def build_topology(self, devices: List[dict], scan_ports: bool = False) -> NetworkTopology:
        """Build network topology from device list"""
        from datetime import datetime
        
        self.topology = NetworkTopology()
        self.topology.scan_time = datetime.now().isoformat()
        
        # Get network info
        local_ip, gateway_ip, subnet = self.get_local_network_info()
        
        # Process devices
        for device in devices:
            ip = device.get('ip', '')
            if not ip:
                continue
            
            mac = device.get('mac', '') or self.get_mac_for_ip(ip)
            
            node = NetworkNode(
                ip=ip,
                mac=mac,
                hostname=device.get('hostname', ''),
                vendor=device.get('vendor', ''),
                ports=device.get('ports', []),
                is_gateway=(ip == gateway_ip),
                subnet=subnet
            )
            
            # Detect device type
            node.node_type = self.detect_device_type(node)
            
            self.topology.nodes[ip] = node
            
            # Track gateway
            if ip == gateway_ip:
                self.topology.gateway = node
        
        # If gateway not in devices, add it
        if gateway_ip and gateway_ip not in self.topology.nodes:
            gateway_mac = self.get_mac_for_ip(gateway_ip)
            gateway_node = NetworkNode(
                ip=gateway_ip,
                mac=gateway_mac,
                node_type="gateway",
                is_gateway=True,
                subnet=subnet
            )
            self.topology.nodes[gateway_ip] = gateway_node
            self.topology.gateway = gateway_node
        
        # Group by subnet
        self.topology.subnets[subnet] = list(self.topology.nodes.keys())
        
        # Infer connections (all connect to gateway in simple topology)
        if self.topology.gateway:
            for ip, node in self.topology.nodes.items():
                if ip != gateway_ip:
                    node.connections = [gateway_ip]
        
        return self.topology
    
    def render_ascii(self, topology: Optional[NetworkTopology] = None) -> str:
        """Render topology as ASCII art"""
        topo = topology or self.topology
        
        if not topo.nodes:
            return "No nodes in topology"
        
        lines = []
        lines.append("")
        lines.append("=" * 70)
        lines.append("  NETWORK TOPOLOGY")
        lines.append("=" * 70)
        lines.append("")
        
        # Internet
        lines.append("                        ☁️  INTERNET")
        lines.append("                            │")
        lines.append("                            │")
        
        # Gateway
        if topo.gateway:
            gw = topo.gateway
            lines.append("                    ┌───────┴───────┐")
            lines.append(f"                    │   🌐 GATEWAY  │")
            lines.append(f"                    │  {gw.ip:^13} │")
            if gw.mac:
                lines.append(f"                    │  {gw.mac:^13} │")
            lines.append("                    └───────┬───────┘")
            lines.append("                            │")
        
        # LAN
        lines.append("        ────────────────────┼────────────────────")
        lines.append("                      LOCAL NETWORK")
        lines.append("")
        
        # Get all hosts (non-gateway)
        hosts = [n for ip, n in topo.nodes.items() if not n.is_gateway]
        
        # Group by type
        routers = [h for h in hosts if h.node_type == "router"]
        switches = [h for h in hosts if h.node_type == "switch"]
        regular_hosts = [h for h in hosts if h.node_type == "host"]
        
        # Display routers
        if routers:
            lines.append("  📡 ROUTERS/APs:")
            for node in routers:
                name = node.hostname or node.vendor or node.ip
                lines.append(f"    ├── {node.ip:15} {name[:25]}")
            lines.append("")
        
        # Display switches
        if switches:
            lines.append("  🔀 SWITCHES:")
            for node in switches:
                name = node.hostname or node.vendor or node.ip
                lines.append(f"    ├── {node.ip:15} {name[:25]}")
            lines.append("")
        
        # Display hosts
        if regular_hosts:
            lines.append("  💻 HOSTS:")
            for i, node in enumerate(regular_hosts):
                name = node.hostname or node.vendor or "Unknown"
                prefix = "└──" if i == len(regular_hosts) - 1 else "├──"
                mac_short = node.mac[:8] if node.mac else ""
                lines.append(f"    {prefix} {node.ip:15} {mac_short:10} {name[:30]}")
        
        lines.append("")
        lines.append("=" * 70)
        lines.append(f"  Total devices: {len(topo.nodes)} | Gateway: {topo.gateway.ip if topo.gateway else 'Unknown'}")
        lines.append("=" * 70)
        lines.append("")
        
        return "\n".join(lines)
    
    def render_dot(self, topology: Optional[NetworkTopology] = None) -> str:
        """Render topology as DOT/Graphviz format"""
        topo = topology or self.topology
        
        lines = ['digraph network {']
        lines.append('    rankdir=TB;')
        lines.append('    node [shape=box, style=filled];')
        lines.append('    ')
        lines.append('    // Internet')
        lines.append('    internet [label="Internet\\n☁️", shape=cloud, fillcolor="#e3f2fd"];')
        lines.append('    ')
        
        # Gateway
        if topo.gateway:
            gw = topo.gateway
            label = f"Gateway\\n{gw.ip}"
            if gw.vendor:
                label += f"\\n{gw.vendor[:20]}"
            lines.append(f'    gateway [label="{label}", fillcolor="#c8e6c9"];')
            lines.append('    internet -> gateway;')
            lines.append('    ')
        
        # Hosts
        lines.append('    // Hosts')
        for ip, node in topo.nodes.items():
            if node.is_gateway:
                continue
            
            # Node ID (sanitize IP)
            node_id = ip.replace('.', '_')
            
            # Label
            label = ip
            if node.hostname:
                label = f"{node.hostname}\\n{ip}"
            elif node.vendor:
                label = f"{ip}\\n{node.vendor[:15]}"
            
            # Color by type
            colors = {
                'router': '#fff9c4',
                'switch': '#f3e5f5',
                'host': '#e8f5e9',
                'unknown': '#f5f5f5'
            }
            color = colors.get(node.node_type, '#f5f5f5')
            
            lines.append(f'    {node_id} [label="{label}", fillcolor="{color}"];')
            
            # Connect to gateway
            if topo.gateway:
                lines.append(f'    gateway -> {node_id};')
        
        lines.append('}')
        
        return '\n'.join(lines)
    
    def render_html(self, topology: Optional[NetworkTopology] = None) -> str:
        """Render topology as interactive HTML using vis.js"""
        topo = topology or self.topology
        
        # Prepare nodes data
        nodes_data = []
        edges_data = []
        
        # Internet node
        nodes_data.append({
            'id': 'internet',
            'label': 'Internet',
            'shape': 'cloud',
            'color': '#2196f3',
            'font': {'color': 'white'}
        })
        
        # Gateway
        if topo.gateway:
            gw = topo.gateway
            nodes_data.append({
                'id': gw.ip,
                'label': f"Gateway\\n{gw.ip}",
                'shape': 'box',
                'color': '#4caf50'
            })
            edges_data.append({'from': 'internet', 'to': gw.ip})
        
        # Hosts
        colors = {
            'router': '#ff9800',
            'switch': '#9c27b0',
            'host': '#03a9f4',
            'unknown': '#9e9e9e'
        }
        
        for ip, node in topo.nodes.items():
            if node.is_gateway:
                continue
            
            label = node.hostname or node.vendor or ip
            if label != ip:
                label = f"{label}\\n{ip}"
            
            nodes_data.append({
                'id': ip,
                'label': label,
                'shape': 'box',
                'color': colors.get(node.node_type, '#9e9e9e')
            })
            
            if topo.gateway:
                edges_data.append({'from': topo.gateway.ip, 'to': ip})
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <title>Network Topology - NetScan</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        .info {{
            color: #666;
            margin-bottom: 20px;
        }}
        #network {{
            width: 100%;
            height: 600px;
            border: 1px solid #ddd;
            background: white;
            border-radius: 8px;
        }}
        .legend {{
            display: flex;
            gap: 20px;
            margin-top: 15px;
            flex-wrap: wrap;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <h1>🌐 Network Topology</h1>
    <div class="info">
        Scanned: {topo.scan_time[:19] if topo.scan_time else 'Unknown'} |
        Devices: {len(topo.nodes)} |
        Gateway: {topo.gateway.ip if topo.gateway else 'Unknown'}
    </div>
    <div id="network"></div>
    <div class="legend">
        <div class="legend-item"><div class="legend-color" style="background:#4caf50"></div> Gateway</div>
        <div class="legend-item"><div class="legend-color" style="background:#ff9800"></div> Router/AP</div>
        <div class="legend-item"><div class="legend-color" style="background:#9c27b0"></div> Switch</div>
        <div class="legend-item"><div class="legend-color" style="background:#03a9f4"></div> Host</div>
    </div>
    <script type="text/javascript">
        var nodes = new vis.DataSet({json.dumps(nodes_data)});
        var edges = new vis.DataSet({json.dumps(edges_data)});
        var container = document.getElementById('network');
        var data = {{ nodes: nodes, edges: edges }};
        var options = {{
            layout: {{
                hierarchical: {{
                    direction: 'UD',
                    sortMethod: 'directed',
                    levelSeparation: 100
                }}
            }},
            physics: false,
            interaction: {{
                hover: true,
                tooltipDelay: 200
            }}
        }};
        var network = new vis.Network(container, data, options);
    </script>
</body>
</html>'''
        
        return html


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(
        description="NetScan Network Topology Mapper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python topology.py --input scan.json --ascii
  python topology.py --input scan.json --dot > network.dot
  python topology.py --input scan.json --html --output topology.html
  python topology.py --scan --ascii
        '''
    )
    
    # Input
    parser.add_argument('--input', '-i', metavar='FILE',
                       help='Input JSON file with scan results')
    parser.add_argument('--scan', '-s', action='store_true',
                       help='Perform network scan first')
    
    # Output format
    parser.add_argument('--ascii', '-a', action='store_true',
                       help='Output ASCII art topology')
    parser.add_argument('--dot', '-d', action='store_true',
                       help='Output DOT/Graphviz format')
    parser.add_argument('--html', action='store_true',
                       help='Output interactive HTML')
    parser.add_argument('--json', '-j', action='store_true',
                       help='Output JSON')
    
    # Output file
    parser.add_argument('--output', '-o', metavar='FILE',
                       help='Output file')
    
    args = parser.parse_args()
    
    mapper = TopologyMapper()
    devices = []
    
    # Load or scan devices
    if args.input:
        try:
            with open(args.input) as f:
                data = json.load(f)
            devices = data.get('devices', data) if isinstance(data, dict) else data
            print(f"Loaded {len(devices)} devices from {args.input}", file=sys.stderr)
        except Exception as e:
            print(f"Error loading input: {e}", file=sys.stderr)
            return 1
    
    elif args.scan:
        print("Performing network scan...", file=sys.stderr)
        # Quick ARP scan
        local_ip, gateway_ip, subnet = mapper.get_local_network_info()
        base = '.'.join(local_ip.split('.')[:3])
        
        # Ping sweep
        import concurrent.futures
        def ping(ip):
            try:
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', '1', ip],
                    capture_output=True, timeout=2
                )
                if result.returncode == 0:
                    return {'ip': ip}
            except:
                pass
            return None
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            results = list(executor.map(ping, [f"{base}.{i}" for i in range(1, 255)]))
            devices = [r for r in results if r]
        
        print(f"Found {len(devices)} devices", file=sys.stderr)
    
    else:
        parser.print_help()
        return 0
    
    # Build topology
    topology = mapper.build_topology(devices)
    
    # Render output
    if args.ascii:
        output = mapper.render_ascii()
    elif args.dot:
        output = mapper.render_dot()
    elif args.html:
        output = mapper.render_html()
    elif args.json:
        output = json.dumps(topology.to_dict(), indent=2)
    else:
        # Default to ASCII
        output = mapper.render_ascii()
    
    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Topology saved to {args.output}", file=sys.stderr)
        
        # Open HTML files
        if args.html:
            try:
                import webbrowser
                webbrowser.open(f"file://{os.path.abspath(args.output)}")
            except:
                pass
    else:
        print(output)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
