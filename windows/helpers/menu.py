#!/usr/bin/env python3
"""
NetScan Windows Menu Module
Interactive menu for Windows version
"""

import os
import sys
import subprocess
import json
from typing import Optional, Callable, List, Dict

# Check if colorama is available for colored output
try:
    from colorama import init, Fore, Style
    init()
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False


class Colors:
    """Terminal colors (with fallback for no colorama)"""
    if HAS_COLOR:
        HEADER = Fore.CYAN + Style.BRIGHT
        BLUE = Fore.BLUE
        GREEN = Fore.GREEN
        YELLOW = Fore.YELLOW
        RED = Fore.RED
        RESET = Style.RESET_ALL
        BOLD = Style.BRIGHT
    else:
        HEADER = BLUE = GREEN = YELLOW = RED = RESET = BOLD = ''


class Menu:
    """Interactive menu system"""
    
    def __init__(self, title: str = "NetScan"):
        self.title = title
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.parent_dir = os.path.dirname(self.script_dir)
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if sys.platform == 'win32' else 'clear')
    
    def print_header(self, subtitle: str = ""):
        """Print menu header"""
        self.clear_screen()
        banner = r"""
  _   _      _   ____                  
 | \ | | ___| |_/ ___|  ___ __ _ _ __  
 |  \| |/ _ \ __\___ \ / __/ _` | '_ \ 
 | |\  |  __/ |_ ___) | (_| (_| | | | |
 |_| \_|\___|\__|____/ \___\__,_|_| |_|
        """
        print(f"{Colors.HEADER}{banner}{Colors.RESET}")
        if subtitle:
            print(f"  {Colors.BLUE}{subtitle}{Colors.RESET}")
        print()
    
    def print_menu(self, options: List[Dict], title: str = ""):
        """
        Print menu options
        
        Args:
            options: List of dicts with 'key', 'label', and optionally 'desc'
            title: Optional section title
        """
        if title:
            print(f"  {Colors.YELLOW}{title}{Colors.RESET}")
            print()
        
        for opt in options:
            key = opt.get('key', '')
            label = opt.get('label', '')
            desc = opt.get('desc', '')
            
            print(f"    {Colors.GREEN}[{key}]{Colors.RESET} {label}", end='')
            if desc:
                print(f"  {Colors.BLUE}- {desc}{Colors.RESET}", end='')
            print()
        print()
    
    def prompt(self, message: str = "Select option") -> str:
        """Prompt for user input"""
        try:
            return input(f"  {Colors.BOLD}{message}: {Colors.RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            return 'q'
    
    def pause(self, message: str = "Press Enter to continue..."):
        """Pause and wait for Enter"""
        try:
            input(f"\n  {message}")
        except (KeyboardInterrupt, EOFError):
            pass
    
    def run_command(self, cmd: List[str], show_output: bool = True) -> Optional[str]:
        """Run a command and optionally show output"""
        try:
            if show_output:
                result = subprocess.run(cmd, capture_output=True, text=True)
                return result.stdout + result.stderr
            else:
                subprocess.run(cmd, check=True)
                return None
        except Exception as e:
            return f"Error: {e}"
    
    def run_python(self, script: str, args: List[str] = None) -> Optional[str]:
        """Run a Python script from helpers directory"""
        script_path = os.path.join(self.script_dir, script)
        if not os.path.exists(script_path):
            return f"Script not found: {script_path}"
        
        cmd = [sys.executable, script_path]
        if args:
            cmd.extend(args)
        
        return self.run_command(cmd)


class MainMenu(Menu):
    """Main application menu"""
    
    def __init__(self):
        super().__init__("NetScan")
    
    def run(self):
        """Run the main menu loop"""
        while True:
            self.print_header("Network Scanner & MAC Lookup Tool")
            
            options = [
                {'key': '1', 'label': 'MAC Lookup', 'desc': 'Look up vendor by MAC address'},
                {'key': '2', 'label': 'Network Scan', 'desc': 'Discover devices on network'},
                {'key': '3', 'label': 'Port Scan', 'desc': 'Scan ports on a target'},
                {'key': '4', 'label': 'ARP Table', 'desc': 'View local ARP cache'},
                {'key': '5', 'label': 'Network Info', 'desc': 'Show network interfaces'},
                {'key': '6', 'label': 'Web Interface', 'desc': 'Start web dashboard'},
                {'key': '7', 'label': 'Settings', 'desc': 'Configuration options'},
                {'key': 'q', 'label': 'Quit', 'desc': 'Exit application'},
            ]
            
            self.print_menu(options, "Main Menu")
            choice = self.prompt("Select option")
            
            if choice == '1':
                self.mac_lookup_menu()
            elif choice == '2':
                self.network_scan_menu()
            elif choice == '3':
                self.port_scan_menu()
            elif choice == '4':
                self.show_arp_table()
            elif choice == '5':
                self.show_network_info()
            elif choice == '6':
                self.start_web_interface()
            elif choice == '7':
                self.settings_menu()
            elif choice.lower() == 'q':
                print(f"\n  {Colors.GREEN}Goodbye!{Colors.RESET}\n")
                break
    
    def mac_lookup_menu(self):
        """MAC address lookup submenu"""
        while True:
            self.print_header("MAC Address Lookup")
            
            options = [
                {'key': '1', 'label': 'Single Lookup', 'desc': 'Look up one MAC address'},
                {'key': '2', 'label': 'Batch Lookup', 'desc': 'Look up multiple addresses'},
                {'key': '3', 'label': 'Search Vendor', 'desc': 'Search by vendor name'},
                {'key': '4', 'label': 'Database Stats', 'desc': 'Show OUI database info'},
                {'key': 'b', 'label': 'Back', 'desc': 'Return to main menu'},
            ]
            
            self.print_menu(options)
            choice = self.prompt("Select option")
            
            if choice == '1':
                mac = self.prompt("Enter MAC address")
                if mac:
                    output = self.run_python('mac_lookup.py', [mac])
                    print(f"\n{output}")
                    self.pause()
            
            elif choice == '2':
                macs = self.prompt("Enter MAC addresses (space-separated)")
                if macs:
                    mac_list = macs.split()
                    output = self.run_python('mac_lookup.py', ['--batch'] + mac_list)
                    print(f"\n{output}")
                    self.pause()
            
            elif choice == '3':
                vendor = self.prompt("Enter vendor name to search")
                if vendor:
                    output = self.run_python('oui_parser.py', ['--search', vendor])
                    print(f"\n{output}")
                    self.pause()
            
            elif choice == '4':
                output = self.run_python('mac_lookup.py', ['--stats'])
                print(f"\n{output}")
                self.pause()
            
            elif choice.lower() == 'b':
                break
    
    def network_scan_menu(self):
        """Network scanning submenu"""
        while True:
            self.print_header("Network Scanner")
            
            options = [
                {'key': '1', 'label': 'Quick Scan', 'desc': 'Scan local network'},
                {'key': '2', 'label': 'Custom Range', 'desc': 'Scan specific IP range'},
                {'key': '3', 'label': 'Full Scan + Ports', 'desc': 'Scan hosts and common ports'},
                {'key': 'b', 'label': 'Back', 'desc': 'Return to main menu'},
            ]
            
            self.print_menu(options)
            choice = self.prompt("Select option")
            
            if choice == '1':
                print(f"\n  {Colors.YELLOW}Scanning local network...{Colors.RESET}\n")
                output = self.run_python('scanner.py', ['--scan'])
                print(output)
                self.pause()
            
            elif choice == '2':
                target = self.prompt("Enter IP range (e.g., 192.168.1.0/24)")
                if target:
                    print(f"\n  {Colors.YELLOW}Scanning {target}...{Colors.RESET}\n")
                    output = self.run_python('scanner.py', ['--scan', target])
                    print(output)
                    self.pause()
            
            elif choice == '3':
                target = self.prompt("Enter IP range (or press Enter for local)")
                args = ['--scan']
                if target:
                    args.append(target)
                
                print(f"\n  {Colors.YELLOW}Performing full scan...{Colors.RESET}\n")
                output = self.run_python('scanner.py', args)
                print(output)
                self.pause()
            
            elif choice.lower() == 'b':
                break
    
    def port_scan_menu(self):
        """Port scanning submenu"""
        self.print_header("Port Scanner")
        
        target = self.prompt("Enter target IP address")
        if not target:
            return
        
        print(f"\n  Port presets:")
        print(f"    {Colors.GREEN}[1]{Colors.RESET} Common (22,80,443,3389,445)")
        print(f"    {Colors.GREEN}[2]{Colors.RESET} Web (80,443,8080,8443)")
        print(f"    {Colors.GREEN}[3]{Colors.RESET} Top 100")
        print(f"    {Colors.GREEN}[4]{Colors.RESET} Custom range\n")
        
        preset = self.prompt("Select preset")
        
        if preset == '1':
            ports = "22,80,443,3389,445,139"
        elif preset == '2':
            ports = "80,443,8080,8443,8000,3000"
        elif preset == '3':
            ports = "1-100"
        elif preset == '4':
            ports = self.prompt("Enter ports (e.g., 22,80,443 or 1-1000)")
        else:
            return
        
        print(f"\n  {Colors.YELLOW}Scanning ports on {target}...{Colors.RESET}\n")
        output = self.run_python('scanner.py', ['--ports', target, '--port-list', ports])
        print(output)
        self.pause()
    
    def show_arp_table(self):
        """Display ARP table"""
        self.print_header("ARP Table")
        output = self.run_python('scanner.py', ['--arp'])
        print(output)
        self.pause()
    
    def show_network_info(self):
        """Display network information"""
        self.print_header("Network Information")
        output = self.run_python('scanner.py', ['--info'])
        print(output)
        self.pause()
    
    def start_web_interface(self):
        """Start web interface"""
        self.print_header("Web Interface")
        
        port = self.prompt("Enter port (default: 5555)") or "5555"
        
        print(f"\n  {Colors.GREEN}Starting web interface on port {port}...{Colors.RESET}")
        print(f"  Open http://localhost:{port} in your browser")
        print(f"  Press Ctrl+C to stop\n")
        
        web_script = os.path.join(self.script_dir, 'web_server.py')
        if os.path.exists(web_script):
            try:
                subprocess.run([sys.executable, web_script, '--port', port])
            except KeyboardInterrupt:
                print(f"\n  {Colors.YELLOW}Web server stopped{Colors.RESET}")
        else:
            print(f"  {Colors.RED}Web server not available{Colors.RESET}")
        
        self.pause()
    
    def settings_menu(self):
        """Settings submenu"""
        while True:
            self.print_header("Settings")
            
            options = [
                {'key': '1', 'label': 'Update OUI Database', 'desc': 'Download latest from IEEE'},
                {'key': '2', 'label': 'View Config', 'desc': 'Show current configuration'},
                {'key': '3', 'label': 'Clear Cache', 'desc': 'Remove cached data'},
                {'key': '4', 'label': 'Check Dependencies', 'desc': 'Verify installed packages'},
                {'key': 'b', 'label': 'Back', 'desc': 'Return to main menu'},
            ]
            
            self.print_menu(options)
            choice = self.prompt("Select option")
            
            if choice == '1':
                self.update_oui_database()
            elif choice == '2':
                self.view_config()
            elif choice == '3':
                self.clear_cache()
            elif choice == '4':
                self.check_dependencies()
            elif choice.lower() == 'b':
                break
    
    def update_oui_database(self):
        """Update OUI database"""
        print(f"\n  {Colors.YELLOW}Downloading OUI database from IEEE...{Colors.RESET}\n")
        
        try:
            import urllib.request
            
            url = "https://standards-oui.ieee.org/oui/oui.txt"
            data_dir = os.path.join(self.parent_dir, 'data')
            os.makedirs(data_dir, exist_ok=True)
            
            oui_path = os.path.join(data_dir, 'oui.txt')
            
            print(f"  Downloading from {url}...")
            urllib.request.urlretrieve(url, oui_path)
            
            size = os.path.getsize(oui_path) / (1024 * 1024)
            print(f"\n  {Colors.GREEN}Downloaded: {oui_path} ({size:.2f} MB){Colors.RESET}")
        
        except Exception as e:
            print(f"\n  {Colors.RED}Error: {e}{Colors.RESET}")
        
        self.pause()
    
    def view_config(self):
        """View configuration"""
        config_path = os.path.join(self.parent_dir, 'config.json')
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            print(f"\n  Configuration ({config_path}):\n")
            print(json.dumps(config, indent=4))
        else:
            print(f"\n  {Colors.YELLOW}No configuration file found{Colors.RESET}")
        
        self.pause()
    
    def clear_cache(self):
        """Clear cached data"""
        cache_dir = os.path.join(self.parent_dir, 'cache')
        
        if os.path.exists(cache_dir):
            import shutil
            shutil.rmtree(cache_dir)
            os.makedirs(cache_dir)
            print(f"\n  {Colors.GREEN}Cache cleared{Colors.RESET}")
        else:
            print(f"\n  {Colors.YELLOW}No cache directory found{Colors.RESET}")
        
        self.pause()
    
    def check_dependencies(self):
        """Check Python dependencies"""
        print(f"\n  {Colors.YELLOW}Checking dependencies...{Colors.RESET}\n")
        
        deps = ['requests', 'flask', 'psutil', 'colorama']
        
        for dep in deps:
            try:
                __import__(dep)
                print(f"    {Colors.GREEN}✓{Colors.RESET} {dep}")
            except ImportError:
                print(f"    {Colors.RED}✗{Colors.RESET} {dep} (not installed)")
        
        # Check nmap
        try:
            subprocess.run(['nmap', '--version'], capture_output=True)
            print(f"    {Colors.GREEN}✓{Colors.RESET} nmap")
        except Exception:
            print(f"    {Colors.YELLOW}○{Colors.RESET} nmap (optional, not found)")
        
        self.pause()


def main():
    """CLI entry point"""
    menu = MainMenu()
    
    try:
        menu.run()
    except KeyboardInterrupt:
        print(f"\n\n  {Colors.YELLOW}Interrupted{Colors.RESET}\n")
        sys.exit(0)


if __name__ == '__main__':
    main()
