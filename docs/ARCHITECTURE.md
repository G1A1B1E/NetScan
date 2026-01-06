# Architecture Overview

This document describes the internal architecture of NetScan.

## Module Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          netscan                                │
│                      (main entry point)                         │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                         lib/ modules                            │
├──────────┬──────────┬──────────┬──────────┬────────────────────┤
│ config   │ logging  │ errors   │   ui     │     parsers        │
│   .sh    │   .sh    │   .sh    │   .sh    │       .sh          │
├──────────┼──────────┼──────────┼──────────┼────────────────────┤
│ vendor   │ loader   │ search   │ export   │                    │
│   .sh    │   .sh    │   .sh    │   .sh    │                    │
└──────────┴──────────┴──────────┴──────────┴────────────────────┘
                               │
                               ▼ (optional acceleration)
┌─────────────────────────────────────────────────────────────────┐
│                      helpers/ (Python)                          │
├────────────────────────────┬────────────────────────────────────┤
│      vendor_cache.py       │         fast_parser.py             │
│   (SQLite vendor cache)    │    (high-performance parsing)      │
└────────────────────────────┴────────────────────────────────────┘
```

## Module Responsibilities

### Core Modules (`lib/`)

| Module | Purpose |
|--------|---------|
| `config.sh` | Colors, global variables, directory paths |
| `logging.sh` | Session logging functions |
| `errors.sh` | Error codes, validation, trap handlers |
| `ui.sh` | Banner, menus, display helpers |
| `parsers.sh` | Format detection and file parsing |
| `vendor.sh` | MAC vendor API lookup |
| `loader.sh` | File loading orchestration |
| `search.sh` | Search and filtering functions |
| `export.sh` | CSV/JSON export |

### Python Helpers (`helpers/`)

| Module | Purpose |
|--------|---------|
| `vendor_cache.py` | SQLite-backed vendor cache with 30-day expiry |
| `fast_parser.py` | High-performance parsing for large files |

## Data Flow

```
Input File(s)
     │
     ▼
┌─────────────────┐
│ detect_format() │  ← Auto-detects XML, ARP, CSV, JSON, text
└─────────────────┘
     │
     ▼
┌─────────────────┐
│  parse_*_file() │  ← Format-specific parser
└─────────────────┘
     │
     ▼
┌─────────────────┐
│   TEMP_FILE     │  ← Normalized: MAC|IP|HOSTNAME|VENDOR
└─────────────────┘
     │
     ▼
┌─────────────────┐
│ lookup_vendor() │  ← API call (cached via Python helper)
└─────────────────┘
     │
     ▼
┌─────────────────┐
│    Display/     │
│    Export       │
└─────────────────┘
```

## Normalized Data Format

All parsed data is stored in `TEMP_FILE` with pipe-delimited format:

```
MAC_ADDRESS|IP_ADDRESS|HOSTNAME|VENDOR
```

Example:
```
AA:BB:CC:DD:EE:FF|192.168.1.100|mydevice|Apple, Inc.
BB:CC:DD:EE:FF:00|192.168.1.101|(none)|Samsung Electronics
```

## Error Handling Strategy

1. **Validation** - Check inputs before processing
2. **Graceful Degradation** - Fall back when Python unavailable
3. **Trap Handlers** - Clean exit on interrupt (Ctrl+C)
4. **Logging** - All errors logged to session log

## Caching Strategy

```
┌──────────────┐     ┌───────────────┐     ┌──────────────┐
│  MAC Lookup  │ ──► │ Check Cache   │ ──► │ Cache Hit?   │
└──────────────┘     └───────────────┘     └──────────────┘
                                                  │
                     ┌────────────────────────────┼────────────┐
                     │ Yes                        │ No         │
                     ▼                            ▼            │
              ┌──────────────┐           ┌──────────────┐      │
              │ Return Cache │           │  API Call    │      │
              └──────────────┘           └──────────────┘      │
                                                  │            │
                                                  ▼            │
                                         ┌──────────────┐      │
                                         │ Store Cache  │ ─────┘
                                         │ (30 days)    │
                                         └──────────────┘
```

## Adding New Features

### New Parser
1. Add `parse_FORMAT_file()` to `lib/parsers.sh`
2. Update `detect_file_format()` 
3. Add Python parser to `helpers/fast_parser.py`

### New Export Format
1. Add `export_to_FORMAT()` to `lib/export.sh`
2. Add menu option in `lib/ui.sh`
3. Add case handler in `netscan`

### New Search Function
1. Add function to `lib/search.sh`
2. Add menu option and case handler
