#!/bin/bash
# ============================================================================
# Search and Display Functions
# ============================================================================

# List all devices
list_all_devices() {
    check_file_loaded || return
    
    print_header "ALL NETWORK DEVICES"
    
    local num=0
    while IFS='|' read -r ip mac hostname vendor_cache; do
        ((num++))
        
        [ -z "$hostname" ] && hostname="(No hostname)"
        [ -z "$mac" ] && mac="N/A"
        
        # Check if we have cached vendor, otherwise lookup
        if [ -z "$vendor_cache" ]; then
            echo -ne "  ${DIM}Looking up vendor for device #$num...${NC}\r"
            sleep 0.3
            vendor_cache=$(lookup_vendor "$mac")
        fi
        
        echo -e "  ${BOLD}#$num${NC} ${YELLOW}$hostname${NC}"
        echo -e "      IP: ${CYAN}$ip${NC}  MAC: ${BLUE}$mac${NC}"
        echo -e "      Vendor: ${GREEN}$vendor_cache${NC}"
        echo ""
    done < "$TEMP_FILE"
    
    echo -e "${DIM}  ════════════════════════════════════════════════════════════${NC}"
    echo -e "  Total: ${GREEN}$num${NC} devices"
    echo ""
    press_enter
}

# Search devices by any field
search_devices() {
    check_file_loaded || return
    
    echo ""
    echo -e "${CYAN}  Enter search term (hostname, IP, or MAC):${NC}"
    read -r -p "  > " search_term
    
    if [ -z "$search_term" ]; then
        print_error "No search term entered"
        press_enter
        return
    fi
    
    log_action "Search devices: '$search_term'"
    
    print_header "SEARCH RESULTS FOR: ${YELLOW}$search_term${NC}"
    
    local found=0
    local num=0
    while IFS='|' read -r ip mac hostname vendor_cache; do
        ((num++))
        
        [ -z "$hostname" ] && hostname="(No hostname)"
        [ -z "$mac" ] && mac="N/A"
        
        # Case-insensitive search
        if echo "$ip $mac $hostname" | grep -qi "$search_term"; then
            ((found++))
            
            if [ -z "$vendor_cache" ]; then
                sleep 0.3
                vendor_cache=$(lookup_vendor "$mac")
            fi
            
            echo -e "  ${BOLD}#$num${NC} ${YELLOW}$hostname${NC}"
            echo -e "      IP: ${CYAN}$ip${NC}  MAC: ${BLUE}$mac${NC}"
            echo -e "      Vendor: ${GREEN}$vendor_cache${NC}"
            echo ""
        fi
    done < "$TEMP_FILE"
    
    log_action "Search results: $found device(s) found for '$search_term'"
    
    if [ $found -eq 0 ]; then
        print_error "No devices found matching '$search_term'"
    else
        echo -e "${DIM}  ════════════════════════════════════════════════════════════${NC}"
        echo -e "  Found: ${GREEN}$found${NC} device(s)"
    fi
    echo ""
    press_enter
}

# Search by vendor name
search_by_vendor() {
    check_file_loaded || return
    
    echo ""
    echo -e "${CYAN}  Enter vendor name (e.g., Apple, Samsung, Amazon, Google):${NC}"
    read -r -p "  > " vendor_search
    
    if [ -z "$vendor_search" ]; then
        print_error "No vendor entered"
        press_enter
        return
    fi
    
    log_action "Search by vendor: '$vendor_search'"
    
    print_header "DEVICES FROM VENDOR: ${YELLOW}$vendor_search${NC}"
    print_progress "Querying vendor database..."
    echo ""
    
    local found=0
    local num=0
    while IFS='|' read -r ip mac hostname vendor_cache; do
        ((num++))
        
        [ -z "$hostname" ] && hostname="(No hostname)"
        [ -z "$mac" ] && mac="N/A"
        
        if [ -n "$mac" ] && [ "$mac" != "N/A" ]; then
            sleep 0.3
            vendor=$(lookup_vendor "$mac")
            
            if echo "$vendor" | grep -qi "$vendor_search"; then
                ((found++))
                echo -e "  ${BOLD}#$num${NC} ${YELLOW}$hostname${NC}"
                echo -e "      IP: ${CYAN}$ip${NC}  MAC: ${BLUE}$mac${NC}"
                echo -e "      Vendor: ${GREEN}$vendor${NC}"
                echo ""
            fi
        fi
    done < "$TEMP_FILE"
    
    log_action "Vendor search results: $found device(s) found for '$vendor_search'"
    
    if [ $found -eq 0 ]; then
        print_error "No devices found from vendor '$vendor_search'"
    else
        echo -e "${DIM}  ════════════════════════════════════════════════════════════${NC}"
        echo -e "  Found: ${GREEN}$found${NC} device(s)"
    fi
    echo ""
    press_enter
}

# Find IP by hostname
find_ip_by_hostname() {
    check_file_loaded || return
    
    echo ""
    echo -e "${CYAN}  Enter hostname (partial match OK):${NC}"
    read -r -p "  > " hostname_search
    
    if [ -z "$hostname_search" ]; then
        print_error "No hostname entered"
        press_enter
        return
    fi
    
    log_action "Find IP by hostname: '$hostname_search'"
    
    print_subheader "IP ADDRESSES FOR: ${YELLOW}$hostname_search${NC}"
    
    local found=0
    while IFS='|' read -r ip mac hostname vendor_cache; do
        if echo "$hostname" | grep -qi "$hostname_search"; then
            ((found++))
            echo -e "  ${YELLOW}$hostname${NC}"
            echo -e "    └── IP: ${BOLD}${CYAN}$ip${NC}"
            echo ""
        fi
    done < "$TEMP_FILE"
    
    log_action "Hostname search results: $found device(s) found for '$hostname_search'"
    
    if [ $found -eq 0 ]; then
        print_error "No devices found with hostname matching '$hostname_search'"
    fi
    echo ""
    press_enter
}

# Find IP by MAC address
find_ip_by_mac() {
    check_file_loaded || return
    
    echo ""
    echo -e "${CYAN}  Enter MAC address (full or partial):${NC}"
    read -r -p "  > " mac_search
    
    if [ -z "$mac_search" ]; then
        print_error "No MAC address entered"
        press_enter
        return
    fi
    
    log_action "Find IP by MAC: '$mac_search'"
    
    print_subheader "DEVICE WITH MAC: ${YELLOW}$mac_search${NC}"
    
    local found=0
    while IFS='|' read -r ip mac hostname vendor_cache; do
        if echo "$mac" | grep -qi "$mac_search"; then
            ((found++))
            [ -z "$hostname" ] && hostname="(No hostname)"
            
            sleep 0.3
            vendor=$(lookup_vendor "$mac")
            
            echo -e "  ${BLUE}$mac${NC}"
            echo -e "    ├── IP: ${BOLD}${CYAN}$ip${NC}"
            echo -e "    ├── Hostname: ${YELLOW}$hostname${NC}"
            echo -e "    └── Vendor: ${GREEN}$vendor${NC}"
            echo ""
        fi
    done < "$TEMP_FILE"
    
    log_action "MAC search results: $found device(s) found for '$mac_search'"
    
    if [ $found -eq 0 ]; then
        print_error "No devices found with MAC matching '$mac_search'"
    fi
    echo ""
    press_enter
}

# Show network summary
show_summary() {
    check_file_loaded || return
    
    print_header "NETWORK SUMMARY"
    
    local total=0
    local with_hostname=0
    local without_mac=0
    
    while IFS='|' read -r ip mac hostname vendor_cache; do
        ((total++))
        [ -n "$hostname" ] && ((with_hostname++))
        [ -z "$mac" ] && ((without_mac++))
    done < "$TEMP_FILE"
    
    echo -e "  ${BOLD}Total Devices:${NC}        ${GREEN}$total${NC}"
    echo -e "  ${BOLD}With Hostname:${NC}        ${CYAN}$with_hostname${NC}"
    echo -e "  ${BOLD}Without Hostname:${NC}     ${YELLOW}$((total - with_hostname))${NC}"
    echo -e "  ${BOLD}Without MAC:${NC}          ${RED}$without_mac${NC} (likely scanning host)"
    echo ""
    
    echo -e "${BOLD}  ${MAGENTA}IP Address Range:${NC}"
    local first_ip=$(head -1 "$TEMP_FILE" | cut -d'|' -f1)
    local last_ip=$(tail -1 "$TEMP_FILE" | cut -d'|' -f1)
    echo -e "    First: ${CYAN}$first_ip${NC}"
    echo -e "    Last:  ${CYAN}$last_ip${NC}"
    echo ""
    
    echo -e "${BOLD}  ${MAGENTA}Devices with Names:${NC}"
    while IFS='|' read -r ip mac hostname vendor_cache; do
        if [ -n "$hostname" ]; then
            echo -e "    • ${YELLOW}$hostname${NC} → ${CYAN}$ip${NC}"
        fi
    done < "$TEMP_FILE"
    
    echo ""
    press_enter
}
