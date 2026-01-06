#!/bin/bash
# ============================================================================
# NetScan Installation Script
# ============================================================================
# Installs NetScan and its dependencies
# Usage: ./install.sh [--uninstall] [--local] [--check]
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Installation paths
SCRIPT_NAME="netscan"
INSTALL_DIR="/usr/local/bin"
LOCAL_INSTALL_DIR="$HOME/.local/bin"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ============================================================================
# Helper Functions
# ============================================================================

print_banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                   NetScan Installation Script                     ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "${BLUE}==>${NC} ${BOLD}$1${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}!${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "  $1"
}

# Check if command exists
has_command() {
    command -v "$1" &>/dev/null
}

# ============================================================================
# Dependency Checks
# ============================================================================

check_dependencies() {
    print_step "Checking dependencies..."
    echo ""
    
    local all_good=true
    local warnings=()
    
    # Required: bash 4+ (warning only, still works with 3.2)
    local bash_version="${BASH_VERSION%%.*}"
    if [[ "$bash_version" -ge 4 ]]; then
        print_success "Bash $BASH_VERSION (4.0+ required)"
    else
        print_warning "Bash $BASH_VERSION (4.0+ recommended for all features)"
        warnings+=("Consider upgrading bash: brew install bash")
        # Don't fail - most features still work
    fi
    
    # Required: curl
    if has_command curl; then
        local curl_version=$(curl --version | head -1 | awk '{print $2}')
        print_success "curl $curl_version"
    else
        print_error "curl not found (required for vendor lookups)"
        warnings+=("Install curl: brew install curl")
        all_good=false
    fi
    
    # Optional: Python 3.6+
    if has_command python3; then
        local py_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:3])))" 2>/dev/null)
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 6) else 1)" 2>/dev/null; then
            print_success "Python $py_version (enables caching & fast parsing)"
        else
            print_warning "Python $py_version (3.6+ recommended)"
            warnings+=("Upgrade Python for better performance: brew install python3")
        fi
    else
        print_warning "Python 3 not found (optional, enables caching)"
        warnings+=("Install Python 3 for better performance: brew install python3")
    fi
    
    # Optional: jq
    if has_command jq; then
        local jq_version=$(jq --version 2>/dev/null | tr -d 'jq-')
        print_success "jq $jq_version (enhanced JSON parsing)"
    else
        print_warning "jq not found (optional, for better JSON parsing)"
        warnings+=("Install jq for better JSON support: brew install jq")
    fi
    
    # Optional: xmllint
    if has_command xmllint; then
        print_success "xmllint (enhanced XML parsing)"
    else
        print_warning "xmllint not found (optional, for better XML parsing)"
    fi
    
    # Optional: nmap
    if has_command nmap; then
        local nmap_version=$(nmap --version | head -1 | awk '{print $3}')
        print_success "nmap $nmap_version (network scanning)"
    else
        print_warning "nmap not found (optional, for network scanning)"
        warnings+=("Install nmap for scanning: brew install nmap")
    fi
    
    echo ""
    
    # Print warnings
    if [[ ${#warnings[@]} -gt 0 ]]; then
        print_step "Recommendations:"
        for warning in "${warnings[@]}"; do
            print_info "$warning"
        done
        echo ""
    fi
    
    $all_good
}

# ============================================================================
# Python Package Installation
# ============================================================================

install_python_packages() {
    print_step "Setting up Python helpers..."
    
    # Check if Python 3 is available
    if ! has_command python3; then
        print_warning "Python 3 not found, skipping Python package installation"
        return 1
    fi
    
    # Check if pip is available
    local pip_cmd=""
    if has_command pip3; then
        pip_cmd="pip3"
    elif python3 -m pip --version &>/dev/null; then
        pip_cmd="python3 -m pip"
    else
        print_warning "pip not found, skipping Python package installation"
        print_info "Install pip: curl https://bootstrap.pypa.io/get-pip.py | python3"
        return 1
    fi
    
    # Required packages for helpers
    local packages=(
        "requests"      # HTTP requests for API calls
    )
    
    # Optional packages for advanced features
    local optional_packages=(
        "reportlab"     # PDF generation (for report_generator.py)
        "matplotlib"    # Charts and graphs (for report_generator.py)
    )
    
    echo ""
    print_info "Checking required Python packages..."
    
    local needs_install=()
    
    for pkg in "${packages[@]}"; do
        if python3 -c "import $pkg" 2>/dev/null; then
            print_success "$pkg installed"
        else
            print_warning "$pkg not found"
            needs_install+=("$pkg")
        fi
    done
    
    # Install missing required packages
    if [[ ${#needs_install[@]} -gt 0 ]]; then
        echo ""
        print_info "Installing missing packages: ${needs_install[*]}"
        
        # Try user install first (no sudo needed)
        if $pip_cmd install --user "${needs_install[@]}" 2>/dev/null; then
            print_success "Installed Python packages successfully"
        else
            # Try with --break-system-packages for newer systems
            if $pip_cmd install --user --break-system-packages "${needs_install[@]}" 2>/dev/null; then
                print_success "Installed Python packages successfully"
            else
                print_warning "Could not install Python packages automatically"
                print_info "Try manually: $pip_cmd install --user ${needs_install[*]}"
            fi
        fi
    fi
    
    # Check optional packages
    echo ""
    print_info "Checking optional Python packages..."
    
    local optional_missing=()
    for pkg in "${optional_packages[@]}"; do
        if python3 -c "import $pkg" 2>/dev/null; then
            print_success "$pkg installed"
        else
            print_warning "$pkg not found (optional: enables PDF reports/charts)"
            optional_missing+=("$pkg")
        fi
    done
    
    if [[ ${#optional_missing[@]} -gt 0 ]]; then
        echo ""
        print_info "To enable PDF reports and charts, install:"
        print_info "  $pip_cmd install --user ${optional_missing[*]}"
    fi
    
    # Verify helpers work
    echo ""
    print_info "Verifying Python helpers..."
    
    local helper_dir="$SCRIPT_DIR/helpers"
    local helpers_ok=true
    local helpers_count=0
    local helpers_working=0
    
    # Core helpers
    local core_helpers=(
        "vendor_cache.py"
        "fast_parser.py"
        "mac_normalizer.py"
        "network_helper.py"
        "export_helper.py"
    )
    
    # Advanced helpers (new)
    local advanced_helpers=(
        "async_scanner.py"
        "monitor.py"
        "report_generator.py"
        "config_manager.py"
        "web_server.py"
    )
    
    echo ""
    print_info "Core helpers:"
    for helper in "${core_helpers[@]}"; do
        ((helpers_count++))
        if [[ -f "$helper_dir/$helper" ]]; then
            if python3 "$helper_dir/$helper" --help &>/dev/null; then
                print_success "$helper ready"
                ((helpers_working++))
            else
                print_warning "$helper has issues"
                helpers_ok=false
            fi
        else
            print_warning "$helper not found"
        fi
    done
    
    echo ""
    print_info "Advanced helpers:"
    for helper in "${advanced_helpers[@]}"; do
        ((helpers_count++))
        if [[ -f "$helper_dir/$helper" ]]; then
            if python3 "$helper_dir/$helper" --help &>/dev/null; then
                print_success "$helper ready"
                ((helpers_working++))
            else
                print_warning "$helper has issues (check dependencies)"
                helpers_ok=false
            fi
        else
            print_warning "$helper not found"
        fi
    done
    
    echo ""
    print_info "$helpers_working/$helpers_count Python helpers available"
    
    if $helpers_ok; then
        print_success "All Python helpers are ready"
    else
        print_warning "Some Python helpers may need additional dependencies"
        print_info "Most features will still work without optional packages"
    fi
    
    return 0
}

# ============================================================================
# Installation Functions
# ============================================================================

setup_directories() {
    print_step "Setting up directories..."
    
    local dirs=("exports" "logs" "cache" "example")
    
    for dir in "${dirs[@]}"; do
        if [[ ! -d "$SCRIPT_DIR/$dir" ]]; then
            mkdir -p "$SCRIPT_DIR/$dir"
            print_success "Created $dir/"
        else
            print_info "$dir/ exists"
        fi
    done
    
    echo ""
}

set_permissions() {
    print_step "Setting file permissions..."
    
    # Make main script executable
    chmod +x "$SCRIPT_DIR/netscan" 2>/dev/null && \
        print_success "netscan"
    
    # Make lib scripts executable
    for script in "$SCRIPT_DIR/lib"/*.sh; do
        if [[ -f "$script" ]]; then
            chmod +x "$script" 2>/dev/null && \
                print_success "lib/$(basename "$script")"
        fi
    done
    
    # Make helper scripts executable
    for script in "$SCRIPT_DIR/helpers"/*.py; do
        if [[ -f "$script" ]]; then
            chmod +x "$script" 2>/dev/null && \
                print_success "helpers/$(basename "$script")"
        fi
    done
    
    # Make install script executable
    chmod +x "$SCRIPT_DIR/install.sh" 2>/dev/null && \
        print_success "install.sh"
    
    echo ""
}

create_symlink() {
    local target_dir="$1"
    local link_path="$target_dir/$SCRIPT_NAME"
    local script_path="$SCRIPT_DIR/netscan"
    
    # Check if we need sudo
    local use_sudo=false
    if [[ ! -w "$target_dir" ]]; then
        use_sudo=true
    fi
    
    # Remove existing link/file
    if [[ -L "$link_path" ]] || [[ -f "$link_path" ]]; then
        if $use_sudo; then
            sudo rm -f "$link_path"
        else
            rm -f "$link_path"
        fi
    fi
    
    # Create symlink
    if $use_sudo; then
        sudo ln -s "$script_path" "$link_path"
    else
        ln -s "$script_path" "$link_path"
    fi
    
    print_success "Created symlink: $link_path -> $script_path"
}

install_global() {
    print_step "Installing globally to $INSTALL_DIR..."
    
    if [[ ! -d "$INSTALL_DIR" ]]; then
        print_error "$INSTALL_DIR does not exist"
        return 1
    fi
    
    create_symlink "$INSTALL_DIR"
    echo ""
}

install_local() {
    print_step "Installing locally to $LOCAL_INSTALL_DIR..."
    
    # Create local bin if it doesn't exist
    if [[ ! -d "$LOCAL_INSTALL_DIR" ]]; then
        mkdir -p "$LOCAL_INSTALL_DIR"
        print_success "Created $LOCAL_INSTALL_DIR"
    fi
    
    create_symlink "$LOCAL_INSTALL_DIR"
    
    # Check if local bin is in PATH
    if [[ ":$PATH:" != *":$LOCAL_INSTALL_DIR:"* ]]; then
        echo ""
        print_warning "$LOCAL_INSTALL_DIR is not in your PATH"
        print_info "Add this line to your ~/.zshrc or ~/.bashrc:"
        echo ""
        echo -e "    ${CYAN}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
        echo ""
    fi
    
    echo ""
}

# ============================================================================
# Uninstallation
# ============================================================================

uninstall() {
    print_step "Uninstalling NetScan..."
    echo ""
    
    # Remove global symlink
    if [[ -L "$INSTALL_DIR/$SCRIPT_NAME" ]]; then
        sudo rm -f "$INSTALL_DIR/$SCRIPT_NAME" && \
            print_success "Removed $INSTALL_DIR/$SCRIPT_NAME"
    fi
    
    # Remove local symlink
    if [[ -L "$LOCAL_INSTALL_DIR/$SCRIPT_NAME" ]]; then
        rm -f "$LOCAL_INSTALL_DIR/$SCRIPT_NAME" && \
            print_success "Removed $LOCAL_INSTALL_DIR/$SCRIPT_NAME"
    fi
    
    echo ""
    print_info "Note: Source files and data in $SCRIPT_DIR were not removed."
    print_info "To remove completely, delete the directory manually."
    echo ""
}

# ============================================================================
# Post-Install
# ============================================================================

print_post_install() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    Installation Complete!                         ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BOLD}Quick Start:${NC}"
    echo ""
    echo -e "  Run NetScan:        ${CYAN}netscan${NC}"
    echo -e "  From this folder:   ${CYAN}./netscan${NC}"
    echo ""
    echo -e "${BOLD}Usage Examples:${NC}"
    echo ""
    echo -e "  Load ARP table:     ${CYAN}arp -a > arp.txt && netscan${NC}"
    echo -e "  Load nmap scan:     ${CYAN}nmap -sn 192.168.1.0/24 -oX scan.xml${NC}"
    echo ""
    echo -e "${BOLD}Supported Formats:${NC}"
    echo ""
    echo -e "  • Nmap XML output     ${DIM}(nmap -oX)${NC}"
    echo -e "  • ARP table output    ${DIM}(arp -a)${NC}"
    echo -e "  • CSV files           ${DIM}(mac,ip,hostname)${NC}"
    echo -e "  • JSON files          ${DIM}(array of devices)${NC}"
    echo -e "  • Plain text          ${DIM}(one MAC per line)${NC}"
    echo ""
}

# ============================================================================
# Main
# ============================================================================

main() {
    print_banner
    
    # Parse arguments
    local do_uninstall=false
    local do_local=false
    local do_check=false
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --uninstall|-u)
                do_uninstall=true
                ;;
            --local|-l)
                do_local=true
                ;;
            --check|-c)
                do_check=true
                ;;
            --help|-h)
                echo "Usage: $0 [options]"
                echo ""
                echo "Options:"
                echo "  --check, -c      Check dependencies only"
                echo "  --local, -l      Install to ~/.local/bin instead of /usr/local/bin"
                echo "  --uninstall, -u  Remove NetScan installation"
                echo "  --help, -h       Show this help message"
                echo ""
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
        shift
    done
    
    # Handle uninstall
    if $do_uninstall; then
        uninstall
        exit 0
    fi
    
    # Check dependencies
    check_dependencies
    local deps_ok=$?
    
    # Check only mode
    if $do_check; then
        if [[ $deps_ok -eq 0 ]]; then
            print_success "All required dependencies are installed"
        else
            print_error "Some required dependencies are missing"
        fi
        exit $deps_ok
    fi
    
    # Continue with installation
    setup_directories
    set_permissions
    install_python_packages
    
    # Install
    if $do_local; then
        install_local
    else
        install_global || install_local
    fi
    
    print_post_install
}

main "$@"
