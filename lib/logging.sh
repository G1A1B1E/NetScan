#!/bin/bash
# ============================================================================
# Logging Functions
# ============================================================================

log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

log_info() {
    log_message "INFO" "$1"
}

log_action() {
    log_message "ACTION" "$1"
}

log_input() {
    log_message "INPUT" "$1"
}

log_export() {
    log_message "EXPORT" "$1"
}

log_error() {
    log_message "ERROR" "$1"
}

log_debug() {
    if [ "${DEBUG:-0}" = "1" ]; then
        log_message "DEBUG" "$1"
    fi
}
