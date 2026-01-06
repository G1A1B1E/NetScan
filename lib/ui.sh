#!/bin/bash
# ============================================================================
# UI Functions - Banner, Menu, and Display Helpers
# ============================================================================

show_banner() {
    clear
    echo -e "${CYAN}"
    echo "  ╔═══════════════════════════════════════════════════════════════╗"
    echo "  ║                                                               ║"
    echo -e "  ║        ${BOLD}${WHITE}🔍 NetScan - Network Device Finder${NC}${CYAN}                    ║"
    echo "  ║                                                               ║"
    echo "  ╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

show_menu() {
    echo -e "${BOLD}${YELLOW}  MAIN MENU${NC}"
    echo -e "${DIM}  ─────────────────────────────────────────${NC}"
    echo ""
    echo -e "  ${GREEN}1)${NC} 📂 Load file (XML, ARP, CSV, JSON, or text)"
    echo -e "  ${GREEN}2)${NC} 📚 Load multiple files"
    echo -e "  ${GREEN}3)${NC} 📋 List all devices"
    echo -e "  ${GREEN}4)${NC} 🔎 Search devices"
    echo -e "  ${GREEN}5)${NC} 🏭 Search by vendor"
    echo -e "  ${GREEN}6)${NC} 🌐 Find IP by hostname"
    echo -e "  ${GREEN}7)${NC} 💻 Find IP by MAC address"
    echo -e "  ${GREEN}8)${NC} 📊 Show network summary"
    echo -e "  ${GREEN}9)${NC} 💾 Export to CSV"
    echo ""
    echo -e "  ${GREEN}s)${NC} 📡 Network scanning"
    echo -e "  ${GREEN}e)${NC} 📁 Load example files"
    echo -e "  ${GREEN}r)${NC} 🔄 Refresh vendor data"
    echo -e "  ${GREEN}c)${NC} ⚙️  System capabilities"
    echo -e "  ${GREEN}0)${NC} 🚪 Exit"
    echo ""
    echo -e "${DIM}  ─────────────────────────────────────────${NC}"
    
    if [ -n "$INPUT_FILE" ]; then
        echo -e "  ${DIM}Loaded: ${NC}${CYAN}$INPUT_FILE${NC} ${DIM}(${FILE_FORMAT})${NC}"
        DEVICE_COUNT=$(wc -l < "$TEMP_FILE" | tr -d ' ')
        echo -e "  ${DIM}Devices: ${NC}${GREEN}$DEVICE_COUNT${NC}"
    else
        echo -e "  ${DIM}No file loaded${NC}"
    fi
    echo ""
}

press_enter() {
    echo ""
    echo -e "${DIM}  Press Enter to continue...${NC}"
    read -r
}

check_file_loaded() {
    if [ -z "$INPUT_FILE" ]; then
        echo ""
        echo -e "  ${RED}✗ No file loaded! Please load a file first (option 1)${NC}"
        echo -e "  ${DIM}Supported formats: nmap XML, ARP table, CSV, JSON, plain text${NC}"
        press_enter
        return 1
    fi
    return 0
}

# Print a section header
print_header() {
    local title="$1"
    echo ""
    echo -e "${BOLD}${CYAN}  $title${NC}"
    echo -e "${DIM}  ════════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Print a sub-header
print_subheader() {
    local title="$1"
    echo ""
    echo -e "${BOLD}${CYAN}  $title${NC}"
    echo -e "${DIM}  ─────────────────────────────────────────${NC}"
    echo ""
}

# Print success message
print_success() {
    echo -e "  ${GREEN}✓ $1${NC}"
}

# Print error message
print_error() {
    echo -e "  ${RED}✗ $1${NC}"
}

# Print warning message
print_warning() {
    echo -e "  ${YELLOW}⚠ $1${NC}"
}

# Print info message
print_info() {
    echo -e "  ${CYAN}ℹ $1${NC}"
}

# Print progress message
print_progress() {
    echo -e "  ${YELLOW}⏳ $1${NC}"
}
