#!/usr/bin/env bash
#===============================================================================
# NetScan Docker Helper Script
# 
# Easy commands to build, run, and manage NetScan in Docker
#===============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_NAME="netscan"
CONTAINER_NAME="netscan"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }

print_banner() {
    echo -e "${CYAN}"
    echo '   ███╗   ██╗███████╗████████╗███████╗ ██████╗ █████╗ ███╗   ██╗'
    echo '   ████╗  ██║██╔════╝╚══██╔══╝██╔════╝██╔════╝██╔══██╗████╗  ██║'
    echo '   ██╔██╗ ██║█████╗     ██║   ███████╗██║     ███████║██╔██╗ ██║'
    echo '   ██║╚██╗██║██╔══╝     ██║   ╚════██║██║     ██╔══██║██║╚██╗██║'
    echo '   ██║ ╚████║███████╗   ██║   ███████║╚██████╗██║  ██║██║ ╚████║'
    echo '   ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝'
    echo -e "${NC}"
    echo -e "${CYAN}   Docker Management Script${NC}"
    echo ""
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        echo ""
        echo "Install Docker:"
        echo "  macOS: brew install --cask docker"
        echo "  Linux: curl -fsSL https://get.docker.com | sh"
        echo "  Or visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        echo "Please start Docker and try again"
        exit 1
    fi
}

build_image() {
    log_info "Building NetScan Docker image..."
    cd "$SCRIPT_DIR"
    
    docker build \
        --tag "$IMAGE_NAME:latest" \
        --tag "$IMAGE_NAME:$(date +%Y%m%d)" \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        . || {
            log_error "Build failed"
            exit 1
        }
    
    log_success "Image built: $IMAGE_NAME:latest"
    docker images "$IMAGE_NAME"
}

build_slim() {
    log_info "Building slim NetScan image (no Rust)..."
    cd "$SCRIPT_DIR"
    
    # Create a slim Dockerfile without Rust build
    docker build \
        --tag "$IMAGE_NAME:slim" \
        --target runtime \
        . || {
            log_error "Slim build failed"
            exit 1
        }
    
    log_success "Slim image built: $IMAGE_NAME:slim"
}

run_interactive() {
    log_info "Starting NetScan interactive mode..."
    
    docker run -it --rm \
        --name "$CONTAINER_NAME-interactive" \
        --network host \
        --cap-add NET_RAW \
        --cap-add NET_ADMIN \
        -v netscan-cache:/app/cache \
        -v netscan-logs:/app/logs \
        -v netscan-exports:/app/exports \
        -v netscan-data:/app/data \
        "$IMAGE_NAME:latest" \
        "${@:---menu}"
}

run_scan() {
    local target="${1:-}"
    
    if [[ -z "$target" ]]; then
        log_error "Usage: $0 scan <target>"
        echo "Example: $0 scan 192.168.1.0/24"
        exit 1
    fi
    
    log_info "Scanning $target..."
    
    docker run -it --rm \
        --network host \
        --cap-add NET_RAW \
        --cap-add NET_ADMIN \
        -v netscan-exports:/app/exports \
        "$IMAGE_NAME:latest" \
        -s "$target"
}

run_lookup() {
    local mac="${1:-}"
    
    if [[ -z "$mac" ]]; then
        log_error "Usage: $0 lookup <mac_address>"
        echo "Example: $0 lookup 00:11:22:33:44:55"
        exit 1
    fi
    
    docker run --rm \
        -v netscan-cache:/app/cache \
        "$IMAGE_NAME:latest" \
        -l "$mac"
}

run_web() {
    local port="${1:-8080}"
    
    log_info "Starting NetScan web interface on port $port..."
    
    # Stop existing web container if running
    docker rm -f "$CONTAINER_NAME-web" 2>/dev/null || true
    
    docker run -d \
        --name "$CONTAINER_NAME-web" \
        -p "$port:8080" \
        -v netscan-cache:/app/cache:ro \
        -v netscan-data:/app/data:ro \
        -v netscan-exports:/app/exports \
        "$IMAGE_NAME:latest" \
        -w --port 8080 --host 0.0.0.0
    
    log_success "Web interface started at http://localhost:$port"
    echo ""
    echo "View logs: docker logs -f $CONTAINER_NAME-web"
    echo "Stop:      docker stop $CONTAINER_NAME-web"
}

run_shell() {
    log_info "Starting shell in NetScan container..."
    
    docker run -it --rm \
        --name "$CONTAINER_NAME-shell" \
        --network host \
        --cap-add NET_RAW \
        --cap-add NET_ADMIN \
        -v netscan-cache:/app/cache \
        -v netscan-logs:/app/logs \
        -v netscan-exports:/app/exports \
        --entrypoint /bin/bash \
        "$IMAGE_NAME:latest"
}

compose_up() {
    log_info "Starting NetScan with docker-compose..."
    cd "$SCRIPT_DIR"
    
    if [[ "${1:-}" == "web" ]]; then
        docker compose --profile web up -d
        log_success "NetScan + Web interface started"
    else
        docker compose up -d netscan
        log_success "NetScan started"
    fi
    
    echo ""
    echo "Attach to container: docker attach netscan"
    echo "View logs:           docker compose logs -f"
    echo "Stop:                docker compose down"
}

compose_down() {
    log_info "Stopping NetScan containers..."
    cd "$SCRIPT_DIR"
    docker compose --profile web down
    log_success "Containers stopped"
}

show_logs() {
    docker logs -f "${1:-$CONTAINER_NAME}" 2>/dev/null || \
        docker compose logs -f
}

clean_all() {
    log_warning "This will remove all NetScan containers, images, and volumes!"
    read -p "Are you sure? [y/N] " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Cleaning up..."
        
        # Stop and remove containers
        docker rm -f $(docker ps -aq --filter "name=netscan") 2>/dev/null || true
        
        # Remove images
        docker rmi -f $(docker images -q "$IMAGE_NAME") 2>/dev/null || true
        
        # Remove volumes
        docker volume rm $(docker volume ls -q --filter "name=netscan") 2>/dev/null || true
        
        log_success "Cleanup complete"
    else
        log_info "Cancelled"
    fi
}

show_status() {
    echo -e "${CYAN}=== NetScan Docker Status ===${NC}"
    echo ""
    
    echo -e "${YELLOW}Images:${NC}"
    docker images "$IMAGE_NAME" 2>/dev/null || echo "  No images found"
    echo ""
    
    echo -e "${YELLOW}Containers:${NC}"
    docker ps -a --filter "name=netscan" 2>/dev/null || echo "  No containers found"
    echo ""
    
    echo -e "${YELLOW}Volumes:${NC}"
    docker volume ls --filter "name=netscan" 2>/dev/null || echo "  No volumes found"
}

show_usage() {
    print_banner
    
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Build Commands:"
    echo "  build           Build the NetScan Docker image (with Rust)"
    echo "  build-slim      Build slim image (Python only, faster)"
    echo ""
    echo "Run Commands:"
    echo "  run [args]      Run NetScan interactively (default: --menu)"
    echo "  scan <target>   Quick network scan"
    echo "  lookup <mac>    Quick MAC vendor lookup"
    echo "  web [port]      Start web interface (default port: 8080)"
    echo "  shell           Open bash shell in container"
    echo ""
    echo "Docker Compose:"
    echo "  up              Start with docker-compose"
    echo "  up web          Start with web interface"
    echo "  down            Stop all containers"
    echo "  logs [name]     View container logs"
    echo ""
    echo "Management:"
    echo "  status          Show Docker resources status"
    echo "  clean           Remove all NetScan Docker resources"
    echo ""
    echo "Examples:"
    echo "  $0 build                    # Build image"
    echo "  $0 run                      # Interactive menu"
    echo "  $0 scan 192.168.1.0/24      # Scan network"
    echo "  $0 lookup 00:11:22:33:44:55 # Lookup vendor"
    echo "  $0 web 9000                 # Web on port 9000"
    echo "  $0 up web                   # Full stack with compose"
}

main() {
    check_docker
    
    case "${1:-}" in
        build)      build_image ;;
        build-slim) build_slim ;;
        run)        shift; run_interactive "$@" ;;
        scan)       shift; run_scan "$@" ;;
        lookup)     shift; run_lookup "$@" ;;
        web)        shift; run_web "$@" ;;
        shell)      run_shell ;;
        up)         shift; compose_up "$@" ;;
        down)       compose_down ;;
        logs)       shift; show_logs "$@" ;;
        status)     show_status ;;
        clean)      clean_all ;;
        -h|--help|help|"")
            show_usage
            ;;
        *)
            log_error "Unknown command: $1"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

main "$@"
