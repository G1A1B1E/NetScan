#!/usr/bin/env bash
#===============================================================================
# NetScan Installer v2.0
# https://github.com/G1A1B1E/NetScan
#
# One-command installation:
# curl -fsSL https://raw.githubusercontent.com/G1A1B1E/NetScan/main/install.sh | bash
#===============================================================================

set -e

REPO_URL="https://github.com/G1A1B1E/NetScan.git"
REPO_NAME="NetScan"
DEFAULT_INSTALL_DIR="$HOME/.netscan"
GLOBAL_BIN_DIR="/usr/local/bin"
LOCAL_BIN_DIR="$HOME/.local/bin"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m'

INSTALL_MODE="global"
SKIP_DEPS=false
UNINSTALL=false
UPDATE=false
VERBOSE=false
FORCE=false

print_banner() {
    echo -e "${CYAN}"
    cat << 'BANNER'
   ███╗   ██╗███████╗████████╗███████╗ ██████╗ █████╗ ███╗   ██╗
   ████╗  ██║██╔════╝╚══██╔══╝██╔════╝██╔════╝██╔══██╗████╗  ██║
   ██╔██╗ ██║█████╗     ██║   ███████╗██║     ███████║██╔██╗ ██║
   ██║╚██╗██║██╔══╝     ██║   ╚════██║██║     ██╔══██║██║╚██╗██║
   ██║ ╚████║███████╗   ██║   ███████║╚██████╗██║  ██║██║ ╚████║
   ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝
BANNER
    echo -e "${NC}"
    echo -e "${BOLD}   Network Scanner & MAC Vendor Lookup Tool${NC}"
    echo -e "${BLUE}   https://github.com/G1A1B1E/NetScan${NC}"
    echo ""
}

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }
log_step() { echo -e "${MAGENTA}[→]${NC} $1"; }

command_exists() { command -v "$1" &> /dev/null; }

get_os() {
    case "$(uname -s)" in
        Darwin*) echo "macos" ;;
        Linux*)  echo "linux" ;;
        *) echo "unknown" ;;
    esac
}

get_shell_rc() {
    local shell_name
    shell_name=$(basename "$SHELL")
    case "$shell_name" in
        zsh)  echo "$HOME/.zshrc" ;;
        bash) [[ -f "$HOME/.bash_profile" ]] && echo "$HOME/.bash_profile" || echo "$HOME/.bashrc" ;;
        fish) echo "$HOME/.config/fish/config.fish" ;;
        *)    echo "$HOME/.profile" ;;
    esac
}

require_sudo() {
    if [[ $EUID -ne 0 ]]; then
        if ! sudo -v 2>/dev/null; then
            log_error "This operation requires sudo privileges"
            return 1
        fi
    fi
}

detect_package_manager() {
    if command_exists brew; then echo "brew"
    elif command_exists apt-get; then echo "apt"
    elif command_exists dnf; then echo "dnf"
    elif command_exists yum; then echo "yum"
    elif command_exists pacman; then echo "pacman"
    else echo "unknown"
    fi
}

install_package() {
    local package="$1"
    local pm
    pm=$(detect_package_manager)
    case "$pm" in
        brew)   brew install "$package" ;;
        apt)    sudo apt-get install -y "$package" ;;
        dnf)    sudo dnf install -y "$package" ;;
        yum)    sudo yum install -y "$package" ;;
        pacman) sudo pacman -S --noconfirm "$package" ;;
        *)      return 1 ;;
    esac
}

check_and_install_deps() {
    local os pm
    os=$(get_os)
    pm=$(detect_package_manager)
    
    log_step "Checking system dependencies..."
    
    local deps_needed=()
    
    command_exists git || deps_needed+=("git")
    
    if ! command_exists python3; then
        [[ "$pm" == "brew" ]] && deps_needed+=("python@3") || deps_needed+=("python3")
    fi
    
    if ! command_exists pip3 && ! python3 -m pip --version &>/dev/null; then
        [[ "$pm" == "apt" ]] && deps_needed+=("python3-pip")
    fi
    
    command_exists nmap || deps_needed+=("nmap")
    
    if [[ "$os" == "macos" ]]; then
        command_exists ggrep || deps_needed+=("grep")
        command_exists gsed || deps_needed+=("gnu-sed")
        command_exists gawk || deps_needed+=("gawk")
    fi
    
    if [[ ${#deps_needed[@]} -gt 0 ]]; then
        log_warning "Missing dependencies: ${deps_needed[*]}"
        
        if [[ "$pm" == "unknown" ]]; then
            log_error "No supported package manager found. Please install manually:"
            printf "  - %s\n" "${deps_needed[@]}"
            return 1
        fi
        
        log_step "Installing dependencies via $pm..."
        
        case "$pm" in
            apt)  sudo apt-get update -qq ;;
            brew) brew update --quiet 2>/dev/null || true ;;
        esac
        
        for dep in "${deps_needed[@]}"; do
            log_step "Installing $dep..."
            install_package "$dep" || log_warning "Failed to install $dep"
        done
    fi
    
    log_success "All system dependencies satisfied"
}

install_python_packages() {
    log_step "Installing Python packages..."
    
    local pip_cmd
    command_exists pip3 && pip_cmd="pip3" || pip_cmd="python3 -m pip"
    
    local packages=("requests" "netifaces")
    local optional=("reportlab" "matplotlib" "scapy" "python-nmap")
    
    for pkg in "${packages[@]}"; do
        if ! python3 -c "import ${pkg//-/_}" &>/dev/null 2>&1; then
            log_step "Installing $pkg..."
            $pip_cmd install --user "$pkg" &>/dev/null || log_warning "Failed to install $pkg"
        fi
    done
    
    log_step "Installing optional packages..."
    for pkg in "${optional[@]}"; do
        $pip_cmd install --user "$pkg" &>/dev/null 2>&1 || true
    done
    
    log_success "Python packages installed"
}

clone_or_update_repo() {
    local install_dir="$1"
    
    if [[ -d "$install_dir/.git" ]]; then
        log_step "Updating existing installation..."
        cd "$install_dir"
        git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || log_warning "Could not update"
    elif [[ -d "$install_dir" ]]; then
        if $FORCE; then
            log_warning "Removing existing directory..."
            rm -rf "$install_dir"
            log_step "Cloning NetScan repository..."
            git clone "$REPO_URL" "$install_dir"
        else
            log_error "Directory $install_dir already exists. Use --force to overwrite."
            return 1
        fi
    else
        log_step "Cloning NetScan repository..."
        git clone "$REPO_URL" "$install_dir"
    fi
    
    cd "$install_dir"
    log_success "Repository ready at $install_dir"
}

setup_directories() {
    local install_dir="$1"
    log_step "Setting up directories..."
    mkdir -p "$install_dir"/{cache,logs,exports,reports,files,data}
    log_success "Directories created"
}

set_permissions() {
    local install_dir="$1"
    log_step "Setting file permissions..."
    chmod +x "$install_dir/netscan" 2>/dev/null || true
    [[ -d "$install_dir/lib" ]] && find "$install_dir/lib" -name "*.sh" -exec chmod +x {} \;
    [[ -d "$install_dir/helpers" ]] && find "$install_dir/helpers" -name "*.py" -exec chmod +x {} \;
    log_success "Permissions set"
}

install_global() {
    local install_dir="$1"
    log_step "Installing globally (requires sudo)..."
    require_sudo || return 1
    
    local target="$GLOBAL_BIN_DIR/netscan"
    sudo rm -f "$target" 2>/dev/null
    
    sudo tee "$target" > /dev/null << EOF
#!/usr/bin/env bash
NETSCAN_HOME="$install_dir"
export NETSCAN_HOME
cd "\$NETSCAN_HOME" 2>/dev/null || true
exec "\$NETSCAN_HOME/netscan" "\$@"
EOF
    
    sudo chmod +x "$target"
    log_success "Installed to $target"
}

install_local() {
    local install_dir="$1"
    log_step "Installing for current user..."
    mkdir -p "$LOCAL_BIN_DIR"
    
    local target="$LOCAL_BIN_DIR/netscan"
    rm -f "$target" 2>/dev/null
    
    cat > "$target" << EOF
#!/usr/bin/env bash
NETSCAN_HOME="$install_dir"
export NETSCAN_HOME
cd "\$NETSCAN_HOME" 2>/dev/null || true
exec "\$NETSCAN_HOME/netscan" "\$@"
EOF
    
    chmod +x "$target"
    
    local shell_rc
    shell_rc=$(get_shell_rc)
    
    if ! echo "$PATH" | grep -q "$LOCAL_BIN_DIR"; then
        if ! grep -q ".local/bin" "$shell_rc" 2>/dev/null; then
            echo "" >> "$shell_rc"
            echo "# Added by NetScan installer" >> "$shell_rc"
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$shell_rc"
            log_info "Added PATH to $shell_rc"
            log_warning "Run 'source $shell_rc' or restart your terminal"
        fi
    fi
    
    log_success "Installed to $target"
}

verify_installation() {
    local install_dir="$1"
    log_step "Verifying installation..."
    
    local errors=0
    
    [[ ! -x "$install_dir/netscan" ]] && { log_error "Main script not executable"; ((errors++)); }
    
    for helper in vendor_cache.py fast_parser.py mac_normalizer.py network_helper.py export_helper.py async_scanner.py monitor.py report_generator.py config_manager.py web_server.py; do
        [[ ! -f "$install_dir/helpers/$helper" ]] && log_warning "Helper not found: $helper"
    done
    
    for lib in config.sh utils.sh lookup.sh scanner.sh; do
        [[ ! -f "$install_dir/lib/$lib" ]] && log_warning "Library not found: $lib"
    done
    
    python3 --version &>/dev/null || { log_error "Python 3 not working"; ((errors++)); }
    
    if python3 "$install_dir/helpers/mac_normalizer.py" "00:11:22:33:44:55" &>/dev/null; then
        log_success "Python helpers working"
    else
        log_warning "Python helper test failed (may still work)"
    fi
    
    [[ $errors -eq 0 ]] && log_success "Installation verified!" || log_error "Installation has $errors error(s)"
}

uninstall_netscan() {
    log_step "Uninstalling NetScan..."
    
    [[ -f "$GLOBAL_BIN_DIR/netscan" ]] && { require_sudo && sudo rm -f "$GLOBAL_BIN_DIR/netscan"; }
    [[ -f "$LOCAL_BIN_DIR/netscan" ]] && rm -f "$LOCAL_BIN_DIR/netscan"
    
    if [[ -d "$DEFAULT_INSTALL_DIR" ]]; then
        read -p "Remove installation directory $DEFAULT_INSTALL_DIR? [y/N] " -n 1 -r
        echo
        [[ $REPLY =~ ^[Yy]$ ]] && rm -rf "$DEFAULT_INSTALL_DIR" && log_success "Removed $DEFAULT_INSTALL_DIR"
    fi
    
    log_success "NetScan uninstalled"
}

print_post_install() {
    local install_dir="$1"
    local install_mode="$2"
    
    echo ""
    echo -e "${GREEN}══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}           NetScan installed successfully!${NC}"
    echo -e "${GREEN}══════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${BOLD}Installation Details:${NC}"
    echo -e "  Location: ${CYAN}$install_dir${NC}"
    echo -e "  Mode: ${CYAN}$install_mode${NC}"
    echo ""
    echo -e "${BOLD}Quick Start:${NC}"
    echo -e "  ${YELLOW}netscan${NC}                       # Launch interactive menu"
    echo -e "  ${YELLOW}netscan -l 00:11:22:33:44:55${NC}  # Lookup MAC vendor"
    echo -e "  ${YELLOW}netscan -s${NC}                    # Scan network"
    echo -e "  ${YELLOW}netscan -w${NC}                    # Start web interface"
    echo -e "  ${YELLOW}netscan --help${NC}                # Show all options"
    echo ""
    echo -e "${BOLD}Documentation:${NC}"
    echo -e "  README: ${CYAN}$install_dir/README.md${NC}"
    echo -e "  GitHub: ${CYAN}https://github.com/G1A1B1E/NetScan${NC}"
    echo ""
}

show_usage() {
    cat << 'USAGE'
NetScan Installer

Usage: ./install.sh [OPTIONS]

Installation Options:
  --global        Install system-wide to /usr/local/bin (default, requires sudo)
  --local         Install for current user only (~/.local/bin)
  --portable      Just clone the repo, don't create symlinks
  --dir PATH      Custom installation directory (default: ~/.netscan)

Other Options:
  --update        Update existing installation
  --uninstall     Remove NetScan installation
  --skip-deps     Skip dependency installation
  --force         Force overwrite existing installation
  --verbose       Show detailed output
  -h, --help      Show this help message

Examples:
  # One-line install (global):
  curl -fsSL https://raw.githubusercontent.com/G1A1B1E/NetScan/main/install.sh | bash

  # Install for current user only:
  bash <(curl -fsSL https://raw.githubusercontent.com/G1A1B1E/NetScan/main/install.sh) --local

  # Custom directory:
  ./install.sh --dir ~/tools/netscan --local

USAGE
}

main() {
    local install_dir="$DEFAULT_INSTALL_DIR"
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --global)     INSTALL_MODE="global"; shift ;;
            --local)      INSTALL_MODE="local"; shift ;;
            --portable)   INSTALL_MODE="portable"; shift ;;
            --dir)        install_dir="$2"; shift 2 ;;
            --update)     UPDATE=true; shift ;;
            --uninstall)  UNINSTALL=true; shift ;;
            --skip-deps)  SKIP_DEPS=true; shift ;;
            --force)      FORCE=true; shift ;;
            --verbose)    VERBOSE=true; shift ;;
            -h|--help)    show_usage; exit 0 ;;
            *)            log_error "Unknown option: $1"; show_usage; exit 1 ;;
        esac
    done
    
    print_banner
    
    if $UNINSTALL; then
        uninstall_netscan
        exit 0
    fi
    
    local running_from_repo=false
    if [[ -f "./netscan" && -d "./lib" && -d "./helpers" ]]; then
        running_from_repo=true
        install_dir="$(pwd)"
        log_info "Running from within NetScan repository"
    fi
    
    echo -e "${BOLD}Installation Configuration:${NC}"
    echo -e "  Mode: ${CYAN}$INSTALL_MODE${NC}"
    echo -e "  Directory: ${CYAN}$install_dir${NC}"
    echo ""
    
    if ! $SKIP_DEPS; then
        check_and_install_deps || { log_error "Failed to install dependencies"; exit 1; }
        install_python_packages
    fi
    
    if ! $running_from_repo; then
        clone_or_update_repo "$install_dir" || exit 1
    fi
    
    setup_directories "$install_dir"
    set_permissions "$install_dir"
    
    case "$INSTALL_MODE" in
        global)
            install_global "$install_dir" || {
                log_warning "Global install failed, falling back to local install"
                INSTALL_MODE="local"
                install_local "$install_dir"
            }
            ;;
        local)
            install_local "$install_dir"
            ;;
        portable)
            log_success "Portable installation complete"
            log_info "Run directly with: $install_dir/netscan"
            ;;
    esac
    
    verify_installation "$install_dir"
    print_post_install "$install_dir" "$INSTALL_MODE"
}

main "$@"
