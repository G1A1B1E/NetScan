#!/bin/bash
# ============================================================================
# File Loading Functions
# ============================================================================

# Load a single file
load_file() {
    echo ""
    echo -e "${CYAN}Enter the path to your file (or drag & drop):${NC}"
    echo -e "${DIM}  Supported formats: nmap XML, ARP table (arp -a), CSV, JSON, plain text${NC}"
    read -r -p "  > " filepath
    
    # Remove quotes if present (from drag & drop)
    filepath=$(echo "$filepath" | sed "s/^['\"]//;s/['\"]$//")
    
    # Expand ~ to home directory
    filepath="${filepath/#\~/$HOME}"
    
    if [ ! -f "$filepath" ]; then
        print_error "File not found: $filepath"
        press_enter
        return 1
    fi
    
    INPUT_FILE="$filepath"
    print_progress "Detecting file format..."
    
    # Auto-detect file format
    FILE_FORMAT=$(detect_file_format "$filepath")
    print_success "Detected format: ${CYAN}$FILE_FORMAT${NC}"
    print_progress "Parsing file..."
    
    case "$FILE_FORMAT" in
        "nmap-xml")
            parse_xml_file
            ;;
        "arp-table")
            parse_arp_file
            ;;
        "plain-text")
            parse_plain_text_file
            ;;
        "csv")
            parse_csv_file
            ;;
        "json")
            parse_json_file
            ;;
        *)
            print_error "Unknown file format"
            log_input "FAILED - Unknown format: $filepath"
            INPUT_FILE=""
            FILE_FORMAT=""
            press_enter
            return 1
            ;;
    esac
    
    local count=$(wc -l < "$TEMP_FILE" | tr -d ' ')
    log_input "Loaded file: $filepath (format: $FILE_FORMAT, devices: $count)"
    print_success "Loaded ${count} devices successfully!"
    press_enter
}

# Load multiple files
load_multiple_files() {
    echo ""
    echo -e "${CYAN}Enter file paths (one per line, empty line to finish):${NC}"
    echo -e "${DIM}  Or enter a directory path to load all supported files${NC}"
    echo ""
    
    local files=()
    local input=""
    
    while true; do
        read -r -p "  > " input
        [ -z "$input" ] && break
        
        # Remove quotes and expand ~
        input=$(echo "$input" | sed "s/^['\"]//;s/['\"]$//")
        input="${input/#\~/$HOME}"
        
        if [ -d "$input" ]; then
            # It's a directory - find all supported files
            print_progress "Scanning directory..."
            while IFS= read -r -d '' file; do
                files+=("$file")
                echo -e "  ${DIM}Found: $file${NC}"
            done < <(find "$input" -maxdepth 1 -type f \( -name "*.xml" -o -name "*.txt" -o -name "*.csv" -o -name "*.json" \) -print0 2>/dev/null)
        elif [ -f "$input" ]; then
            files+=("$input")
        else
            print_error "Not found: $input"
        fi
    done
    
    if [ ${#files[@]} -eq 0 ]; then
        print_error "No files to load"
        press_enter
        return 1
    fi
    
    echo ""
    print_progress "Loading ${#files[@]} file(s)..."
    
    # Clear temp file
    > "$TEMP_FILE"
    
    local total_devices=0
    local loaded_files=0
    
    for file in "${files[@]}"; do
        local format=$(detect_file_format "$file")
        echo -e "  ${DIM}Processing: $file ($format)${NC}"
        
        local temp_single=$(mktemp)
        
        # Temporarily change INPUT_FILE for parsing
        local orig_input="$INPUT_FILE"
        INPUT_FILE="$file"
        
        case "$format" in
            "nmap-xml")
                parse_xml_file_to "$temp_single"
                ;;
            "arp-table")
                parse_arp_file_to "$temp_single"
                ;;
            "plain-text")
                parse_plain_text_file_to "$temp_single"
                ;;
            "csv")
                parse_csv_file_to "$temp_single"
                ;;
            "json")
                parse_json_file_to "$temp_single"
                ;;
        esac
        
        INPUT_FILE="$orig_input"
        
        if [ -s "$temp_single" ]; then
            cat "$temp_single" >> "$TEMP_FILE"
            local count=$(wc -l < "$temp_single" | tr -d ' ')
            total_devices=$((total_devices + count))
            ((loaded_files++))
            log_input "Loaded file: $file (format: $format, devices: $count)"
        fi
        
        rm -f "$temp_single"
    done
    
    # Remove duplicates based on IP address
    sort -t'|' -k1,1 -u "$TEMP_FILE" -o "$TEMP_FILE"
    
    INPUT_FILE="[${loaded_files} files]"
    FILE_FORMAT="multiple"
    
    local final_count=$(wc -l < "$TEMP_FILE" | tr -d ' ')
    log_info "Multiple files loaded: $loaded_files files, $final_count unique devices"
    print_success "Loaded $final_count unique devices from $loaded_files file(s)"
    press_enter
}

# Load example files
load_examples() {
    local example_dir="$SCRIPT_DIR/example"
    
    echo ""
    print_header "Example Files"
    
    if [ ! -d "$example_dir" ]; then
        print_error "Example directory not found: $example_dir"
        press_enter
        return 1
    fi
    
    # List available examples
    local examples=()
    local i=1
    
    echo -e "  ${BOLD}Available example files:${NC}"
    echo ""
    
    for file in "$example_dir"/*; do
        if [ -f "$file" ]; then
            local basename=$(basename "$file")
            local format=$(detect_file_format "$file")
            local size=$(wc -l < "$file" | tr -d ' ')
            examples+=("$file")
            echo -e "  ${GREEN}$i)${NC} $basename ${DIM}($format, $size lines)${NC}"
            ((i++))
        fi
    done
    
    echo ""
    echo -e "  ${GREEN}a)${NC} Load all examples"
    echo -e "  ${GREEN}0)${NC} Cancel"
    echo ""
    
    echo -e "${CYAN}  Select example to load:${NC}"
    read -r -p "  > " choice
    
    if [[ "$choice" == "0" ]]; then
        return 0
    fi
    
    if [[ "$choice" == "a" || "$choice" == "A" ]]; then
        # Load all examples
        > "$TEMP_FILE"
        local total=0
        
        for file in "${examples[@]}"; do
            local format=$(detect_file_format "$file")
            local temp_single=$(mktemp)
            
            INPUT_FILE="$file"
            
            case "$format" in
                "nmap-xml") parse_xml_file_to "$temp_single" ;;
                "arp-table") parse_arp_file_to "$temp_single" ;;
                "plain-text") parse_plain_text_file_to "$temp_single" ;;
                "csv") parse_csv_file_to "$temp_single" ;;
                "json") parse_json_file_to "$temp_single" ;;
            esac
            
            if [ -s "$temp_single" ]; then
                cat "$temp_single" >> "$TEMP_FILE"
                local count=$(wc -l < "$temp_single" | tr -d ' ')
                total=$((total + count))
                print_success "Loaded $(basename "$file") ($count devices)"
            fi
            
            rm -f "$temp_single"
        done
        
        sort -t'|' -k1,1 -u "$TEMP_FILE" -o "$TEMP_FILE"
        local final=$(wc -l < "$TEMP_FILE" | tr -d ' ')
        
        INPUT_FILE="[examples]"
        FILE_FORMAT="multiple"
        
        log_input "Loaded all examples: $final unique devices"
        echo ""
        print_success "Loaded $final unique devices from ${#examples[@]} example files"
        press_enter
        return 0
    fi
    
    # Load single example
    if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le "${#examples[@]}" ]; then
        local selected="${examples[$((choice-1))]}"
        INPUT_FILE="$selected"
        FILE_FORMAT=$(detect_file_format "$selected")
        
        print_progress "Loading $(basename "$selected")..."
        
        case "$FILE_FORMAT" in
            "nmap-xml") parse_xml_file ;;
            "arp-table") parse_arp_file ;;
            "plain-text") parse_plain_text_file ;;
            "csv") parse_csv_file ;;
            "json") parse_json_file ;;
        esac
        
        local count=$(wc -l < "$TEMP_FILE" | tr -d ' ')
        log_input "Loaded example: $selected ($count devices)"
        print_success "Loaded $count devices from $(basename "$selected")"
        press_enter
    else
        print_error "Invalid selection"
        press_enter
    fi
}

