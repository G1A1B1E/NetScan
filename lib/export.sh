#!/bin/bash
# ============================================================================
# Export Functions
# ============================================================================

# Convert internal data format to JSON for Python helper
convert_to_json_array() {
    local json="["
    local first=1
    
    while IFS='|' read -r ip mac hostname vendor; do
        [ -z "$hostname" ] && hostname=""
        [ -z "$mac" ] && mac=""
        [ -z "$vendor" ] && vendor=""
        
        # Escape quotes
        hostname=$(echo "$hostname" | sed 's/"/\\"/g')
        vendor=$(echo "$vendor" | sed 's/"/\\"/g')
        
        if [ $first -eq 1 ]; then
            first=0
        else
            json+=","
        fi
        
        json+="{\"ip\":\"$ip\",\"mac\":\"$mac\",\"hostname\":\"$hostname\",\"vendor\":\"$vendor\"}"
    done < "$TEMP_FILE"
    
    json+="]"
    echo "$json"
}

# Export devices to CSV file
export_to_csv() {
    check_file_loaded || return
    
    echo ""
    echo -e "${CYAN}  Enter output filename (default: network_devices_TIMESTAMP.csv):${NC}"
    echo -e "${DIM}  Files are saved to: $EXPORTS_DIR${NC}"
    read -r -p "  > " output_file
    
    # Generate default filename with timestamp if not provided
    if [ -z "$output_file" ]; then
        output_file="network_devices_$(date +%Y%m%d_%H%M%S).csv"
    fi
    
    # If filename doesn't have a path, put it in exports folder
    if [[ "$output_file" != */* ]]; then
        output_file="$EXPORTS_DIR/$output_file"
    else
        # Expand ~ to home directory
        output_file="${output_file/#\~/$HOME}"
    fi
    
    echo ""
    print_progress "Exporting to CSV..."
    
    local device_count=0
    
    # Use Python export helper if available
    if $HAS_EXPORT_HELPER; then
        # Prepare JSON data with vendor lookup
        local json_data="["
        local first=1
        
        while IFS='|' read -r ip mac hostname vendor_cache; do
            [ -z "$hostname" ] && hostname=""
            [ -z "$mac" ] && mac=""
            
            if [ -n "$mac" ]; then
                vendor=$(lookup_vendor "$mac")
            else
                vendor="N/A"
            fi
            
            # Escape quotes
            hostname=$(echo "$hostname" | sed 's/"/\\"/g')
            vendor=$(echo "$vendor" | sed 's/"/\\"/g')
            
            if [ $first -eq 1 ]; then
                first=0
            else
                json_data+=","
            fi
            
            json_data+="{\"ip\":\"$ip\",\"mac\":\"$mac\",\"hostname\":\"$hostname\",\"vendor\":\"$vendor\"}"
            ((device_count++))
        done < "$TEMP_FILE"
        
        json_data+="]"
        
        # Use Python helper for clean CSV output
        echo "$json_data" | run_python_helper "$EXPORT_HELPER_PY" --to csv --fields "ip,mac,hostname,vendor" > "$output_file"
    else
        # Fallback to bash implementation
        echo "IP Address,MAC Address,Hostname,Vendor" > "$output_file"
        
        while IFS='|' read -r ip mac hostname vendor_cache; do
            [ -z "$hostname" ] && hostname=""
            [ -z "$mac" ] && mac=""
            
            if [ -n "$mac" ]; then
                sleep 0.3
                vendor=$(lookup_vendor "$mac")
            else
                vendor="N/A"
            fi
            
            # Escape commas in fields
            hostname=$(echo "$hostname" | sed 's/,/;/g')
            vendor=$(echo "$vendor" | sed 's/,/;/g')
            
            echo "$ip,$mac,$hostname,$vendor" >> "$output_file"
            ((device_count++))
        done < "$TEMP_FILE"
    fi
    
    log_export "Exported $device_count devices to: $output_file"
    print_success "Exported to: $output_file"
    echo ""
    press_enter
}

# Export to JSON format
export_to_json() {
    check_file_loaded || return
    
    echo ""
    echo -e "${CYAN}  Enter output filename (default: network_devices_TIMESTAMP.json):${NC}"
    echo -e "${DIM}  Files are saved to: $EXPORTS_DIR${NC}"
    read -r -p "  > " output_file
    
    if [ -z "$output_file" ]; then
        output_file="network_devices_$(date +%Y%m%d_%H%M%S).json"
    fi
    
    if [[ "$output_file" != */* ]]; then
        output_file="$EXPORTS_DIR/$output_file"
    else
        output_file="${output_file/#\~/$HOME}"
    fi
    
    echo ""
    print_progress "Exporting to JSON..."
    
    local device_count=0
    
    # Use Python export helper if available
    if $HAS_EXPORT_HELPER; then
        # Prepare JSON data with vendor lookup
        local json_data="["
        local first=1
        
        while IFS='|' read -r ip mac hostname vendor_cache; do
            [ -z "$hostname" ] && hostname=""
            [ -z "$mac" ] && mac=""
            
            if [ -n "$mac" ]; then
                vendor=$(lookup_vendor "$mac")
            else
                vendor="N/A"
            fi
            
            # Escape quotes
            hostname=$(echo "$hostname" | sed 's/"/\\"/g')
            vendor=$(echo "$vendor" | sed 's/"/\\"/g')
            
            if [ $first -eq 1 ]; then
                first=0
            else
                json_data+=","
            fi
            
            json_data+="{\"ip\":\"$ip\",\"mac\":\"$mac\",\"hostname\":\"$hostname\",\"vendor\":\"$vendor\"}"
            ((device_count++))
        done < "$TEMP_FILE"
        
        json_data+="]"
        
        # Use Python helper for clean JSON output
        echo "$json_data" | run_python_helper "$EXPORT_HELPER_PY" --to json > "$output_file"
    else
        # Fallback to bash implementation
        echo "[" > "$output_file"
        
        local first=1
        while IFS='|' read -r ip mac hostname vendor_cache; do
            [ -z "$hostname" ] && hostname=""
            [ -z "$mac" ] && mac=""
            
            if [ -n "$mac" ]; then
                sleep 0.3
                vendor=$(lookup_vendor "$mac")
            else
                vendor="N/A"
            fi
            
            # Escape quotes in fields
            hostname=$(echo "$hostname" | sed 's/"/\\"/g')
            vendor=$(echo "$vendor" | sed 's/"/\\"/g')
            
            if [ $first -eq 1 ]; then
                first=0
            else
                echo "," >> "$output_file"
            fi
            
            echo "  {" >> "$output_file"
            echo "    \"ip\": \"$ip\"," >> "$output_file"
            echo "    \"mac\": \"$mac\"," >> "$output_file"
            echo "    \"hostname\": \"$hostname\"," >> "$output_file"
            echo "    \"vendor\": \"$vendor\"" >> "$output_file"
            echo -n "  }" >> "$output_file"
            
            ((device_count++))
        done < "$TEMP_FILE"
        
        echo "" >> "$output_file"
        echo "]" >> "$output_file"
    fi
    
    log_export "Exported $device_count devices to JSON: $output_file"
    print_success "Exported to: $output_file"
    echo ""
    press_enter
}

# Export to HTML format
export_to_html() {
    check_file_loaded || return
    
    echo ""
    echo -e "${CYAN}  Enter output filename (default: network_devices_TIMESTAMP.html):${NC}"
    echo -e "${DIM}  Files are saved to: $EXPORTS_DIR${NC}"
    read -r -p "  > " output_file
    
    if [ -z "$output_file" ]; then
        output_file="network_devices_$(date +%Y%m%d_%H%M%S).html"
    fi
    
    if [[ "$output_file" != */* ]]; then
        output_file="$EXPORTS_DIR/$output_file"
    else
        output_file="${output_file/#\~/$HOME}"
    fi
    
    echo ""
    print_progress "Exporting to HTML..."
    
    local device_count=0
    
    # Prepare JSON data with vendor lookup
    local json_data="["
    local first=1
    
    while IFS='|' read -r ip mac hostname vendor_cache; do
        [ -z "$hostname" ] && hostname=""
        [ -z "$mac" ] && mac=""
        
        if [ -n "$mac" ]; then
            vendor=$(lookup_vendor "$mac")
        else
            vendor="N/A"
        fi
        
        # Escape quotes
        hostname=$(echo "$hostname" | sed 's/"/\\"/g')
        vendor=$(echo "$vendor" | sed 's/"/\\"/g')
        
        if [ $first -eq 1 ]; then
            first=0
        else
            json_data+=","
        fi
        
        json_data+="{\"ip\":\"$ip\",\"mac\":\"$mac\",\"hostname\":\"$hostname\",\"vendor\":\"$vendor\"}"
        ((device_count++))
    done < "$TEMP_FILE"
    
    json_data+="]"
    
    # Use Python export helper if available
    if $HAS_EXPORT_HELPER; then
        echo "$json_data" | run_python_helper "$EXPORT_HELPER_PY" --to html --full-html --title "Network Devices" --fields "ip,mac,hostname,vendor" > "$output_file"
    else
        # Fallback to simple HTML
        {
            echo "<!DOCTYPE html><html><head><title>Network Devices</title>"
            echo "<style>table{border-collapse:collapse;width:100%}th,td{border:1px solid #ddd;padding:8px;text-align:left}th{background:#4a90d9;color:white}tr:nth-child(even){background:#f9f9f9}</style>"
            echo "</head><body><h1>Network Devices</h1><table>"
            echo "<tr><th>IP Address</th><th>MAC Address</th><th>Hostname</th><th>Vendor</th></tr>"
            
            echo "$json_data" | $PYTHON_CMD -c "
import json, sys, html
data = json.load(sys.stdin)
for d in data:
    print(f'<tr><td>{html.escape(d.get(\"ip\", \"\"))}</td><td>{html.escape(d.get(\"mac\", \"\"))}</td><td>{html.escape(d.get(\"hostname\", \"\"))}</td><td>{html.escape(d.get(\"vendor\", \"\"))}</td></tr>')
" 2>/dev/null || {
                # Even simpler fallback without Python
                while IFS='|' read -r ip mac hostname vendor_cache; do
                    echo "<tr><td>$ip</td><td>$mac</td><td>$hostname</td><td>$vendor</td></tr>"
                done < "$TEMP_FILE"
            }
            
            echo "</table><p>Generated: $(date)</p></body></html>"
        } > "$output_file"
    fi
    
    log_export "Exported $device_count devices to HTML: $output_file"
    print_success "Exported to: $output_file"
    echo ""
    press_enter
}

# Export to Markdown format
export_to_markdown() {
    check_file_loaded || return
    
    echo ""
    echo -e "${CYAN}  Enter output filename (default: network_devices_TIMESTAMP.md):${NC}"
    echo -e "${DIM}  Files are saved to: $EXPORTS_DIR${NC}"
    read -r -p "  > " output_file
    
    if [ -z "$output_file" ]; then
        output_file="network_devices_$(date +%Y%m%d_%H%M%S).md"
    fi
    
    if [[ "$output_file" != */* ]]; then
        output_file="$EXPORTS_DIR/$output_file"
    else
        output_file="${output_file/#\~/$HOME}"
    fi
    
    echo ""
    print_progress "Exporting to Markdown..."
    
    local device_count=0
    
    # Prepare JSON data with vendor lookup
    local json_data="["
    local first=1
    
    while IFS='|' read -r ip mac hostname vendor_cache; do
        [ -z "$hostname" ] && hostname=""
        [ -z "$mac" ] && mac=""
        
        if [ -n "$mac" ]; then
            vendor=$(lookup_vendor "$mac")
        else
            vendor="N/A"
        fi
        
        # Escape quotes
        hostname=$(echo "$hostname" | sed 's/"/\\"/g')
        vendor=$(echo "$vendor" | sed 's/"/\\"/g')
        
        if [ $first -eq 1 ]; then
            first=0
        else
            json_data+=","
        fi
        
        json_data+="{\"ip\":\"$ip\",\"mac\":\"$mac\",\"hostname\":\"$hostname\",\"vendor\":\"$vendor\"}"
        ((device_count++))
    done < "$TEMP_FILE"
    
    json_data+="]"
    
    # Use Python export helper if available
    if $HAS_EXPORT_HELPER; then
        {
            echo "# Network Devices"
            echo ""
            echo "Generated: $(date)"
            echo ""
            echo "$json_data" | run_python_helper "$EXPORT_HELPER_PY" --to markdown --fields "ip,mac,hostname,vendor"
        } > "$output_file"
    else
        # Fallback to bash implementation
        {
            echo "# Network Devices"
            echo ""
            echo "Generated: $(date)"
            echo ""
            echo "| IP Address | MAC Address | Hostname | Vendor |"
            echo "| --- | --- | --- | --- |"
            
            while IFS='|' read -r ip mac hostname vendor_cache; do
                [ -z "$hostname" ] && hostname=""
                [ -z "$mac" ] && mac=""
                vendor="${vendor_cache:-Unknown}"
                echo "| $ip | $mac | $hostname | $vendor |"
            done < "$TEMP_FILE"
        } > "$output_file"
    fi
    
    log_export "Exported $device_count devices to Markdown: $output_file"
    print_success "Exported to: $output_file"
    echo ""
    press_enter
}
