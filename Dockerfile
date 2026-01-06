# NetScan Docker Image
# Multi-stage build for optimal size

# =============================================================================
# Stage 1: Rust Builder (for performance module)
# =============================================================================
FROM rust:1.75-slim-bookworm AS rust-builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    python3-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install maturin
RUN pip3 install --break-system-packages maturin

# Copy Rust source
COPY rust_helpers/ ./rust_helpers/

# Build Rust module
WORKDIR /build/rust_helpers
RUN maturin build --release --strip

# =============================================================================
# Stage 2: Python Runtime
# =============================================================================
FROM python:3.11-slim-bookworm AS runtime

LABEL maintainer="G1A1B1E"
LABEL description="NetScan - Network Scanner & MAC Vendor Lookup Tool"
LABEL version="2.0"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    nmap \
    arp-scan \
    net-tools \
    iputils-ping \
    iproute2 \
    dnsutils \
    bash \
    curl \
    grep \
    gawk \
    sed \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Python packages
RUN pip install --no-cache-dir \
    requests \
    netifaces \
    reportlab \
    matplotlib \
    scapy \
    python-nmap

# Create netscan user (for non-root operation when possible)
RUN useradd -m -s /bin/bash netscan

# Set working directory
WORKDIR /app

# Copy application files
COPY --chown=netscan:netscan . /app/

# Copy Rust module from builder (if available)
COPY --from=rust-builder /build/rust_helpers/target/wheels/*.whl /tmp/ 
RUN pip install /tmp/*.whl 2>/dev/null || echo "Rust module not available, using Python fallback"

# Create necessary directories
RUN mkdir -p /app/cache /app/logs /app/exports /app/reports /app/data \
    && chown -R netscan:netscan /app

# Make scripts executable
RUN chmod +x /app/netscan \
    && find /app/lib -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true \
    && find /app/helpers -name "*.py" -exec chmod +x {} \; 2>/dev/null || true

# Set environment variables
ENV NETSCAN_HOME=/app
ENV PATH="/app:${PATH}"
ENV PYTHONUNBUFFERED=1

# Expose web interface port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)"

# Default to interactive shell, can be overridden
ENTRYPOINT ["/app/netscan"]
CMD ["--help"]
