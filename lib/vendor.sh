#!/bin/bash
# ============================================================================
# Vendor Lookup Functions
# ============================================================================

# Lookup vendor by MAC address using macvendors.com API
# Uses Python cache helper if available for better performance
lookup_vendor() {
    local mac="$1"
    local vendor=""
    
    if [ -z "$mac" ]; then
        echo "N/A"
        return
    fi
    
    # Try Python cache helper first (faster, with caching)
    if $HAS_VENDOR_CACHE; then
        vendor=$(run_python_helper "$VENDOR_CACHE_PY" "$mac" 2>/dev/null)
        if [ -n "$vendor" ] && [[ "$vendor" != "Error"* ]]; then
            echo "$vendor"
            return
        fi
    fi
    
    # Fallback to direct API call
    vendor=$(curl -s --max-time 3 "https://api.macvendors.com/$mac" 2>/dev/null)
    
    if [ -z "$vendor" ] || [[ "$vendor" == *"Not Found"* ]] || [[ "$vendor" == *"Too Many Requests"* ]] || [[ "$vendor" == *"errors"* ]]; then
        vendor="Unknown"
    fi
    
    echo "$vendor"
}

# Batch lookup vendors for multiple MACs (much faster with Python helper)
batch_lookup_vendors() {
    local mac_list="$1"  # Newline-separated list of MACs
    
    if $HAS_VENDOR_CACHE; then
        # Use Python helper for batch lookup
        echo "$mac_list" | run_python_helper "$VENDOR_CACHE_PY" --batch 2>/dev/null
        return $?
    else
        # Fallback to individual lookups
        while IFS= read -r mac; do
            local vendor=$(lookup_vendor "$mac")
            echo "$mac|$vendor"
        done <<< "$mac_list"
    fi
}

# Normalize MAC address format
normalize_mac() {
    local mac="$1"
    local format="${2:-colon}"  # colon, dash, cisco, bare
    
    if $HAS_MAC_NORMALIZER; then
        run_python_helper "$MAC_NORMALIZER_PY" -f "$format" "$mac" 2>/dev/null
    else
        # Simple bash normalization (colon format only)
        echo "$mac" | tr '[:upper:]' '[:lower:]' | sed 's/[-.]//g' | sed 's/\(..\)/\1:/g' | sed 's/:$//'
    fi
}

# Validate MAC address
is_valid_mac() {
    local mac="$1"
    
    if $HAS_MAC_NORMALIZER; then
        run_python_helper "$MAC_NORMALIZER_PY" --validate "$mac" 2>/dev/null
        return $?
    else
        # Simple regex validation
        [[ "$mac" =~ ^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$ ]] || \
        [[ "$mac" =~ ^([0-9A-Fa-f]{4}\.){2}([0-9A-Fa-f]{4})$ ]] || \
        [[ "$mac" =~ ^[0-9A-Fa-f]{12}$ ]]
    fi
}

# Get vendor cache stats
vendor_cache_stats() {
    if $HAS_VENDOR_CACHE; then
        echo ""
        echo -e "${CYAN}  Vendor Cache Statistics:${NC}"
        echo ""
        run_python_helper "$VENDOR_CACHE_PY" --stats 2>/dev/null | sed 's/^/    /'
        echo ""
    else
        echo ""
        echo -e "${YELLOW}  Python vendor cache not available${NC}"
        echo ""
    fi
}

# Clean up old cache entries
cleanup_vendor_cache() {
    if $HAS_VENDOR_CACHE; then
        run_python_helper "$VENDOR_CACHE_PY" --cleanup 2>/dev/null
        return $?
    fi
    return 1
}

# Refresh vendor data for all devices in TEMP_FILE
refresh_vendors() {
    check_file_loaded || return
    
    echo ""
    print_progress "Refreshing vendor data for all devices..."
    echo ""
    
    local new_temp=$(mktemp)
    local num=0
    local total=$(wc -l < "$TEMP_FILE" | tr -d ' ')
    
    # Collect all MACs for batch lookup
    if $HAS_VENDOR_CACHE; then
        local macs=""
        while IFS='|' read -r ip mac hostname vendor_cache; do
            if [ -n "$mac" ]; then
                macs+="$mac"$'\n'
            fi
        done < "$TEMP_FILE"
        
        # Batch lookup
        declare -A vendor_map
        while IFS='|' read -r mac vendor; do
            vendor_map["$mac"]="$vendor"
        done < <(echo "$macs" | run_python_helper "$VENDOR_CACHE_PY" --batch 2>/dev/null)
        
        # Write results
        while IFS='|' read -r ip mac hostname vendor_cache; do
            ((num++))
            echo -ne "  ${DIM}Processing device $num/$total...${NC}\r"
            
            if [ -n "$mac" ]; then
                vendor="${vendor_map[$mac]:-Unknown}"
            else
                vendor=""
            fi
            
            echo "$ip|$mac|$hostname|$vendor" >> "$new_temp"
        done < "$TEMP_FILE"
    else
        # Fallback to individual lookups
        while IFS='|' read -r ip mac hostname vendor_cache; do
            ((num++))
            echo -ne "  ${DIM}Processing device $num/$total...${NC}\r"
            
            if [ -n "$mac" ]; then
                sleep 0.3
                vendor=$(lookup_vendor "$mac")
            else
                vendor=""
            fi
            
            echo "$ip|$mac|$hostname|$vendor" >> "$new_temp"
        done < "$TEMP_FILE"
    fi
    
    mv "$new_temp" "$TEMP_FILE"
    
    echo ""
    print_success "Vendor data refreshed for $num devices"
    echo ""
    press_enter
}
