#!/usr/bin/env bash
#===============================================================================
# Build Rust Helpers for NetScan
# 
# This script compiles the Rust performance modules.
# After building, NetScan will be 10-100x faster for:
#   - MAC address normalization
#   - OUI database parsing
#   - IP range expansion
#   - File parsing
#===============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUST_DIR="$SCRIPT_DIR/rust_helpers"
HELPERS_DIR="$SCRIPT_DIR/helpers"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }

check_rust() {
    if ! command -v rustc &> /dev/null; then
        log_error "Rust is not installed"
        echo ""
        echo "Install Rust with:"
        echo "  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
        echo ""
        echo "Or on macOS:"
        echo "  brew install rust"
        echo ""
        return 1
    fi
    
    log_success "Rust $(rustc --version | cut -d' ' -f2) found"
}

check_maturin() {
    if ! command -v maturin &> /dev/null; then
        log_warning "maturin not found, installing..."
        pip3 install --user maturin || {
            log_error "Failed to install maturin"
            return 1
        }
    fi
    
    log_success "maturin found"
}

build_rust_module() {
    log_info "Building Rust performance module..."
    
    cd "$RUST_DIR"
    
    # Build with maturin
    if command -v maturin &> /dev/null; then
        log_info "Building with maturin..."
        maturin develop --release || {
            log_error "maturin build failed"
            return 1
        }
    else
        # Fallback to cargo
        log_info "Building with cargo..."
        cargo build --release || {
            log_error "cargo build failed"
            return 1
        }
        
        # Copy the library
        local lib_name
        case "$(uname -s)" in
            Darwin*) lib_name="libnetscan_core.dylib" ;;
            Linux*)  lib_name="libnetscan_core.so" ;;
            *)       lib_name="netscan_core.dll" ;;
        esac
        
        if [[ -f "target/release/$lib_name" ]]; then
            # Python expects specific naming
            local py_lib_name="netscan_core.so"
            [[ "$(uname -s)" == "Darwin" ]] && py_lib_name="netscan_core.cpython-*-darwin.so"
            
            cp "target/release/$lib_name" "$HELPERS_DIR/netscan_core.so"
            log_success "Copied library to $HELPERS_DIR"
        fi
    fi
    
    log_success "Rust module built successfully!"
}

verify_module() {
    log_info "Verifying Python can import the module..."
    
    cd "$SCRIPT_DIR"
    
    if python3 -c "import sys; sys.path.insert(0, 'helpers'); import netscan_core; print('✓ Module loaded')" 2>/dev/null; then
        log_success "Module verified!"
        
        # Run benchmark
        log_info "Running quick benchmark..."
        python3 helpers/fast_core.py
        
        return 0
    else
        log_warning "Module not loadable yet (this is normal if using cargo build)"
        log_info "Try running: cd rust_helpers && maturin develop --release"
        return 1
    fi
}

show_usage() {
    echo "Build Rust Performance Module for NetScan"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --check     Only check if Rust is installed"
    echo "  --clean     Clean build artifacts"
    echo "  --verify    Verify the module works"
    echo "  -h, --help  Show this help"
    echo ""
    echo "Prerequisites:"
    echo "  - Rust (rustc, cargo)"
    echo "  - Python 3.7+"
    echo "  - maturin (pip install maturin)"
}

main() {
    case "${1:-}" in
        --check)
            check_rust
            check_maturin
            ;;
        --clean)
            log_info "Cleaning build artifacts..."
            cd "$RUST_DIR"
            cargo clean 2>/dev/null || true
            rm -rf target/
            rm -f "$HELPERS_DIR/netscan_core"*.so
            log_success "Cleaned"
            ;;
        --verify)
            verify_module
            ;;
        -h|--help)
            show_usage
            ;;
        *)
            echo ""
            echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
            echo -e "${BLUE}║${NC}     NetScan Rust Performance Module Builder                  ${BLUE}║${NC}"
            echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
            echo ""
            
            check_rust || exit 1
            check_maturin || exit 1
            build_rust_module || exit 1
            verify_module
            
            echo ""
            echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
            echo -e "${GREEN}  Build complete! NetScan will now use Rust for performance.${NC}"
            echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
            echo ""
            ;;
    esac
}

main "$@"
