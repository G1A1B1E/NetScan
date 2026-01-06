#!/bin/bash
# ============================================================================
# Configuration and Global Variables
# ============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color
BOLD='\033[1m'
DIM='\033[2m'

# Global variables
INPUT_FILE=""
FILE_FORMAT=""
DEVICES_DATA=""

# Create temp file if not already set
if [ -z "$TEMP_FILE" ]; then
    TEMP_FILE=$(mktemp)
    trap "rm -f $TEMP_FILE" EXIT
fi

# Directory setup - get script directory
# This will be set by the main script before sourcing
if [ -z "$SCRIPT_DIR" ]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fi

# User data directory (writable) - use home directory
NETSCAN_DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/netscan"

# File directories (use user home for writable dirs)
FILES_DIR="$NETSCAN_DATA_DIR/files"
LOGS_DIR="$FILES_DIR/logs"
EXPORTS_DIR="$FILES_DIR/exports"
OUTPUT_DIR="$FILES_DIR/output"
CACHE_DIR="$NETSCAN_DATA_DIR/cache"

# Library and helpers stay with installation
LIB_DIR="$SCRIPT_DIR/lib"
HELPERS_DIR="$SCRIPT_DIR/helpers"

# Create directories if they don't exist
mkdir -p "$LOGS_DIR" "$EXPORTS_DIR" "$OUTPUT_DIR" "$CACHE_DIR"

# Log file with timestamp (will be initialized once per session)
if [ -z "$LOG_FILE" ]; then
    LOG_FILE="$LOGS_DIR/session_$(date +%Y%m%d_%H%M%S).log"
fi

# ============================================================================
# Python Helper Detection
# ============================================================================

# Check if Python 3 is available
HAS_PYTHON=false
PYTHON_CMD=""
if command -v python3 &>/dev/null; then
    HAS_PYTHON=true
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    # Check if it's Python 3
    if python -c "import sys; sys.exit(0 if sys.version_info[0] >= 3 else 1)" 2>/dev/null; then
        HAS_PYTHON=true
        PYTHON_CMD="python"
    fi
fi

# Python helper paths
VENDOR_CACHE_PY="$HELPERS_DIR/vendor_cache.py"
FAST_PARSER_PY="$HELPERS_DIR/fast_parser.py"
MAC_NORMALIZER_PY="$HELPERS_DIR/mac_normalizer.py"
NETWORK_HELPER_PY="$HELPERS_DIR/network_helper.py"
EXPORT_HELPER_PY="$HELPERS_DIR/export_helper.py"

# Check which helpers are available
HAS_VENDOR_CACHE=false
HAS_FAST_PARSER=false
HAS_MAC_NORMALIZER=false
HAS_NETWORK_HELPER=false
HAS_EXPORT_HELPER=false

if $HAS_PYTHON; then
    [[ -f "$VENDOR_CACHE_PY" ]] && $PYTHON_CMD "$VENDOR_CACHE_PY" --help &>/dev/null && HAS_VENDOR_CACHE=true
    [[ -f "$FAST_PARSER_PY" ]] && $PYTHON_CMD "$FAST_PARSER_PY" --help &>/dev/null && HAS_FAST_PARSER=true
    [[ -f "$MAC_NORMALIZER_PY" ]] && $PYTHON_CMD "$MAC_NORMALIZER_PY" --help &>/dev/null && HAS_MAC_NORMALIZER=true
    [[ -f "$NETWORK_HELPER_PY" ]] && $PYTHON_CMD "$NETWORK_HELPER_PY" --help &>/dev/null && HAS_NETWORK_HELPER=true
    [[ -f "$EXPORT_HELPER_PY" ]] && $PYTHON_CMD "$EXPORT_HELPER_PY" --help &>/dev/null && HAS_EXPORT_HELPER=true
fi

# Helper function to run Python helpers
run_python_helper() {
    local helper="$1"
    shift
    if $HAS_PYTHON && [[ -f "$helper" ]]; then
        $PYTHON_CMD "$helper" "$@"
        return $?
    else
        return 1
    fi
}
