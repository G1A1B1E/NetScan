#!/bin/bash
# ============================================================================
# Error Handling Module
# ============================================================================
# Provides error codes, trap handlers, and graceful degradation
# ============================================================================

# Error codes
readonly E_SUCCESS=0
readonly E_GENERAL=1
readonly E_INVALID_ARG=2
readonly E_FILE_NOT_FOUND=3
readonly E_PERMISSION_DENIED=4
readonly E_DEPENDENCY_MISSING=5
readonly E_NETWORK_ERROR=6
readonly E_PARSE_ERROR=7
readonly E_INVALID_FORMAT=8
readonly E_CACHE_ERROR=9
readonly E_USER_ABORT=130

# Error messages (bash 3.2 compatible - no associative arrays)
get_error_message() {
    case "$1" in
        0) echo "Success" ;;
        1) echo "General error" ;;
        2) echo "Invalid argument" ;;
        3) echo "File not found" ;;
        4) echo "Permission denied" ;;
        5) echo "Required dependency missing" ;;
        6) echo "Network error" ;;
        7) echo "Parse error" ;;
        8) echo "Invalid file format" ;;
        9) echo "Cache error" ;;
        130) echo "User abort" ;;
        *) echo "Unknown error" ;;
    esac
}

# Global error state
LAST_ERROR=""
LAST_ERROR_CODE=0

# ============================================================================
# Error Functions
# ============================================================================

# Set error state
set_error() {
    local code="${1:-$E_GENERAL}"
    local message="${2:-$(get_error_message $code)}"
    LAST_ERROR_CODE=$code
    LAST_ERROR="$message"
    log_error "[$code] $message"
}

# Get last error message
get_error() {
    echo "$LAST_ERROR"
}

# Get last error code
get_error_code() {
    echo "$LAST_ERROR_CODE"
}

# Clear error state
clear_error() {
    LAST_ERROR=""
    LAST_ERROR_CODE=0
}

# Check if last operation had error
has_error() {
    [[ $LAST_ERROR_CODE -ne 0 ]]
}

# Die with error message
die() {
    local code="${1:-$E_GENERAL}"
    local message="${2:-$(get_error_message $code)}"
    echo -e "${RED}Fatal Error: $message${NC}" >&2
    log_error "FATAL: [$code] $message"
    exit "$code"
}

# ============================================================================
# Validation Functions
# ============================================================================

# Validate file exists and is readable
validate_file() {
    local filepath="$1"
    
    if [[ -z "$filepath" ]]; then
        set_error $E_INVALID_ARG "No file path provided"
        return $E_INVALID_ARG
    fi
    
    if [[ ! -e "$filepath" ]]; then
        set_error $E_FILE_NOT_FOUND "File not found: $filepath"
        return $E_FILE_NOT_FOUND
    fi
    
    if [[ ! -r "$filepath" ]]; then
        set_error $E_PERMISSION_DENIED "Cannot read file: $filepath"
        return $E_PERMISSION_DENIED
    fi
    
    if [[ ! -s "$filepath" ]]; then
        set_error $E_INVALID_ARG "File is empty: $filepath"
        return $E_INVALID_ARG
    fi
    
    clear_error
    return $E_SUCCESS
}

# Validate directory exists and is writable
validate_directory() {
    local dirpath="$1"
    local create="${2:-false}"
    
    if [[ -z "$dirpath" ]]; then
        set_error $E_INVALID_ARG "No directory path provided"
        return $E_INVALID_ARG
    fi
    
    if [[ ! -d "$dirpath" ]]; then
        if [[ "$create" == "true" ]]; then
            mkdir -p "$dirpath" 2>/dev/null || {
                set_error $E_PERMISSION_DENIED "Cannot create directory: $dirpath"
                return $E_PERMISSION_DENIED
            }
        else
            set_error $E_FILE_NOT_FOUND "Directory not found: $dirpath"
            return $E_FILE_NOT_FOUND
        fi
    fi
    
    if [[ ! -w "$dirpath" ]]; then
        set_error $E_PERMISSION_DENIED "Cannot write to directory: $dirpath"
        return $E_PERMISSION_DENIED
    fi
    
    clear_error
    return $E_SUCCESS
}

# Validate MAC address format
validate_mac() {
    local mac="$1"
    
    if [[ -z "$mac" ]]; then
        return 1
    fi
    
    # Normalize and check format
    local normalized=$(echo "$mac" | tr '[:lower:]' '[:upper:]' | tr -d ':-.')
    
    if [[ ${#normalized} -ge 6 ]] && [[ "$normalized" =~ ^[0-9A-F]+$ ]]; then
        return 0
    fi
    
    return 1
}

# Validate IP address format
validate_ip() {
    local ip="$1"
    
    if [[ "$ip" =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        return 0
    fi
    
    return 1
}

# ============================================================================
# Dependency Checking
# ============================================================================

# Check for required command
require_command() {
    local cmd="$1"
    local package="${2:-$cmd}"
    
    if ! command -v "$cmd" &>/dev/null; then
        set_error $E_DEPENDENCY_MISSING "Required command not found: $cmd (install $package)"
        return $E_DEPENDENCY_MISSING
    fi
    
    return $E_SUCCESS
}

# Check for optional command (with fallback info)
check_command() {
    local cmd="$1"
    command -v "$cmd" &>/dev/null
}

# Check Python availability and version
check_python() {
    local min_version="${1:-3.6}"
    
    if check_command python3; then
        local version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))" 2>/dev/null)
        if [[ -n "$version" ]]; then
            # Simple version comparison
            if python3 -c "import sys; exit(0 if sys.version_info >= (3, 6) else 1)" 2>/dev/null; then
                return 0
            fi
        fi
    fi
    return 1
}

# ============================================================================
# Trap Handlers
# ============================================================================

# Cleanup function called on exit
cleanup() {
    local exit_code=$?
    
    # Remove temp files
    [[ -n "$TEMP_FILE" && -f "$TEMP_FILE" ]] && rm -f "$TEMP_FILE"
    
    # Log session end if not already logged
    if [[ $exit_code -ne $E_USER_ABORT ]]; then
        log_info "Session ended (exit code: $exit_code)"
    fi
    
    exit $exit_code
}

# Handle SIGINT (Ctrl+C)
handle_interrupt() {
    echo ""
    log_info "Session interrupted by user"
    echo -e "\n${YELLOW}Interrupted. Cleaning up...${NC}"
    exit $E_USER_ABORT
}

# Handle SIGTERM
handle_terminate() {
    log_info "Session terminated"
    echo -e "\n${YELLOW}Terminated. Cleaning up...${NC}"
    exit $E_USER_ABORT
}

# Handle errors (for set -e mode)
handle_error() {
    local exit_code=$?
    local line_no=$1
    log_error "Error on line $line_no (exit code: $exit_code)"
    echo -e "${RED}Error occurred on line $line_no${NC}" >&2
}

# Setup all trap handlers
setup_error_handlers() {
    trap cleanup EXIT
    trap handle_interrupt INT
    trap handle_terminate TERM
    # Uncomment for strict mode:
    # trap 'handle_error $LINENO' ERR
}

# ============================================================================
# Safe Operations
# ============================================================================

# Safe file read with error handling
safe_read_file() {
    local filepath="$1"
    
    validate_file "$filepath" || return $?
    
    cat "$filepath" 2>/dev/null || {
        set_error $E_GENERAL "Failed to read file: $filepath"
        return $E_GENERAL
    }
}

# Safe command execution with timeout
safe_exec() {
    local timeout="${1:-10}"
    shift
    local cmd=("$@")
    
    if check_command timeout; then
        timeout "$timeout" "${cmd[@]}"
    else
        "${cmd[@]}"
    fi
}

# Safe network request with retry
safe_curl() {
    local url="$1"
    local max_retries="${2:-3}"
    local timeout="${3:-5}"
    local retry=0
    
    while [[ $retry -lt $max_retries ]]; do
        local response
        response=$(curl -s --max-time "$timeout" "$url" 2>/dev/null)
        local exit_code=$?
        
        if [[ $exit_code -eq 0 && -n "$response" ]]; then
            echo "$response"
            return 0
        fi
        
        ((retry++))
        [[ $retry -lt $max_retries ]] && sleep 1
    done
    
    set_error $E_NETWORK_ERROR "Failed to fetch URL: $url"
    return $E_NETWORK_ERROR
}

# ============================================================================
# Graceful Degradation
# ============================================================================

# Check if Python helpers are available
has_python_helpers() {
    if ! check_python; then
        return 1
    fi
    
    local helpers_dir="$SCRIPT_DIR/helpers"
    [[ -f "$helpers_dir/vendor_cache.py" && -f "$helpers_dir/fast_parser.py" ]]
}

# Get feature availability status
get_capabilities() {
    local caps=()
    
    check_command curl && caps+=("vendor_lookup")
    check_command jq && caps+=("json_parsing")
    check_python && caps+=("python_helpers")
    has_python_helpers && caps+=("fast_parsing" "vendor_cache")
    check_command nmap && caps+=("network_scan")
    
    echo "${caps[*]}"
}

# Print capabilities status
print_capabilities() {
    echo -e "${BOLD}System Capabilities:${NC}"
    echo ""
    
    local features=(
        "curl:vendor_lookup:MAC vendor lookups"
        "jq:json_parsing:Enhanced JSON parsing"
        "python3:python_helpers:Python acceleration"
        "nmap:network_scan:Network scanning"
    )
    
    for feature in "${features[@]}"; do
        IFS=':' read -r cmd cap desc <<< "$feature"
        if check_command "$cmd"; then
            echo -e "  ${GREEN}✓${NC} $desc ($cmd)"
        else
            echo -e "  ${DIM}○${NC} $desc (install $cmd)"
        fi
    done
    
    echo ""
    
    if has_python_helpers; then
        echo -e "  ${GREEN}✓${NC} Fast parsing enabled"
        echo -e "  ${GREEN}✓${NC} Vendor caching enabled"
    else
        echo -e "  ${DIM}○${NC} Fast parsing (run install.sh)"
        echo -e "  ${DIM}○${NC} Vendor caching (run install.sh)"
    fi
}
