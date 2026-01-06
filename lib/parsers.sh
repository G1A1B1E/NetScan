#!/bin/bash
# ============================================================================
# File Parsers - Support for multiple input formats
# ============================================================================

# Detect file format based on content
detect_file_format() {
    local file="$1"
    local first_lines=$(head -20 "$file")
    
    # Check for XML
    if echo "$first_lines" | grep -q '<?xml' || echo "$first_lines" | grep -qi '<nmaprun\|<host>'; then
        echo "nmap-xml"
        return
    fi
    
    # Check for JSON
    if echo "$first_lines" | grep -qE '^\s*[\[\{]'; then
        echo "json"
        return
    fi
    
    # Check for CSV (with header)
    if echo "$first_lines" | head -1 | grep -qiE '^(ip|mac|host|address|device).*,'; then
        echo "csv"
        return
    fi
    
    # Check for ARP table format: hostname (ip) at mac on interface
    if echo "$first_lines" | grep -qE '\([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\)\s+at\s+[0-9a-fA-F:]+'; then
        echo "arp-table"
        return
    fi
    
    # Default to plain text (try to extract IP/MAC pairs)
    echo "plain-text"
}

# ============================================================================
# XML Parser (nmap format)
# ============================================================================

parse_xml_file() {
    parse_xml_file_to "$TEMP_FILE"
}

parse_xml_file_to() {
    local outfile="$1"
    awk '
    BEGIN { 
        RS="</host>"
        ip = ""; mac = ""; hostname = ""
    }
    {
        ip = ""; mac = ""; hostname = ""
        
        n = split($0, parts, "addr=\"")
        for (i = 2; i <= n; i++) {
            split(parts[i], val, "\"")
            addr = val[1]
            
            if (parts[i] ~ /addrtype="ipv4"/) {
                if (addr ~ /^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$/) {
                    ip = addr
                }
            }
            if (parts[i] ~ /addrtype="mac"/) {
                if (addr ~ /^[0-9A-Fa-f][0-9A-Fa-f]:/) {
                    mac = addr
                }
            }
        }
        
        if (match($0, /hostname name="[^"]+"/)) {
            tmp = substr($0, RSTART, RLENGTH)
            gsub(/hostname name="/, "", tmp)
            gsub(/"/, "", tmp)
            hostname = tmp
        }
        
        if (ip != "") {
            print ip "|" mac "|" hostname "|"
        }
    }
    ' "$INPUT_FILE" > "$outfile"
}

# ============================================================================
# ARP Table Parser
# ============================================================================

parse_arp_file() {
    parse_arp_file_to "$TEMP_FILE"
}

parse_arp_file_to() {
    local outfile="$1"
    awk '
    function pad_mac(m) {
        n = split(m, parts, ":")
        result = ""
        for (i = 1; i <= n; i++) {
            if (length(parts[i]) == 1) {
                parts[i] = "0" parts[i]
            }
            result = result (i > 1 ? ":" : "") toupper(parts[i])
        }
        return result
    }
    
    {
        hostname = ""
        ip = ""
        mac = ""
        
        if (match($0, /^[^ ]+/)) {
            hostname = substr($0, RSTART, RLENGTH)
            if (hostname == "?") hostname = ""
        }
        
        if (match($0, /\([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\)/)) {
            ip = substr($0, RSTART+1, RLENGTH-2)
        }
        
        if (match($0, /at [0-9a-fA-F:]+/)) {
            mac = substr($0, RSTART+3, RLENGTH-3)
            mac = pad_mac(mac)
        }
        
        if (ip != "" && mac != "" && mac !~ /incomplete/ && mac !~ /FF:FF:FF:FF:FF:FF/) {
            print ip "|" mac "|" hostname "|"
        }
    }
    ' "$INPUT_FILE" > "$outfile"
}

# ============================================================================
# Plain Text Parser
# ============================================================================

parse_plain_text_file() {
    parse_plain_text_file_to "$TEMP_FILE"
}

parse_plain_text_file_to() {
    local outfile="$1"
    awk '
    function normalize_mac(m) {
        gsub(/[-.]/, "", m)
        m = toupper(m)
        if (length(m) == 12 && m ~ /^[0-9A-F]+$/) {
            return substr(m,1,2) ":" substr(m,3,2) ":" substr(m,5,2) ":" \
                   substr(m,7,2) ":" substr(m,9,2) ":" substr(m,11,2)
        }
        return m
    }
    
    {
        ip = ""
        mac = ""
        hostname = ""
        
        if (match($0, /[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/)) {
            ip = substr($0, RSTART, RLENGTH)
        }
        
        if (match($0, /[0-9a-fA-F]{1,2}[:-][0-9a-fA-F]{1,2}[:-][0-9a-fA-F]{1,2}[:-][0-9a-fA-F]{1,2}[:-][0-9a-fA-F]{1,2}[:-][0-9a-fA-F]{1,2}/)) {
            mac = substr($0, RSTART, RLENGTH)
            gsub(/-/, ":", mac)
        }
        else if (match($0, /[0-9a-fA-F]{4}\.[0-9a-fA-F]{4}\.[0-9a-fA-F]{4}/)) {
            mac = substr($0, RSTART, RLENGTH)
        }
        
        if (mac != "") {
            mac = normalize_mac(mac)
        }
        
        n = split($0, words, /[ \t,;]+/)
        for (i = 1; i <= n; i++) {
            w = words[i]
            if (w == ip) continue
            if (toupper(w) == mac) continue
            if (w ~ /^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$/) continue
            if (w ~ /^[0-9a-fA-F:.-]+$/ && length(w) > 10) continue
            if (tolower(w) ~ /^(ip|mac|host|hostname|address|device):?$/) continue
            if (w ~ /^[a-zA-Z]/ && length(w) > 1) {
                hostname = w
                break
            }
        }
        
        if (ip != "" && mac != "") {
            print ip "|" mac "|" hostname "|"
        }
    }
    ' "$INPUT_FILE" | sort -u > "$outfile"
}

# ============================================================================
# CSV Parser
# ============================================================================

parse_csv_file() {
    parse_csv_file_to "$TEMP_FILE"
}

parse_csv_file_to() {
    local outfile="$1"
    awk -F',' '
    BEGIN {
        ip_col = 0; mac_col = 0; host_col = 0
    }
    
    function normalize_mac(m) {
        gsub(/[-.]/, "", m)
        m = toupper(m)
        if (length(m) == 12 && m ~ /^[0-9A-F]+$/) {
            return substr(m,1,2) ":" substr(m,3,2) ":" substr(m,5,2) ":" \
                   substr(m,7,2) ":" substr(m,9,2) ":" substr(m,11,2)
        }
        return m
    }
    
    function trim(s) {
        gsub(/^[ \t"]+|[ \t"]+$/, "", s)
        return s
    }
    
    NR == 1 {
        for (i = 1; i <= NF; i++) {
            col = tolower(trim($i))
            if (col ~ /^ip/ || col == "address" || col == "ipaddress") ip_col = i
            else if (col ~ /^mac/ || col == "physical" || col == "hardware") mac_col = i
            else if (col ~ /^host/ || col == "name" || col == "device") host_col = i
        }
        if (ip_col == 0 && mac_col == 0 && $1 ~ /^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$/) {
            ip_col = 1; mac_col = 2; host_col = 3
            ip = trim($ip_col); mac = trim($mac_col); hostname = (host_col > 0) ? trim($host_col) : ""
            if (ip != "" && mac != "") print ip "|" normalize_mac(mac) "|" hostname "|"
        }
        next
    }
    
    ip_col > 0 {
        ip = trim($ip_col); mac = (mac_col > 0) ? trim($mac_col) : ""; hostname = (host_col > 0) ? trim($host_col) : ""
        if (ip != "" && ip ~ /^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$/) print ip "|" normalize_mac(mac) "|" hostname "|"
    }
    ' "$INPUT_FILE" > "$outfile"
}

# ============================================================================
# JSON Parser
# ============================================================================

parse_json_file() {
    parse_json_file_to "$TEMP_FILE"
}

parse_json_file_to() {
    local outfile="$1"
    if command -v jq &> /dev/null; then
        jq -r '
            (if type == "array" then . else [.] end) |
            .[] |
            select(type == "object") |
            ((.ip // .ipAddress // .ip_address // .IP // .address // "") | tostring) as $ip |
            ((.mac // .macAddress // .mac_address // .MAC // .hwaddr // "") | tostring) as $mac |
            ((.hostname // .host // .name // .deviceName // "") | tostring) as $host |
            select($ip != "" and $ip != "null") |
            "\($ip)|\($mac | ascii_upcase | gsub("-"; ":"))|\($host)|"
        ' "$INPUT_FILE" 2>/dev/null > "$outfile"
        
        if [ ! -s "$outfile" ]; then
            parse_json_fallback_to "$outfile"
        fi
    else
        parse_json_fallback_to "$outfile"
    fi
}

parse_json_fallback_to() {
    local outfile="$1"
    awk '
    BEGIN { RS="[{},\n]"; ip=""; mac=""; host="" }
    
    /"ip"|"ipAddress"|"ip_address"|"address"/ {
        n = split($0, parts, "\"")
        for (i=1; i<=length(parts); i++) {
            if (parts[i] ~ /^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$/) {
                ip = parts[i]
                break
            }
        }
    }
    
    /"mac"|"macAddress"|"mac_address"|"hwaddr"/ {
        n = split($0, parts, "\"")
        for (i=1; i<=length(parts); i++) {
            if (parts[i] ~ /^[0-9a-fA-F:.-]+$/ && length(parts[i]) >= 12) {
                mac = toupper(parts[i])
                gsub(/-/, ":", mac)
                break
            }
        }
    }
    
    /"hostname"|"host"|"name"|"deviceName"/ {
        n = split($0, parts, "\"")
        for (i=1; i<=length(parts); i++) {
            if (parts[i] !~ /^(hostname|host|name|deviceName|:|,|\s)*$/ && length(parts[i]) > 0) {
                host = parts[i]
                break
            }
        }
    }
    
    /}/ {
        if (ip != "") {
            print ip "|" mac "|" host "|"
        }
        ip = ""; mac = ""; host = ""
    }
    ' "$INPUT_FILE" > "$outfile"
}
