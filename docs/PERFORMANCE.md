# NetScan Performance Optimization Guide

## Overview

NetScan can be significantly accelerated (10-100x) by compiling the optional Rust performance module. The Python code will automatically use Rust when available, with seamless fallback to pure Python.

## Performance Comparison

| Operation | Python | Rust | Speedup |
|-----------|--------|------|---------|
| MAC normalization (1000 MACs) | ~50ms | ~0.5ms | **100x** |
| CIDR expansion (/16 = 65K IPs) | ~200ms | ~5ms | **40x** |
| OUI file parsing (30K entries) | ~500ms | ~10ms | **50x** |
| Batch vendor lookup (1000 MACs) | ~100ms | ~2ms | **50x** |
| ARP output parsing (1000 lines) | ~80ms | ~2ms | **40x** |
| TCP port scan (254 hosts, 10 ports) | ~30s | ~3s | **10x** |

## Installation

### Option 1: Quick Install (Recommended)

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# Install maturin (Python build tool for Rust)
pip3 install maturin

# Build the performance module
./build_rust.sh
```

### Option 2: macOS with Homebrew

```bash
brew install rust
pip3 install maturin
./build_rust.sh
```

### Option 3: Manual Build

```bash
cd rust_helpers
cargo build --release
# Copy the library to helpers/
cp target/release/libnetscan_core.dylib ../helpers/netscan_core.so
```

## Verification

After building, verify the module is working:

```bash
python3 helpers/fast_core.py
```

You should see:
```
✓ Using Rust backend (10-100x faster)

Normalized 4000 MACs in 0.45ms
  Rate: 8888888 MACs/sec

Expanded /24 to 254 hosts in 0.02ms
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Python Layer                             │
│  async_scanner.py, vendor_cache.py, fast_parser.py, etc.    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    fast_core.py                              │
│          (Auto-selects Rust or Python backend)               │
└─────────────────────────────────────────────────────────────┘
                    │                       │
          ┌────────┴────────┐     ┌────────┴────────┐
          ▼                 ▼     ▼                 ▼
    ┌──────────┐      ┌──────────────┐      ┌──────────────┐
    │   Rust   │      │    Python    │      │   Python     │
    │  Module  │      │   Fallback   │      │  Fallback    │
    │ (10-100x)│      │ (Compatible) │      │ (Compatible) │
    └──────────┘      └──────────────┘      └──────────────┘
```

## What Gets Accelerated

### 1. MAC Address Processing
- Normalization (XX:XX:XX:XX:XX:XX format)
- Batch processing with parallelization
- OUI prefix extraction

### 2. OUI Database
- Memory-mapped file parsing
- Parallel line processing with rayon
- Hash-based lookups

### 3. IP Address Utilities
- CIDR expansion (network.hosts())
- IP range generation
- Numeric IP sorting
- Private IP detection

### 4. Network Scanning
- Async TCP connect scanning with tokio
- Concurrent host discovery
- Port scanning with configurable concurrency

### 5. File Parsing
- ARP table output parsing
- Pipe-delimited file parsing
- Device deduplication

## Rust Module Structure

```
rust_helpers/
├── Cargo.toml           # Dependencies and build config
├── src/
│   ├── lib.rs          # Main module with MAC, IP, parsing functions
│   └── scanner.rs      # Async TCP scanner
```

### Key Dependencies

- **pyo3**: Python bindings for Rust
- **rayon**: Data parallelism (parallel iterators)
- **tokio**: Async runtime for network I/O
- **dashmap**: Concurrent HashMap
- **memmap2**: Memory-mapped file I/O
- **regex**: Pattern matching
- **ipnetwork**: IP/CIDR handling

## Troubleshooting

### Module not loading

```bash
# Check if the .so file exists
ls -la helpers/netscan_core*.so

# Check Python can find it
python3 -c "import sys; sys.path.insert(0, 'helpers'); import netscan_core"
```

### Build failures

```bash
# Update Rust
rustup update

# Clean and rebuild
cd rust_helpers
cargo clean
cargo build --release
```

### Performance not improved

Make sure you're using the module:

```python
from helpers.fast_core import get_backend_info
print(get_backend_info())
# Should show: {'rust_available': True, 'backend': 'rust', ...}
```

## Without Rust

NetScan works perfectly fine without Rust - just slower for large-scale operations. The pure Python implementation is:

- Fully compatible
- Easier to debug
- No compilation needed
- Sufficient for small networks (<100 devices)

Consider compiling Rust if you're:
- Scanning large networks (/16 or bigger)
- Processing many MAC addresses
- Doing frequent vendor lookups
- Running automated scans
