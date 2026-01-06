#!/bin/bash
# ============================================================================
# Network Scanning Module - Optimized
# ============================================================================
# Provides network scanning capabilities using various tools
# Output files are saved to: files/output/
# Includes Python-accelerated async scanning and monitoring
# ============================================================================

# Global variables for scanner
LAST_SCAN_FILE=""
SCAN_TARGET=""

# Python helper paths
ASYNC_SCANNER="$SCRIPT_DIR/helpers/async_scanner.py"
MONITOR_HELPER="$SCRIPT_DIR/helpers/monitor.py"
REPORT_HELPER="$SCRIPT_DIR/helpers/report_generator.py"
CONFIG_HELPER="$SCRIPT_DIR/helpers/config_manager.py"
WEB_SERVER="$SCRIPT_DIR/helpers/web_server.py"
EXPORT_HELPER="$SCRIPT_DIR/helpers/export.py"
FINGERPRINT_HELPER="$SCRIPT_DIR/helpers/fingerprint.py"
WOL_HELPER="$SCRIPT_DIR/helpers/wol.py"
SCHEDULER_HELPER="$SCRIPT_DIR/helpers/scheduler.py"
TOPOLOGY_HELPER="$SCRIPT_DIR/helpers/topology.py"
SECURITY_HELPER="$SCRIPT_DIR/helpers/security.py"

# Check if Python helpers are available
has_async_scanner() {
    [[ -f "$ASYNC_SCANNER" ]] && command -v python3 &>/dev/null
}

has_monitor() {
    [[ -f "$MONITOR_HELPER" ]] && command -v python3 &>/dev/null
}

has_reports() {
    [[ -f "$REPORT_HELPER" ]] && command -v python3 &>/dev/null
}

has_config() {
    [[ -f "$CONFIG_HELPER" ]] && command -v python3 &>/dev/null
}

has_web() {
    [[ -f "$WEB_SERVER" ]] && command -v python3 &>/dev/null
}

has_export() {
    [[ -f "$EXPORT_HELPER" ]] && command -v python3 &>/dev/null
}

has_fingerprint() {
    [[ -f "$FINGERPRINT_HELPER" ]] && command -v python3 &>/dev/null
}

has_wol() {
    [[ -f "$WOL_HELPER" ]] && command -v python3 &>/dev/null
}

has_scheduler() {
    [[ -f "$SCHEDULER_HELPER" ]] && command -v python3 &>/dev/null
}

has_topology() {
    [[ -f "$TOPOLOGY_HELPER" ]] && command -v python3 &>/dev/null
}

has_security() {
    [[ -f "$SECURITY_HELPER" ]] && command -v python3 &>/dev/null
}

# ============================================================================
# SCAN MENU
# ============================================================================

show_scan_menu() {
    clear
    echo -e "${CYAN}"
    echo "  ╔═══════════════════════════════════════════════════════════════╗"
    echo "  ║                                                               ║"
    echo -e "  ║              ${BOLD}${WHITE}📡 Network Scanning${NC}${CYAN}                             ║"
    echo "  ║                                                               ║"
    echo "  ╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo -e "${BOLD}${YELLOW}  QUICK SCANS${NC}"
    echo -e "${DIM}  ─────────────────────────────────────────${NC}"
    echo -e "  ${GREEN}1)${NC} 📡 ARP cache ${DIM}(instant, local cache)${NC}"
    echo -e "  ${GREEN}2)${NC} 🔔 Ping sweep ${DIM}(ICMP discovery)${NC}"
    if has_async_scanner; then
        echo -e "  ${GREEN}p)${NC} ⚡ Python async scan ${DIM}(fast, concurrent)${NC}"
    fi
    echo ""
    
    echo -e "${BOLD}${YELLOW}  NMAP SCANS${NC}"
    echo -e "${DIM}  ─────────────────────────────────────────${NC}"
    echo -e "  ${GREEN}3)${NC} 🔍 Host discovery ${DIM}(nmap -sn)${NC}"
    echo -e "  ${GREEN}4)${NC} ⚡ Quick port scan ${DIM}(top 100 ports)${NC}"
    echo -e "  ${GREEN}5)${NC} 🔬 Standard scan ${DIM}(top 1000 ports)${NC}"
    echo -e "  ${GREEN}6)${NC} 📋 Service detection ${DIM}(version info)${NC}"
    echo -e "  ${GREEN}7)${NC} 🎯 Aggressive scan ${DIM}(OS + services + scripts)${NC}"
    echo -e "  ${GREEN}8)${NC} 💻 OS detection ${DIM}(fingerprinting)${NC} ${RED}[sudo]${NC}"
    echo -e "  ${GREEN}9)${NC} 🔓 Vulnerability scan ${DIM}(NSE scripts)${NC}"
    echo ""
    
    echo -e "${BOLD}${YELLOW}  MAC & LAYER 2${NC}"
    echo -e "${DIM}  ─────────────────────────────────────────${NC}"
    echo -e "  ${GREEN}m)${NC} 📶 MAC discovery ${DIM}(nmap with MAC)${NC}"
    echo -e "  ${GREEN}a)${NC} 🔗 ARP-scan ${DIM}(layer 2 scan)${NC} ${RED}[sudo]${NC}"
    echo ""
    
    echo -e "${BOLD}${YELLOW}  ADVANCED${NC}"
    echo -e "${DIM}  ─────────────────────────────────────────${NC}"
    if has_monitor; then
        echo -e "  ${GREEN}w)${NC} 👁️  Real-time monitor ${DIM}(watch for new devices)${NC}"
    fi
    if has_fingerprint; then
        echo -e "  ${GREEN}f)${NC} 🔬 Device fingerprint ${DIM}(identify device types)${NC}"
    fi
    if has_wol; then
        echo -e "  ${GREEN}z)${NC} ⚡ Wake-on-LAN ${DIM}(wake devices remotely)${NC}"
    fi
    if has_scheduler; then
        echo -e "  ${GREEN}j)${NC} ⏰ Scheduled scans ${DIM}(automate with cron/launchd)${NC}"
    fi
    if has_topology; then
        echo -e "  ${GREEN}y)${NC} 🗺️  Network topology ${DIM}(visualize network map)${NC}"
    fi
    if has_security; then
        echo -e "  ${GREEN}s)${NC} 🔒 Security audit ${DIM}(vulnerability assessment)${NC}"
    fi
    if has_reports; then
        echo -e "  ${GREEN}t)${NC} 📊 Generate report ${DIM}(PDF/HTML export)${NC}"
    fi
    if has_export; then
        echo -e "  ${GREEN}x)${NC} 📤 Export results ${DIM}(CSV/HTML/JSON/Markdown)${NC}"
    fi
    if has_config; then
        echo -e "  ${GREEN}g)${NC} ⚙️  Configuration ${DIM}(preferences, custom OUIs)${NC}"
    fi
    if has_web; then
        echo -e "  ${GREEN}b)${NC} 🌐 Web interface ${DIM}(browser dashboard)${NC}"
        # Check if web server is running
        if [[ -f "$SCRIPT_DIR/.web_server.pid" ]]; then
            local pid
            pid=$(cat "$SCRIPT_DIR/.web_server.pid" 2>/dev/null)
            if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
                echo -e "  ${GREEN}k)${NC} 🛑 Kill web server ${DIM}(PID: $pid)${NC}"
            fi
        fi
    fi
    echo ""
    
    echo -e "${BOLD}${YELLOW}  UTILITIES${NC}"
    echo -e "${DIM}  ─────────────────────────────────────────${NC}"
    echo -e "  ${GREEN}i)${NC} ℹ️  Network info"
    echo -e "  ${GREEN}o)${NC} 📂 Open output folder"
    echo -e "  ${GREEN}l)${NC} 📄 Load last scan"
    echo -e "  ${GREEN}h)${NC} 📖 Scan history"
    echo -e "  ${GREEN}0)${NC} ↩️  Back"
    echo ""
}

handle_scan_menu() {
    local choice=""
    while true; do
        show_scan_menu
        
        echo -e "${CYAN}  Select scan type:${NC}"
        read -r choice
        
        # Trim whitespace
        choice="${choice// /}"
        
        case "$choice" in
            1) scan_arp; continue ;;
            2) scan_ping_sweep; continue ;;
            3) scan_nmap_discovery; continue ;;
            4) scan_nmap_quick; continue ;;
            5) scan_nmap_standard; continue ;;
            6) scan_nmap_services; continue ;;
            7) scan_nmap_aggressive; continue ;;
            8) scan_nmap_os; continue ;;
            9) scan_nmap_vuln; continue ;;
            p|P) scan_python_async; continue ;;
            m|M) scan_nmap_mac; continue ;;
            a|A) scan_arp_scan; continue ;;
            w|W) start_monitor; continue ;;
            f|F) run_fingerprint; continue ;;
            z|Z) run_wol; continue ;;
            j|J) run_scheduler; continue ;;
            y|Y) run_topology; continue ;;
            s|S) run_security; continue ;;
            t|T) generate_report; continue ;;
            x|X) run_export; continue ;;
            g|G) manage_config; continue ;;
            b|B) start_web_server; continue ;;
            k|K) kill_web_server; continue ;;
            i|I) show_network_info; continue ;;
            o|O) open_output_folder; continue ;;
            l|L) load_last_scan; continue ;;
            h|H) show_scan_history; continue ;;
            0|q|Q|"") return 0 ;;
            *) 
                echo -e "  ${RED}Invalid option${NC}"
                sleep 0.5
                continue
                ;;
        esac
    done
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

check_scan_tool() {
    local tool="$1"
    if ! command -v "$tool" &>/dev/null; then
        echo ""
        print_error "$tool is not installed"
        echo -e "  ${DIM}Install with: brew install $tool${NC}"
        press_enter
        return 1
    fi
    return 0
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        echo ""
        print_warning "This scan requires root privileges"
        echo -e "  ${DIM}Run with: sudo netscan${NC}"
        press_enter
        return 1
    fi
    return 0
}

get_output_filename() {
    local prefix="$1"
    local ext="${2:-txt}"
    echo "$OUTPUT_DIR/${prefix}_$(date +%Y%m%d_%H%M%S).${ext}"
}

# Prompt for target - returns via global variable to avoid subshell issues
prompt_scan_target() {
    local default_range
    default_range=$(detect_network_range)
    
    echo ""
    echo -e "  ${CYAN}Enter target (IP, range, or CIDR):${NC}"
    echo -e "  ${DIM}Examples: 192.168.1.1, 192.168.1.0/24, 10.0.0.1-50${NC}"
    echo -e "  ${DIM}Default: ${NC}${GREEN}$default_range${NC}"
    echo ""
    read -r -p "  Target> " SCAN_TARGET
    
    if [[ -z "$SCAN_TARGET" ]]; then
        SCAN_TARGET="$default_range"
    fi
    
    echo -e "  ${DIM}Scanning: $SCAN_TARGET${NC}"
}

# Save result and offer to load
save_and_load() {
    local file="$1"
    local count="$2"
    local scan_type="$3"
    
    LAST_SCAN_FILE="$file"
    
    echo ""
    echo -e "  ${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "  ${GREEN}✓${NC} Scan complete!"
    echo -e "  ${DIM}Type:${NC}    $scan_type"
    echo -e "  ${DIM}Found:${NC}   ${GREEN}$count${NC} hosts/entries"
    echo -e "  ${DIM}Saved:${NC}   $(basename "$file")"
    echo -e "  ${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    echo -e "  ${CYAN}Load results into NetScan? [Y/n]${NC}"
    read -r response
    
    if [[ ! "$response" =~ ^[Nn]$ ]]; then
        load_scan_file "$file"
    fi
    
    press_enter
}

# Load a scan file
load_scan_file() {
    local file="$1"
    
    INPUT_FILE="$file"
    FILE_FORMAT=$(detect_file_format "$file")
    
    echo -e "  ${DIM}Parsing $FILE_FORMAT...${NC}"
    
    case "$FILE_FORMAT" in
        "nmap-xml") parse_xml_file ;;
        "arp-table") parse_arp_file ;;
        "plain-text") parse_plain_text_file ;;
        "csv") parse_csv_file ;;
        "json") parse_json_file ;;
        *) 
            print_error "Unknown format: $FILE_FORMAT"
            return 1
            ;;
    esac
    
    local loaded
    loaded=$(wc -l < "$TEMP_FILE" | tr -d ' ')
    print_success "Loaded $loaded devices into NetScan"
}

# ============================================================================
# NETWORK INFO
# ============================================================================

detect_interface() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        route -n get default 2>/dev/null | grep 'interface:' | awk '{print $2}'
    else
        ip route 2>/dev/null | grep default | awk '{print $5}' | head -1
    fi
}

detect_local_ip() {
    local iface
    iface=$(detect_interface)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        ipconfig getifaddr "$iface" 2>/dev/null
    else
        ip addr show "$iface" 2>/dev/null | grep 'inet ' | awk '{print $2}' | cut -d/ -f1
    fi
}

detect_network_range() {
    local ip
    ip=$(detect_local_ip)
    if [[ -n "$ip" ]]; then
        echo "${ip%.*}.0/24"
    else
        echo "192.168.1.0/24"
    fi
}

detect_gateway() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        route -n get default 2>/dev/null | grep 'gateway:' | awk '{print $2}'
    else
        ip route 2>/dev/null | grep default | awk '{print $3}'
    fi
}

show_network_info() {
    clear
    print_header "Network Information"
    
    local iface ip gateway range
    iface=$(detect_interface)
    ip=$(detect_local_ip)
    gateway=$(detect_gateway)
    range=$(detect_network_range)
    
    echo -e "  ${BOLD}Interface:${NC}      $iface"
    echo -e "  ${BOLD}Local IP:${NC}       $ip"
    echo -e "  ${BOLD}Gateway:${NC}        $gateway"
    echo -e "  ${BOLD}Network Range:${NC}  $range"
    echo ""
    
    echo -e "  ${BOLD}Installed Tools:${NC}"
    local tools=("nmap" "arp-scan" "fping" "masscan" "netcat")
    for tool in "${tools[@]}"; do
        if command -v "$tool" &>/dev/null; then
            local ver
            ver=$("$tool" --version 2>&1 | head -1 | cut -d' ' -f2-3)
            echo -e "    ${GREEN}✓${NC} $tool ${DIM}$ver${NC}"
        else
            echo -e "    ${DIM}○${NC} $tool ${DIM}(not installed)${NC}"
        fi
    done
    
    echo ""
    echo -e "  ${BOLD}Output Directory:${NC}"
    echo -e "    $OUTPUT_DIR"
    local file_count
    file_count=$(ls -1 "$OUTPUT_DIR" 2>/dev/null | wc -l | tr -d ' ')
    echo -e "    ${DIM}$file_count scan files${NC}"
    
    press_enter
}

open_output_folder() {
    mkdir -p "$OUTPUT_DIR"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open "$OUTPUT_DIR"
    else
        xdg-open "$OUTPUT_DIR" 2>/dev/null || echo -e "  ${DIM}$OUTPUT_DIR${NC}"
    fi
}

load_last_scan() {
    if [[ -z "$LAST_SCAN_FILE" ]] || [[ ! -f "$LAST_SCAN_FILE" ]]; then
        LAST_SCAN_FILE=$(ls -t "$OUTPUT_DIR"/* 2>/dev/null | head -1)
    fi
    
    if [[ -z "$LAST_SCAN_FILE" ]] || [[ ! -f "$LAST_SCAN_FILE" ]]; then
        echo ""
        print_error "No scan results found in output folder"
        press_enter
        return 1
    fi
    
    echo ""
    echo -e "  ${CYAN}Loading: $(basename "$LAST_SCAN_FILE")${NC}"
    load_scan_file "$LAST_SCAN_FILE"
    press_enter
}

show_scan_history() {
    clear
    print_header "Scan History"
    
    local files
    files=$(ls -lt "$OUTPUT_DIR"/* 2>/dev/null | head -20)
    
    if [[ -z "$files" ]]; then
        echo -e "  ${DIM}No scan files found${NC}"
        press_enter
        return
    fi
    
    echo -e "  ${BOLD}Recent scans:${NC}"
    echo ""
    
    local i=1
    while IFS= read -r line; do
        local fname fsize fdate
        fname=$(echo "$line" | awk '{print $NF}')
        fsize=$(echo "$line" | awk '{print $5}')
        fdate=$(echo "$line" | awk '{print $6, $7, $8}')
        
        echo -e "  ${GREEN}$i)${NC} $(basename "$fname") ${DIM}($fsize bytes, $fdate)${NC}"
        ((i++))
    done <<< "$(ls -lt "$OUTPUT_DIR"/* 2>/dev/null | head -15)"
    
    echo ""
    echo -e "  ${CYAN}Enter number to load, or 0 to cancel:${NC}"
    read -r choice
    
    if [[ "$choice" =~ ^[0-9]+$ ]] && [[ "$choice" -gt 0 ]]; then
        local selected
        selected=$(ls -t "$OUTPUT_DIR"/* 2>/dev/null | sed -n "${choice}p")
        if [[ -f "$selected" ]]; then
            load_scan_file "$selected"
        fi
    fi
    
    press_enter
}

# ============================================================================
# SCAN IMPLEMENTATIONS
# ============================================================================

# 1. ARP Cache
scan_arp() {
    clear
    print_header "ARP Cache Scan"
    echo -e "  ${DIM}Reading local ARP cache (recently contacted devices)${NC}"
    echo ""
    
    local outfile
    outfile=$(get_output_filename "arp" "txt")
    
    print_progress "Reading ARP cache..."
    arp -a > "$outfile" 2>&1
    
    local count
    count=$(wc -l < "$outfile" | tr -d ' ')
    log_action "ARP scan: $count entries"
    
    # Preview
    echo ""
    echo -e "  ${BOLD}Results:${NC}"
    head -10 "$outfile" | while IFS= read -r line; do
        echo -e "  ${DIM}$line${NC}"
    done
    [[ $count -gt 10 ]] && echo -e "  ${DIM}... and $((count - 10)) more${NC}"
    
    save_and_load "$outfile" "$count" "ARP Cache"
}

# 2. Ping Sweep
scan_ping_sweep() {
    clear
    print_header "Ping Sweep"
    
    prompt_scan_target
    local target="$SCAN_TARGET"
    local base_ip="${target%.*}"
    
    echo ""
    local outfile
    outfile=$(get_output_filename "ping" "txt")
    
    {
        echo "# Ping sweep - $(date)"
        echo "# Target: $target"
        echo ""
    } > "$outfile"
    
    print_progress "Scanning $target..."
    
    if command -v fping &>/dev/null; then
        echo -e "  ${DIM}Using fping (fast mode)${NC}"
        fping -a -g "$target" 2>/dev/null | tee -a "$outfile"
    else
        echo -e "  ${DIM}Using ping (slower)${NC}"
        for i in {1..254}; do
            (ping -c 1 -W 1 "${base_ip}.${i}" &>/dev/null && echo "${base_ip}.${i}") &
            [[ $((i % 50)) -eq 0 ]] && { wait; echo -ne "\r  Progress: $i/254..."; }
        done
        wait
        echo ""
    fi >> "$outfile"
    
    local count
    count=$(grep -c "^[0-9]" "$outfile" 2>/dev/null || echo "0")
    log_action "Ping sweep: $count hosts"
    
    save_and_load "$outfile" "$count" "Ping Sweep"
}

# 3. Nmap Host Discovery
scan_nmap_discovery() {
    check_scan_tool "nmap" || return 1
    
    clear
    print_header "Nmap Host Discovery"
    echo -e "  ${DIM}Find live hosts without port scanning${NC}"
    
    prompt_scan_target
    
    echo ""
    local outfile
    outfile=$(get_output_filename "nmap_discovery" "xml")
    
    print_progress "Scanning $SCAN_TARGET..."
    echo -e "  ${DIM}Command: nmap -sn -T4 $SCAN_TARGET${NC}"
    echo ""
    
    nmap -sn -T4 --open "$SCAN_TARGET" -oX "$outfile" 2>&1 | \
        grep -E "(Nmap scan|Host is|MAC Address|Nmap done)" | \
        sed 's/^/  /'
    
    local count
    count=$(grep -c "<host " "$outfile" 2>/dev/null || echo "0")
    log_action "Nmap discovery: $count hosts"
    
    save_and_load "$outfile" "$count" "Host Discovery"
}

# 4. Nmap Quick Scan (top 100 ports)
scan_nmap_quick() {
    check_scan_tool "nmap" || return 1
    
    clear
    print_header "Nmap Quick Port Scan"
    echo -e "  ${DIM}Scan top 100 most common ports${NC}"
    
    prompt_scan_target
    
    echo ""
    local outfile
    outfile=$(get_output_filename "nmap_quick" "xml")
    
    print_progress "Quick scanning $SCAN_TARGET..."
    echo -e "  ${DIM}Command: nmap -F -T4 $SCAN_TARGET${NC}"
    echo ""
    
    nmap -F -T4 -sV --version-light --open "$SCAN_TARGET" -oX "$outfile" 2>&1 | \
        grep -E "(Nmap scan|Host is|PORT|open|MAC Address|Nmap done)" | \
        sed 's/^/  /'
    
    local count
    count=$(grep -c "<host " "$outfile" 2>/dev/null || echo "0")
    log_action "Nmap quick: $count hosts"
    
    save_and_load "$outfile" "$count" "Quick Port Scan"
}

# 5. Nmap Standard Scan (top 1000 ports)
scan_nmap_standard() {
    check_scan_tool "nmap" || return 1
    
    clear
    print_header "Nmap Standard Scan"
    echo -e "  ${DIM}Scan top 1000 ports with service detection${NC}"
    
    prompt_scan_target
    
    echo ""
    local outfile
    outfile=$(get_output_filename "nmap_standard" "xml")
    
    print_progress "Scanning $SCAN_TARGET..."
    echo -e "  ${DIM}Command: nmap -sV -T4 $SCAN_TARGET${NC}"
    echo ""
    
    nmap -sV -T4 --open "$SCAN_TARGET" -oX "$outfile" 2>&1 | \
        grep -E "(Nmap scan|Host is|PORT|open|Service|MAC Address|Nmap done)" | \
        sed 's/^/  /'
    
    local count
    count=$(grep -c "<host " "$outfile" 2>/dev/null || echo "0")
    log_action "Nmap standard: $count hosts"
    
    save_and_load "$outfile" "$count" "Standard Scan"
}

# 6. Nmap Service Detection
scan_nmap_services() {
    check_scan_tool "nmap" || return 1
    
    clear
    print_header "Nmap Service Detection"
    echo -e "  ${DIM}Detailed service version detection${NC}"
    
    prompt_scan_target
    
    echo ""
    local outfile
    outfile=$(get_output_filename "nmap_services" "xml")
    
    print_progress "Detecting services on $SCAN_TARGET..."
    echo -e "  ${DIM}Command: nmap -sV --version-all -T4 $SCAN_TARGET${NC}"
    echo ""
    
    nmap -sV --version-all -T4 --open "$SCAN_TARGET" -oX "$outfile" 2>&1 | \
        grep -E "(Nmap scan|Host is|PORT|open|Service Info|MAC Address|Nmap done)" | \
        sed 's/^/  /'
    
    local count
    count=$(grep -c "<host " "$outfile" 2>/dev/null || echo "0")
    log_action "Nmap services: $count hosts"
    
    save_and_load "$outfile" "$count" "Service Detection"
}

# 7. Nmap Aggressive Scan
scan_nmap_aggressive() {
    check_scan_tool "nmap" || return 1
    
    clear
    print_header "Nmap Aggressive Scan"
    echo -e "  ${DIM}OS detection, version detection, scripts, and traceroute${NC}"
    echo -e "  ${YELLOW}⚠ This scan is noisy and may take a while${NC}"
    
    prompt_scan_target
    
    echo ""
    echo -e "  ${CYAN}Continue with aggressive scan? [y/N]${NC}"
    read -r confirm
    [[ ! "$confirm" =~ ^[Yy]$ ]] && return
    
    local outfile
    outfile=$(get_output_filename "nmap_aggressive" "xml")
    
    print_progress "Aggressive scanning $SCAN_TARGET..."
    echo -e "  ${DIM}Command: nmap -A -T4 $SCAN_TARGET${NC}"
    echo ""
    
    nmap -A -T4 --open "$SCAN_TARGET" -oX "$outfile" 2>&1 | \
        grep -E "(Nmap scan|Host is|PORT|open|Running|OS details|Service|MAC Address|Nmap done)" | \
        sed 's/^/  /'
    
    local count
    count=$(grep -c "<host " "$outfile" 2>/dev/null || echo "0")
    log_action "Nmap aggressive: $count hosts"
    
    save_and_load "$outfile" "$count" "Aggressive Scan"
}

# 8. Nmap OS Detection
scan_nmap_os() {
    check_scan_tool "nmap" || return 1
    check_root || return 1
    
    clear
    print_header "Nmap OS Detection"
    echo -e "  ${DIM}Fingerprint operating systems${NC}"
    
    prompt_scan_target
    
    echo ""
    local outfile
    outfile=$(get_output_filename "nmap_os" "xml")
    
    print_progress "Detecting OS on $SCAN_TARGET..."
    echo -e "  ${DIM}Command: nmap -O --osscan-guess $SCAN_TARGET${NC}"
    echo ""
    
    nmap -O --osscan-guess -T4 "$SCAN_TARGET" -oX "$outfile" 2>&1 | \
        grep -E "(Nmap scan|Host is|Running|OS details|Aggressive OS|MAC Address|Nmap done)" | \
        sed 's/^/  /'
    
    local count
    count=$(grep -c "<host " "$outfile" 2>/dev/null || echo "0")
    log_action "Nmap OS: $count hosts"
    
    save_and_load "$outfile" "$count" "OS Detection"
}

# 9. Nmap Vulnerability Scan
scan_nmap_vuln() {
    check_scan_tool "nmap" || return 1
    
    clear
    print_header "Nmap Vulnerability Scan"
    echo -e "  ${DIM}Run NSE vulnerability scripts${NC}"
    echo -e "  ${YELLOW}⚠ This scan is intrusive and may take a long time${NC}"
    
    prompt_scan_target
    
    echo ""
    echo -e "  ${CYAN}Continue with vulnerability scan? [y/N]${NC}"
    read -r confirm
    [[ ! "$confirm" =~ ^[Yy]$ ]] && return
    
    local outfile
    outfile=$(get_output_filename "nmap_vuln" "xml")
    
    print_progress "Vulnerability scanning $SCAN_TARGET..."
    echo -e "  ${DIM}Command: nmap --script vuln $SCAN_TARGET${NC}"
    echo ""
    
    nmap --script vuln -T4 "$SCAN_TARGET" -oX "$outfile" 2>&1 | \
        grep -E "(Nmap scan|Host is|PORT|VULNERABLE|CVE|MAC Address|Nmap done)" | \
        sed 's/^/  /'
    
    local count
    count=$(grep -c "<host " "$outfile" 2>/dev/null || echo "0")
    log_action "Nmap vuln: $count hosts"
    
    save_and_load "$outfile" "$count" "Vulnerability Scan"
}

# M. Nmap MAC Discovery
scan_nmap_mac() {
    check_scan_tool "nmap" || return 1
    
    clear
    print_header "Nmap MAC Discovery"
    echo -e "  ${DIM}Discover MAC addresses on local network${NC}"
    
    prompt_scan_target
    
    echo ""
    local outfile
    outfile=$(get_output_filename "nmap_mac" "xml")
    
    print_progress "Scanning for MAC addresses..."
    echo -e "  ${DIM}Command: nmap -sn -PR $SCAN_TARGET${NC}"
    echo ""
    
    # Use -PR for ARP ping on local network
    nmap -sn -PR -T4 "$SCAN_TARGET" -oX "$outfile" 2>&1 | \
        grep -E "(Nmap scan|Host is|MAC Address|Nmap done)" | \
        sed 's/^/  /'
    
    local count
    count=$(grep -c "<host " "$outfile" 2>/dev/null || echo "0")
    log_action "Nmap MAC: $count hosts"
    
    save_and_load "$outfile" "$count" "MAC Discovery"
}

# A. ARP-Scan
scan_arp_scan() {
    if ! check_scan_tool "arp-scan"; then
        echo -e "  ${DIM}Install: brew install arp-scan${NC}"
        press_enter
        return 1
    fi
    check_root || return 1
    
    clear
    print_header "ARP-Scan (Layer 2)"
    echo -e "  ${DIM}Direct layer 2 network scan${NC}"
    echo ""
    
    local outfile
    outfile=$(get_output_filename "arpscan" "txt")
    
    local iface
    iface=$(detect_interface)
    
    print_progress "ARP scanning on $iface..."
    echo -e "  ${DIM}Command: arp-scan --localnet -I $iface${NC}"
    echo ""
    
    arp-scan --localnet -I "$iface" 2>&1 | tee "$outfile" | \
        grep -E "^[0-9]|packets|hosts" | \
        sed 's/^/  /'
    
    local count
    count=$(grep -cE "^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+" "$outfile" 2>/dev/null || echo "0")
    log_action "ARP-scan: $count hosts"
    
    save_and_load "$outfile" "$count" "ARP-Scan"
}

# ============================================================================
# PYTHON-POWERED ADVANCED FEATURES
# ============================================================================

# P. Python Async Scan (fast, concurrent)
scan_python_async() {
    if ! has_async_scanner; then
        print_error "Python async scanner not available"
        echo -e "  ${DIM}Check helpers/async_scanner.py exists and Python 3 is installed${NC}"
        press_enter
        return 1
    fi
    
    clear
    print_header "Python Async Network Scan"
    echo -e "  ${DIM}High-performance concurrent network discovery${NC}"
    echo -e "  ${DIM}Features: CIDR expansion, parallel pings, vendor lookups${NC}"
    echo ""
    
    prompt_scan_target
    
    echo ""
    echo -e "  ${BOLD}Scan type:${NC}"
    echo -e "  ${GREEN}1)${NC} Quick scan ${DIM}(default, fast discovery)${NC}"
    echo -e "  ${GREEN}2)${NC} Full scan ${DIM}(with service discovery)${NC}"
    echo -e "  ${GREEN}3)${NC} Ping sweep only ${DIM}(ICMP only)${NC}"
    echo -e "  ${GREEN}4)${NC} ARP table ${DIM}(read local cache)${NC}"
    echo -e "  ${GREEN}5)${NC} Stealth scan ${DIM}(slower, less detectable)${NC}"
    echo ""
    read -r -p "  Select [1]: " scan_type
    scan_type="${scan_type:-1}"
    
    local outfile
    outfile=$(get_output_filename "async_scan" "json")
    
    print_progress "Running async scan on $SCAN_TARGET..."
    echo ""
    
    local args=""
    case "$scan_type" in
        1) args="" ;;                    # Quick scan (default)
        2) args="--full" ;;              # Full scan with services
        3) args="--ping" ;;              # Ping sweep only
        4) args="--arp"; SCAN_TARGET="" ;;  # ARP table (no target needed)
        5) args="--stealth" ;;           # Stealth scan
        *) args="" ;;
    esac
    
    echo -e "  ${DIM}Running: python3 async_scanner.py $SCAN_TARGET $args --json${NC}"
    echo ""
    
    # Run async scanner and capture output
    local result
    if [[ -n "$SCAN_TARGET" ]]; then
        result=$(python3 "$ASYNC_SCANNER" "$SCAN_TARGET" $args --json 2>&1)
    else
        result=$(python3 "$ASYNC_SCANNER" $args --json 2>&1)
    fi
    
    # Save to file
    echo "$result" > "$outfile"
    
    # Show summary
    local count
    count=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d) if isinstance(d,list) else len(d.get('devices',d.get('hosts',[]))))" 2>/dev/null || echo "0")
    
    # Show preview
    echo -e "  ${BOLD}Results preview:${NC}"
    echo "$result" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    items = d if isinstance(d, list) else d.get('devices', d.get('hosts', []))
    for i, item in enumerate(items[:10]):
        ip = item.get('ip', 'N/A')
        mac = item.get('mac', 'N/A')
        vendor = item.get('vendor', '')[:30]
        print(f'  {ip:15} {mac:17} {vendor}')
    if len(items) > 10:
        print(f'  ... and {len(items)-10} more')
except:
    pass
" 2>/dev/null
    
    log_action "Async scan: $count hosts"
    save_and_load "$outfile" "$count" "Async Network Scan"
}

# W. Real-time Network Monitor
start_monitor() {
    if ! has_monitor; then
        print_error "Network monitor not available"
        echo -e "  ${DIM}Check helpers/monitor.py exists and Python 3 is installed${NC}"
        press_enter
        return 1
    fi
    
    clear
    print_header "Real-time Network Monitor"
    echo -e "  ${DIM}Watch for new devices, track changes, get alerts${NC}"
    echo ""
    
    echo -e "  ${BOLD}Monitor options:${NC}"
    echo -e "  ${GREEN}1)${NC} Start watching ${DIM}(continuous monitoring)${NC}"
    echo -e "  ${GREEN}2)${NC} Single scan ${DIM}(one-time snapshot)${NC}"
    echo -e "  ${GREEN}3)${NC} List all devices ${DIM}(from database)${NC}"
    echo -e "  ${GREEN}4)${NC} List unknown devices"
    echo -e "  ${GREEN}5)${NC} Show statistics"
    echo -e "  ${GREEN}6)${NC} Mark device as known"
    echo -e "  ${GREEN}0)${NC} Back"
    echo ""
    read -r -p "  Select: " monitor_choice
    
    case "$monitor_choice" in
        1)
            echo ""
            echo -e "  ${CYAN}Monitor interval (seconds, default 60):${NC}"
            read -r interval
            interval="${interval:-60}"
            
            echo ""
            echo -e "  ${CYAN}Target network (leave empty for ARP only):${NC}"
            read -r target
            
            echo ""
            print_progress "Starting network monitor (Ctrl+C to stop)..."
            echo ""
            
            local args="--interval $interval"
            [[ -n "$target" ]] && args="$args --target $target"
            
            python3 "$MONITOR_HELPER" $args 2>&1 | sed 's/^/  /'
            ;;
        2)
            echo ""
            print_progress "Running single scan..."
            echo ""
            python3 "$MONITOR_HELPER" --once 2>&1 | sed 's/^/  /'
            ;;
        3)
            echo ""
            print_header "Known Devices"
            python3 "$MONITOR_HELPER" --list 2>&1 | sed 's/^/  /'
            ;;
        4)
            echo ""
            print_header "Unknown Devices"
            python3 "$MONITOR_HELPER" --unknown 2>&1 | sed 's/^/  /'
            ;;
        5)
            echo ""
            print_header "Monitor Statistics"
            python3 "$MONITOR_HELPER" --stats 2>&1 | sed 's/^/  /'
            ;;
        6)
            echo ""
            echo -e "  ${CYAN}MAC address to mark as known:${NC}"
            read -r mac
            if [[ -n "$mac" ]]; then
                python3 "$MONITOR_HELPER" --mark-known "$mac" 2>&1 | sed 's/^/  /'
            fi
            ;;
        0|"") return ;;
    esac
    
    press_enter
}

# F. Device Fingerprinting (v1.1)
run_fingerprint() {
    if ! has_fingerprint; then
        print_error "Device fingerprinting not available"
        echo -e "  ${DIM}Check helpers/fingerprint.py exists and Python 3 is installed${NC}"
        press_enter
        return 1
    fi
    
    clear
    print_header "Device Fingerprinting"
    echo -e "  ${DIM}Identify device types using MAC, ports, and TTL analysis${NC}"
    echo ""
    
    echo -e "  ${BOLD}Fingerprint options:${NC}"
    echo -e "  ${GREEN}1)${NC} 🎯 Fingerprint single device"
    echo -e "  ${GREEN}2)${NC} 🔍 Scan & fingerprint network"
    echo -e "  ${GREEN}3)${NC} 📊 Show device type summary"
    echo -e "  ${GREEN}4)${NC} 📋 Export fingerprint database"
    echo -e "  ${GREEN}0)${NC} Back"
    echo ""
    read -r -p "  Select: " fp_choice
    
    case "$fp_choice" in
        1)
            echo ""
            echo -e "  ${CYAN}Target IP address:${NC}"
            read -r target_ip
            if [[ -n "$target_ip" ]]; then
                echo ""
                print_progress "Fingerprinting $target_ip..."
                echo ""
                python3 "$FINGERPRINT_HELPER" --target "$target_ip" --verbose 2>&1 | sed 's/^/  /'
            fi
            ;;
        2)
            echo ""
            print_progress "Scanning network and fingerprinting devices..."
            echo -e "  ${DIM}This may take a few minutes...${NC}"
            echo ""
            python3 "$FINGERPRINT_HELPER" --scan-network --verbose 2>&1 | sed 's/^/  /'
            ;;
        3)
            echo ""
            print_header "Device Type Summary"
            python3 "$FINGERPRINT_HELPER" --summary 2>&1 | sed 's/^/  /'
            ;;
        4)
            local outfile
            outfile=$(get_output_filename "fingerprints" "json")
            echo ""
            print_progress "Exporting fingerprint database..."
            python3 "$FINGERPRINT_HELPER" --export "$outfile" 2>&1 | sed 's/^/  /'
            if [[ -f "$outfile" ]]; then
                print_success "Exported to: $outfile"
            fi
            ;;
        0|"") return ;;
    esac
    
    press_enter
}

# Z. Wake-on-LAN (v1.1)
run_wol() {
    if ! has_wol; then
        print_error "Wake-on-LAN not available"
        echo -e "  ${DIM}Check helpers/wol.py exists and Python 3 is installed${NC}"
        press_enter
        return 1
    fi
    
    clear
    print_header "Wake-on-LAN"
    echo -e "  ${DIM}Send magic packets to wake sleeping devices${NC}"
    echo ""
    
    echo -e "  ${BOLD}WoL options:${NC}"
    echo -e "  ${GREEN}1)${NC} ⚡ Wake single device"
    echo -e "  ${GREEN}2)${NC} 📋 Wake from favorites"
    echo -e "  ${GREEN}3)${NC} ➕ Add to favorites"
    echo -e "  ${GREEN}4)${NC} 📝 List favorites"
    echo -e "  ${GREEN}5)${NC} ➖ Remove from favorites"
    echo -e "  ${GREEN}0)${NC} Back"
    echo ""
    read -r -p "  Select: " wol_choice
    
    case "$wol_choice" in
        1)
            echo ""
            echo -e "  ${CYAN}MAC address (e.g., AA:BB:CC:DD:EE:FF):${NC}"
            read -r mac_addr
            if [[ -n "$mac_addr" ]]; then
                echo ""
                echo -e "  ${CYAN}Broadcast IP (default 255.255.255.255):${NC}"
                read -r broadcast_ip
                broadcast_ip="${broadcast_ip:-255.255.255.255}"
                
                print_progress "Sending magic packet to $mac_addr..."
                python3 "$WOL_HELPER" --mac "$mac_addr" --broadcast "$broadcast_ip" 2>&1 | sed 's/^/  /'
            fi
            ;;
        2)
            echo ""
            print_progress "Loading favorites..."
            python3 "$WOL_HELPER" --list-favorites 2>&1 | sed 's/^/  /'
            echo ""
            echo -e "  ${CYAN}Device name to wake (or 'all'):${NC}"
            read -r device_name
            if [[ -n "$device_name" ]]; then
                if [[ "$device_name" == "all" ]]; then
                    print_progress "Waking all favorites..."
                    python3 "$WOL_HELPER" --wake-all 2>&1 | sed 's/^/  /'
                else
                    print_progress "Waking $device_name..."
                    python3 "$WOL_HELPER" --wake-favorite "$device_name" 2>&1 | sed 's/^/  /'
                fi
            fi
            ;;
        3)
            echo ""
            echo -e "  ${CYAN}Device name:${NC}"
            read -r name
            echo -e "  ${CYAN}MAC address:${NC}"
            read -r mac
            echo -e "  ${CYAN}Description (optional):${NC}"
            read -r desc
            if [[ -n "$name" && -n "$mac" ]]; then
                python3 "$WOL_HELPER" --add-favorite "$name" "$mac" ${desc:+--description "$desc"} 2>&1 | sed 's/^/  /'
            fi
            ;;
        4)
            echo ""
            print_header "WoL Favorites"
            python3 "$WOL_HELPER" --list-favorites 2>&1 | sed 's/^/  /'
            ;;
        5)
            echo ""
            python3 "$WOL_HELPER" --list-favorites 2>&1 | sed 's/^/  /'
            echo ""
            echo -e "  ${CYAN}Device name to remove:${NC}"
            read -r device_name
            if [[ -n "$device_name" ]]; then
                python3 "$WOL_HELPER" --remove-favorite "$device_name" 2>&1 | sed 's/^/  /'
            fi
            ;;
        0|"") return ;;
    esac
    
    press_enter
}

# X. Export Results (v1.1)
run_export() {
    if ! has_export; then
        print_error "Export module not available"
        echo -e "  ${DIM}Check helpers/export.py exists and Python 3 is installed${NC}"
        press_enter
        return 1
    fi
    
    clear
    print_header "Export Scan Results"
    echo -e "  ${DIM}Export to CSV, HTML, JSON, or PDF formats${NC}"
    echo ""
    
    # Check if we have scan data
    local input_file=""
    if [[ -n "$LAST_SCAN_FILE" ]] && [[ -f "$LAST_SCAN_FILE" ]]; then
        input_file="$LAST_SCAN_FILE"
        echo -e "  ${DIM}Using last scan: $LAST_SCAN_FILE${NC}"
    else
        # Look for recent scan files
        local recent_file
        recent_file=$(find "$OUTPUT_DIR" -name "*.json" -type f -mmin -60 2>/dev/null | head -1)
        if [[ -n "$recent_file" ]]; then
            input_file="$recent_file"
            echo -e "  ${DIM}Using recent: $recent_file${NC}"
        fi
    fi
    
    if [[ -z "$input_file" ]]; then
        print_warning "No scan results found"
        echo -e "  ${DIM}Run a scan first, or provide a file path${NC}"
        echo ""
        echo -e "  ${CYAN}Enter scan results file path (or press Enter to cancel):${NC}"
        read -r input_file
        if [[ -z "$input_file" ]] || [[ ! -f "$input_file" ]]; then
            return
        fi
    fi
    
    echo ""
    echo -e "  ${BOLD}Export format:${NC}"
    echo -e "  ${GREEN}1)${NC} 📊 CSV ${DIM}(spreadsheet compatible)${NC}"
    echo -e "  ${GREEN}2)${NC} 🌐 HTML ${DIM}(styled web report)${NC}"
    echo -e "  ${GREEN}3)${NC} 📄 JSON ${DIM}(structured data)${NC}"
    echo -e "  ${GREEN}4)${NC} 📑 PDF ${DIM}(printable document)${NC}"
    echo -e "  ${GREEN}5)${NC} 📦 All formats"
    echo -e "  ${GREEN}0)${NC} Cancel"
    echo ""
    read -r -p "  Select: " export_choice
    
    local format outfile
    case "$export_choice" in
        1)
            format="csv"
            outfile=$(get_output_filename "export" "csv")
            ;;
        2)
            format="html"
            outfile=$(get_output_filename "export" "html")
            ;;
        3)
            format="json"
            outfile=$(get_output_filename "export" "json")
            ;;
        4)
            format="pdf"
            outfile=$(get_output_filename "export" "pdf")
            ;;
        5)
            # Export all formats
            echo ""
            print_progress "Exporting to all formats..."
            local base_name
            base_name=$(get_output_filename "export" "")
            base_name="${base_name%.*}"
            
            python3 "$EXPORT_HELPER" --input "$input_file" --format csv --output "${base_name}.csv" 2>&1 | sed 's/^/  /'
            python3 "$EXPORT_HELPER" --input "$input_file" --format html --output "${base_name}.html" 2>&1 | sed 's/^/  /'
            python3 "$EXPORT_HELPER" --input "$input_file" --format json --output "${base_name}.json" 2>&1 | sed 's/^/  /'
            python3 "$EXPORT_HELPER" --input "$input_file" --format pdf --output "${base_name}.pdf" 2>&1 | sed 's/^/  /'
            
            echo ""
            print_success "Exported to $OUTPUT_DIR"
            press_enter
            return
            ;;
        0|"") return ;;
        *) return ;;
    esac
    
    echo ""
    print_progress "Exporting to $format..."
    python3 "$EXPORT_HELPER" --input "$input_file" --format "$format" --output "$outfile" 2>&1 | sed 's/^/  /'
    
    if [[ -f "$outfile" ]]; then
        echo ""
        print_success "Exported to: $outfile"
        
        # Open if HTML or PDF
        if [[ "$format" == "html" ]] || [[ "$format" == "pdf" ]]; then
            echo -e "  ${CYAN}Open file? [Y/n]${NC}"
            read -r open_confirm
            [[ ! "$open_confirm" =~ ^[Nn]$ ]] && open "$outfile" 2>/dev/null
        fi
    fi
    
    press_enter
}

# J. Scheduled Scans (v1.1)
run_scheduler() {
    if ! has_scheduler; then
        print_error "Scheduler not available"
        echo -e "  ${DIM}Check helpers/scheduler.py exists and Python 3 is installed${NC}"
        press_enter
        return 1
    fi
    
    clear
    print_header "Scheduled Scans"
    echo -e "  ${DIM}Automate scans with cron (Linux) or launchd (macOS)${NC}"
    echo ""
    
    echo -e "  ${BOLD}Scheduler options:${NC}"
    echo -e "  ${GREEN}1)${NC} 📋 List scheduled jobs"
    echo -e "  ${GREEN}2)${NC} ➕ Create new scheduled scan"
    echo -e "  ${GREEN}3)${NC} ▶️  Run job now"
    echo -e "  ${GREEN}4)${NC} ⏸️  Enable/disable job"
    echo -e "  ${GREEN}5)${NC} ❌ Remove job"
    echo -e "  ${GREEN}6)${NC} 📊 Show job details"
    echo -e "  ${GREEN}0)${NC} Back"
    echo ""
    read -r -p "  Select: " sched_choice
    
    case "$sched_choice" in
        1)
            echo ""
            print_header "Scheduled Jobs"
            python3 "$SCHEDULER_HELPER" --list 2>&1 | sed 's/^/  /'
            ;;
        2)
            echo ""
            echo -e "  ${CYAN}Job name (e.g., daily_scan):${NC}"
            read -r job_name
            if [[ -z "$job_name" ]]; then
                return
            fi
            
            echo ""
            echo -e "  ${BOLD}Schedule:${NC}"
            echo -e "  ${GREEN}1)${NC} Hourly"
            echo -e "  ${GREEN}2)${NC} Daily (9 AM)"
            echo -e "  ${GREEN}3)${NC} Nightly (2 AM)"
            echo -e "  ${GREEN}4)${NC} Weekly (Monday 9 AM)"
            echo -e "  ${GREEN}5)${NC} Monthly (1st of month)"
            echo -e "  ${GREEN}6)${NC} Custom cron expression"
            read -r -p "  Select: " sched_type
            
            local schedule
            case "$sched_type" in
                1) schedule="hourly" ;;
                2) schedule="daily" ;;
                3) schedule="nightly" ;;
                4) schedule="weekly" ;;
                5) schedule="monthly" ;;
                6)
                    echo -e "  ${CYAN}Cron expression (min hour day month weekday):${NC}"
                    read -r schedule
                    ;;
                *) schedule="daily" ;;
            esac
            
            echo ""
            echo -e "  ${BOLD}Scan type:${NC}"
            echo -e "  ${GREEN}1)${NC} Quick (ARP scan)"
            echo -e "  ${GREEN}2)${NC} Full (with ports)"
            read -r -p "  Select [1]: " scan_type_choice
            local scan_type
            case "$scan_type_choice" in
                2) scan_type="full" ;;
                *) scan_type="quick" ;;
            esac
            
            echo ""
            echo -e "  ${CYAN}Email for notifications (optional):${NC}"
            read -r notify_email
            
            echo ""
            print_progress "Creating scheduled job..."
            python3 "$SCHEDULER_HELPER" --create "$job_name" \
                --schedule "$schedule" \
                --scan-type "$scan_type" \
                ${notify_email:+--notify "$notify_email"} 2>&1 | sed 's/^/  /'
            ;;
        3)
            echo ""
            python3 "$SCHEDULER_HELPER" --list 2>&1 | sed 's/^/  /'
            echo ""
            echo -e "  ${CYAN}Job name to run:${NC}"
            read -r job_name
            if [[ -n "$job_name" ]]; then
                print_progress "Running job: $job_name"
                python3 "$SCHEDULER_HELPER" --run "$job_name" 2>&1 | sed 's/^/  /'
            fi
            ;;
        4)
            echo ""
            python3 "$SCHEDULER_HELPER" --list 2>&1 | sed 's/^/  /'
            echo ""
            echo -e "  ${CYAN}Job name:${NC}"
            read -r job_name
            if [[ -n "$job_name" ]]; then
                echo -e "  ${GREEN}1)${NC} Enable"
                echo -e "  ${GREEN}2)${NC} Disable"
                read -r -p "  Select: " enable_choice
                if [[ "$enable_choice" == "1" ]]; then
                    python3 "$SCHEDULER_HELPER" --enable "$job_name" 2>&1 | sed 's/^/  /'
                else
                    python3 "$SCHEDULER_HELPER" --disable "$job_name" 2>&1 | sed 's/^/  /'
                fi
            fi
            ;;
        5)
            echo ""
            python3 "$SCHEDULER_HELPER" --list 2>&1 | sed 's/^/  /'
            echo ""
            echo -e "  ${CYAN}Job name to remove:${NC}"
            read -r job_name
            if [[ -n "$job_name" ]]; then
                echo -e "  ${YELLOW}⚠ This will remove the scheduled job.${NC}"
                echo -e "  ${CYAN}Are you sure? [y/N]${NC}"
                read -r confirm
                if [[ "$confirm" =~ ^[Yy]$ ]]; then
                    python3 "$SCHEDULER_HELPER" --remove "$job_name" 2>&1 | sed 's/^/  /'
                fi
            fi
            ;;
        6)
            echo ""
            echo -e "  ${CYAN}Job name:${NC}"
            read -r job_name
            if [[ -n "$job_name" ]]; then
                python3 "$SCHEDULER_HELPER" --show "$job_name" 2>&1 | sed 's/^/  /'
            fi
            ;;
        0|"") return ;;
    esac
    
    press_enter
}

# Y. Network Topology (v1.1)
run_topology() {
    if ! has_topology; then
        print_error "Topology mapper not available"
        echo -e "  ${DIM}Check helpers/topology.py exists and Python 3 is installed${NC}"
        press_enter
        return 1
    fi
    
    clear
    print_header "Network Topology"
    echo -e "  ${DIM}Visualize your network structure${NC}"
    echo ""
    
    # Check for scan data
    local input_file=""
    if [[ -n "$LAST_SCAN_FILE" ]] && [[ -f "$LAST_SCAN_FILE" ]]; then
        input_file="$LAST_SCAN_FILE"
        echo -e "  ${DIM}Using last scan: $LAST_SCAN_FILE${NC}"
    fi
    
    echo ""
    echo -e "  ${BOLD}Output format:${NC}"
    echo -e "  ${GREEN}1)${NC} 📟 ASCII art ${DIM}(terminal view)${NC}"
    echo -e "  ${GREEN}2)${NC} 🌐 Interactive HTML ${DIM}(browser view)${NC}"
    echo -e "  ${GREEN}3)${NC} 📊 DOT/Graphviz ${DIM}(for graphviz)${NC}"
    echo -e "  ${GREEN}4)${NC} 📄 JSON ${DIM}(raw data)${NC}"
    echo -e "  ${GREEN}5)${NC} 🔄 Scan & display ${DIM}(fresh scan)${NC}"
    echo -e "  ${GREEN}0)${NC} Back"
    echo ""
    read -r -p "  Select: " topo_choice
    
    case "$topo_choice" in
        1)
            echo ""
            if [[ -n "$input_file" ]]; then
                python3 "$TOPOLOGY_HELPER" --input "$input_file" --ascii 2>&1 | sed 's/^/  /'
            else
                python3 "$TOPOLOGY_HELPER" --scan --ascii 2>&1 | sed 's/^/  /'
            fi
            ;;
        2)
            local outfile
            outfile=$(get_output_filename "topology" "html")
            echo ""
            print_progress "Generating topology visualization..."
            
            if [[ -n "$input_file" ]]; then
                python3 "$TOPOLOGY_HELPER" --input "$input_file" --html --output "$outfile" 2>&1 | sed 's/^/  /'
            else
                python3 "$TOPOLOGY_HELPER" --scan --html --output "$outfile" 2>&1 | sed 's/^/  /'
            fi
            
            if [[ -f "$outfile" ]]; then
                print_success "Topology saved: $outfile"
                open "$outfile" 2>/dev/null
            fi
            ;;
        3)
            local outfile
            outfile=$(get_output_filename "topology" "dot")
            echo ""
            
            if [[ -n "$input_file" ]]; then
                python3 "$TOPOLOGY_HELPER" --input "$input_file" --dot --output "$outfile" 2>&1 | sed 's/^/  /'
            else
                python3 "$TOPOLOGY_HELPER" --scan --dot --output "$outfile" 2>&1 | sed 's/^/  /'
            fi
            
            if [[ -f "$outfile" ]]; then
                print_success "DOT file saved: $outfile"
                echo -e "  ${DIM}Render with: dot -Tpng $outfile -o topology.png${NC}"
            fi
            ;;
        4)
            local outfile
            outfile=$(get_output_filename "topology" "json")
            echo ""
            
            if [[ -n "$input_file" ]]; then
                python3 "$TOPOLOGY_HELPER" --input "$input_file" --json --output "$outfile" 2>&1 | sed 's/^/  /'
            else
                python3 "$TOPOLOGY_HELPER" --scan --json --output "$outfile" 2>&1 | sed 's/^/  /'
            fi
            
            if [[ -f "$outfile" ]]; then
                print_success "JSON saved: $outfile"
            fi
            ;;
        5)
            echo ""
            print_progress "Scanning network..."
            python3 "$TOPOLOGY_HELPER" --scan --ascii 2>&1 | sed 's/^/  /'
            ;;
        0|"") return ;;
    esac
    
    press_enter
}

# S. Security Audit (v1.1)
run_security() {
    if ! has_security; then
        print_error "Security auditor not available"
        echo -e "  ${DIM}Check helpers/security.py exists and Python 3 is installed${NC}"
        press_enter
        return 1
    fi
    
    clear
    print_header "Security Audit"
    echo -e "  ${DIM}Scan for common vulnerabilities and security issues${NC}"
    echo ""
    
    # Check for scan data
    local input_file=""
    if [[ -n "$LAST_SCAN_FILE" ]] && [[ -f "$LAST_SCAN_FILE" ]]; then
        input_file="$LAST_SCAN_FILE"
        echo -e "  ${DIM}Using last scan: $LAST_SCAN_FILE${NC}"
    fi
    
    echo ""
    echo -e "  ${BOLD}Audit options:${NC}"
    echo -e "  ${GREEN}1)${NC} 🔍 Quick audit ${DIM}(scan from previous results)${NC}"
    echo -e "  ${GREEN}2)${NC} 🔬 Full audit ${DIM}(fresh scan + audit)${NC}"
    echo -e "  ${GREEN}3)${NC} 🎯 Audit single host"
    echo -e "  ${GREEN}4)${NC} 📄 Generate HTML report"
    echo -e "  ${GREEN}0)${NC} Back"
    echo ""
    read -r -p "  Select: " sec_choice
    
    case "$sec_choice" in
        1)
            echo ""
            if [[ -n "$input_file" ]]; then
                print_progress "Running security audit..."
                python3 "$SECURITY_HELPER" --input "$input_file" 2>&1 | sed 's/^/  /'
            else
                print_warning "No scan data available. Running fresh scan..."
                python3 "$SECURITY_HELPER" --scan 2>&1 | sed 's/^/  /'
            fi
            ;;
        2)
            echo ""
            print_progress "Scanning network and auditing..."
            echo -e "  ${DIM}This may take several minutes...${NC}"
            python3 "$SECURITY_HELPER" --scan 2>&1 | sed 's/^/  /'
            ;;
        3)
            echo ""
            echo -e "  ${CYAN}Target IP address:${NC}"
            read -r target_ip
            if [[ -n "$target_ip" ]]; then
                print_progress "Auditing $target_ip..."
                python3 "$SECURITY_HELPER" --target "$target_ip" 2>&1 | sed 's/^/  /'
            fi
            ;;
        4)
            local outfile
            outfile=$(get_output_filename "security_audit" "html")
            echo ""
            print_progress "Generating security report..."
            
            if [[ -n "$input_file" ]]; then
                python3 "$SECURITY_HELPER" --input "$input_file" --html --output "$outfile" 2>&1 | sed 's/^/  /'
            else
                python3 "$SECURITY_HELPER" --scan --html --output "$outfile" 2>&1 | sed 's/^/  /'
            fi
            
            if [[ -f "$outfile" ]]; then
                print_success "Report saved: $outfile"
                open "$outfile" 2>/dev/null
            fi
            ;;
        0|"") return ;;
    esac
    
    press_enter
}

# T. Generate Reports
generate_report() {
    if ! has_reports; then
        print_error "Report generator not available"
        echo -e "  ${DIM}Check helpers/report_generator.py exists and Python 3 is installed${NC}"
        press_enter
        return 1
    fi
    
    clear
    print_header "Generate Report"
    echo -e "  ${DIM}Create HTML, PDF, or Markdown reports${NC}"
    echo ""
    
    # Check if we have data
    local input_file=""
    if [[ -n "$LAST_SCAN_FILE" ]] && [[ -f "$LAST_SCAN_FILE" ]]; then
        input_file="$LAST_SCAN_FILE"
        echo -e "  ${DIM}Using: $(basename "$input_file")${NC}"
    elif [[ -n "$INPUT_FILE" ]] && [[ -f "$INPUT_FILE" ]]; then
        input_file="$INPUT_FILE"
        echo -e "  ${DIM}Using: $(basename "$input_file")${NC}"
    else
        echo -e "  ${YELLOW}⚠ No scan data loaded. Run a scan first or specify a file.${NC}"
        echo ""
        echo -e "  ${CYAN}Enter path to scan file (JSON format):${NC}"
        read -r input_file
        if [[ ! -f "$input_file" ]]; then
            print_error "File not found"
            press_enter
            return 1
        fi
    fi
    echo ""
    
    echo -e "  ${BOLD}Report type:${NC}"
    echo -e "  ${GREEN}1)${NC} 🌐 HTML report ${DIM}(web page with styling)${NC}"
    echo -e "  ${GREEN}2)${NC} � PDF report ${DIM}(requires reportlab)${NC}"
    echo -e "  ${GREEN}3)${NC} � Markdown report"
    echo -e "  ${GREEN}4)${NC} 🔄 Compare two scans"
    echo -e "  ${GREEN}0)${NC} Back"
    echo ""
    read -r -p "  Select: " report_choice
    
    local outfile
    
    case "$report_choice" in
        1)
            outfile=$(get_output_filename "report" "html")
            echo ""
            print_progress "Generating HTML report..."
            
            python3 "$REPORT_HELPER" "$input_file" --html --output "$outfile" 2>&1 | sed 's/^/  /'
            
            if [[ -f "$outfile" ]]; then
                print_success "HTML saved: $outfile"
                open "$outfile" 2>/dev/null
            fi
            ;;
        2)
            outfile=$(get_output_filename "report" "pdf")
            echo ""
            print_progress "Generating PDF report..."
            
            python3 "$REPORT_HELPER" "$input_file" --pdf "$outfile" 2>&1 | sed 's/^/  /'
            
            if [[ -f "$outfile" ]]; then
                print_success "PDF saved: $outfile"
                open "$outfile" 2>/dev/null
            fi
            ;;
        3)
            outfile=$(get_output_filename "report" "md")
            echo ""
            print_progress "Generating Markdown report..."
            
            python3 "$REPORT_HELPER" "$input_file" --markdown --output "$outfile" 2>&1 | sed 's/^/  /'
            
            if [[ -f "$outfile" ]]; then
                print_success "Markdown saved: $outfile"
                cat "$outfile" | head -30 | sed 's/^/  /'
                echo ""
            fi
            ;;
        4)
            echo ""
            echo -e "  ${CYAN}Previous scan file to compare:${NC}"
            read -r compare_file
            
            if [[ -f "$compare_file" ]]; then
                outfile=$(get_output_filename "comparison" "html")
                print_progress "Generating comparison report..."
                
                python3 "$REPORT_HELPER" "$input_file" --compare "$compare_file" --html --output "$outfile" 2>&1 | sed 's/^/  /'
                
                if [[ -f "$outfile" ]]; then
                    print_success "Comparison saved: $outfile"
                    open "$outfile" 2>/dev/null
                fi
            else
                print_error "Comparison file not found"
            fi
            ;;
        0|"") return ;;
    esac
    
    press_enter
}

# G. Configuration Manager
manage_config() {
    if ! has_config; then
        print_error "Configuration manager not available"
        echo -e "  ${DIM}Check helpers/config_manager.py exists and Python 3 is installed${NC}"
        press_enter
        return 1
    fi
    
    clear
    print_header "Configuration"
    echo -e "  ${DIM}Manage preferences, custom OUIs, and known devices${NC}"
    echo ""
    
    echo -e "  ${BOLD}Options:${NC}"
    echo -e "  ${GREEN}1)${NC} 📋 Show current config"
    echo -e "  ${GREEN}2)${NC} 🏭 Custom OUI definitions"
    echo -e "  ${GREEN}3)${NC} 📱 Known devices"
    echo -e "  ${GREEN}4)${NC} 🚫 Exclude list"
    echo -e "  ${GREEN}5)${NC} 💾 Export config"
    echo -e "  ${GREEN}6)${NC} � Import config"
    echo -e "  ${GREEN}7)${NC} � Reset to defaults"
    echo -e "  ${GREEN}0)${NC} Back"
    echo ""
    read -r -p "  Select: " config_choice
    
    case "$config_choice" in
        1)
            clear
            print_header "Current Configuration"
            python3 "$CONFIG_HELPER" --show 2>&1 | sed 's/^/  /'
            ;;
        2)
            clear
            print_header "Custom OUI Definitions"
            echo -e "  ${DIM}Add your own MAC vendor mappings${NC}"
            echo ""
            python3 "$CONFIG_HELPER" --list-ouis 2>&1 | sed 's/^/  /'
            echo ""
            echo -e "  ${CYAN}Add OUI? Enter 'PREFIX VENDOR' (e.g., 'AABBCC MyCompany'):${NC}"
            read -r oui_entry
            if [[ -n "$oui_entry" ]]; then
                local prefix="${oui_entry%% *}"
                local vendor="${oui_entry#* }"
                python3 "$CONFIG_HELPER" --add-oui "$prefix" "$vendor" 2>&1 | sed 's/^/  /'
            fi
            ;;
        3)
            clear
            print_header "Known Devices"
            python3 "$CONFIG_HELPER" --list-devices 2>&1 | sed 's/^/  /'
            echo ""
            echo -e "  ${GREEN}1)${NC} Add device"
            echo -e "  ${GREEN}2)${NC} Remove device"
            echo -e "  ${GREEN}0)${NC} Back"
            read -r -p "  Select: " device_action
            case "$device_action" in
                1)
                    echo -e "  ${CYAN}MAC address:${NC}"
                    read -r mac
                    echo -e "  ${CYAN}Device name:${NC}"
                    read -r name
                    [[ -n "$mac" && -n "$name" ]] && python3 "$CONFIG_HELPER" --add-device "$mac" "$name" 2>&1 | sed 's/^/  /'
                    ;;
                2)
                    echo -e "  ${CYAN}MAC address to remove:${NC}"
                    read -r mac
                    [[ -n "$mac" ]] && python3 "$CONFIG_HELPER" --remove-device "$mac" 2>&1 | sed 's/^/  /'
                    ;;
            esac
            ;;
        4)
            clear
            print_header "Exclude List"
            echo -e "  ${DIM}MACs/IPs to ignore in scans${NC}"
            echo ""
            python3 "$CONFIG_HELPER" --list-exclusions 2>&1 | sed 's/^/  /'
            echo ""
            echo -e "  ${GREEN}1)${NC} Exclude MAC"
            echo -e "  ${GREEN}2)${NC} Exclude IP"
            echo -e "  ${GREEN}3)${NC} Remove exclusion"
            echo -e "  ${GREEN}0)${NC} Back"
            read -r -p "  Select: " excl_action
            case "$excl_action" in
                1)
                    echo -e "  ${CYAN}MAC address to exclude:${NC}"
                    read -r mac
                    [[ -n "$mac" ]] && python3 "$CONFIG_HELPER" --exclude-mac "$mac" 2>&1 | sed 's/^/  /'
                    ;;
                2)
                    echo -e "  ${CYAN}IP address to exclude:${NC}"
                    read -r ip
                    [[ -n "$ip" ]] && python3 "$CONFIG_HELPER" --exclude-ip "$ip" 2>&1 | sed 's/^/  /'
                    ;;
                3)
                    echo -e "  ${CYAN}MAC or IP to un-exclude:${NC}"
                    read -r entry
                    if [[ -n "$entry" ]]; then
                        if [[ "$entry" == *:* ]]; then
                            python3 "$CONFIG_HELPER" --include-mac "$entry" 2>&1 | sed 's/^/  /'
                        else
                            python3 "$CONFIG_HELPER" --include-ip "$entry" 2>&1 | sed 's/^/  /'
                        fi
                    fi
                    ;;
            esac
            ;;
        5)
            local export_file
            export_file=$(get_output_filename "config_backup" "json")
            python3 "$CONFIG_HELPER" --export "$export_file" 2>&1 | sed 's/^/  /'
            print_success "Exported to: $export_file"
            ;;
        6)
            echo -e "  ${CYAN}Import file path:${NC}"
            read -r import_file
            [[ -f "$import_file" ]] && python3 "$CONFIG_HELPER" --import "$import_file" 2>&1 | sed 's/^/  /'
            ;;
        7)
            echo -e "  ${YELLOW}⚠ This will reset all configuration to defaults.${NC}"
            echo -e "  ${CYAN}Are you sure? [y/N]${NC}"
            read -r confirm
            [[ "$confirm" =~ ^[Yy]$ ]] && python3 "$CONFIG_HELPER" --reset 2>&1 | sed 's/^/  /'
            ;;
        0|"") return ;;
    esac
    
    press_enter
}

# B. Web Interface
start_web_server() {
    if ! has_web; then
        print_error "Web server not available"
        echo -e "  ${DIM}Check helpers/web_server.py exists and Python 3 is installed${NC}"
        press_enter
        return 1
    fi
    
    clear
    print_header "Web Interface"
    echo -e "  ${DIM}Browser-based dashboard and REST API${NC}"
    echo ""
    
    echo -e "  ${CYAN}Port (default 8080):${NC}"
    read -r port
    port="${port:-8080}"
    
    echo ""
    echo -e "  ${BOLD}Server will start at:${NC} ${GREEN}http://localhost:$port${NC}"
    echo -e "  ${DIM}Press Ctrl+C in terminal to stop${NC}"
    echo ""
    
    echo -e "  ${GREEN}1)${NC} Start in foreground ${DIM}(see logs)${NC}"
    echo -e "  ${GREEN}2)${NC} Start in background ${DIM}(daemon mode)${NC}"
    echo -e "  ${GREEN}0)${NC} Cancel"
    echo ""
    read -r -p "  Select: " start_mode
    
    case "$start_mode" in
        1)
            print_progress "Starting web server on port $port..."
            echo ""
            
            # Open browser after a short delay
            (sleep 2 && open "http://localhost:$port" 2>/dev/null) &
            
            python3 "$WEB_SERVER" --port "$port" 2>&1 | sed 's/^/  /'
            ;;
        2)
            print_progress "Starting web server in background..."
            
            # Start in background
            nohup python3 "$WEB_SERVER" --port "$port" > "$LOGS_DIR/web_server.log" 2>&1 &
            local pid=$!
            
            echo "$pid" > "$SCRIPT_DIR/.web_server.pid"
            
            sleep 1
            if kill -0 "$pid" 2>/dev/null; then
                print_success "Web server started (PID: $pid)"
                echo -e "  ${DIM}Log: $LOGS_DIR/web_server.log${NC}"
                echo ""
                
                # Open browser
                open "http://localhost:$port" 2>/dev/null
                
                echo -e "  ${CYAN}To stop: Use 'k' in scan menu or kill $pid${NC}"
            else
                print_error "Failed to start web server"
                cat "$LOGS_DIR/web_server.log" 2>/dev/null | tail -5 | sed 's/^/  /'
            fi
            ;;
        0|"") return ;;
    esac
    
    press_enter
}

# K. Kill Web Server
kill_web_server() {
    local pid_file="$SCRIPT_DIR/.web_server.pid"
    
    if [[ ! -f "$pid_file" ]]; then
        print_error "No web server PID file found"
        press_enter
        return 1
    fi
    
    local pid
    pid=$(cat "$pid_file" 2>/dev/null)
    
    if [[ -z "$pid" ]]; then
        print_error "Invalid PID file"
        rm -f "$pid_file"
        press_enter
        return 1
    fi
    
    echo ""
    if kill -0 "$pid" 2>/dev/null; then
        print_progress "Stopping web server (PID: $pid)..."
        kill "$pid" 2>/dev/null
        sleep 1
        
        if kill -0 "$pid" 2>/dev/null; then
            # Force kill if still running
            kill -9 "$pid" 2>/dev/null
        fi
        
        rm -f "$pid_file"
        print_success "Web server stopped"
    else
        print_warning "Web server was not running"
        rm -f "$pid_file"
    fi
    
    press_enter
}