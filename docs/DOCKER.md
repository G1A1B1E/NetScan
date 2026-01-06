# NetScan Docker Guide

Run NetScan in a container with all dependencies pre-installed. No local setup required!

## Quick Start

### Option 1: Using docker.sh Helper Script

```bash
# Build the image
./docker.sh build

# Run interactive menu
./docker.sh run

# Quick network scan
./docker.sh scan 192.168.1.0/24

# Quick MAC lookup
./docker.sh lookup 00:11:22:33:44:55

# Start web interface
./docker.sh web
```

### Option 2: Docker Compose

```bash
# Start NetScan
docker compose up -d

# Start with web interface
docker compose --profile web up -d

# Attach to container
docker attach netscan

# Stop
docker compose down
```

### Option 3: Direct Docker Commands

```bash
# Build
docker build -t netscan .

# Run interactive
docker run -it --rm \
    --network host \
    --cap-add NET_RAW \
    --cap-add NET_ADMIN \
    netscan --menu

# MAC lookup (no special permissions needed)
docker run --rm netscan -l 00:11:22:33:44:55

# Network scan (requires host network + capabilities)
docker run -it --rm \
    --network host \
    --cap-add NET_RAW \
    --cap-add NET_ADMIN \
    netscan -s 192.168.1.0/24
```

## Docker Images

### Full Image (with Rust)
```bash
./docker.sh build
# or
docker build -t netscan .
```
- Includes Rust performance module
- 10-100x faster for large operations
- Larger image size (~500MB)

### Slim Image (Python only)
```bash
./docker.sh build-slim
# or
docker build --target runtime -t netscan:slim .
```
- Python-only, no Rust compilation
- Faster to build
- Smaller image size (~300MB)
- Good enough for most use cases

## Network Scanning Requirements

For network scanning to work properly, the container needs:

### 1. Host Network Mode
```bash
docker run --network host ...
```
This allows the container to see your actual network interfaces and scan the local network.

### 2. Network Capabilities
```bash
docker run --cap-add NET_RAW --cap-add NET_ADMIN ...
```
- `NET_RAW`: Required for ping, arp-scan, raw sockets
- `NET_ADMIN`: Required for interface operations

### 3. Why Not Bridge Network?
With bridge networking, the container:
- Has its own IP (172.17.x.x)
- Can't see your local network (192.168.x.x)
- Can't perform ARP scans
- Only sees the Docker bridge network

## Persistent Data

Data is stored in Docker volumes:

| Volume | Purpose |
|--------|---------|
| `netscan-cache` | OUI database, vendor cache |
| `netscan-logs` | Scan logs, history |
| `netscan-exports` | Exported scan results |
| `netscan-reports` | Generated reports |
| `netscan-data` | Device database, settings |

### Manage Volumes

```bash
# List volumes
docker volume ls --filter "name=netscan"

# Inspect a volume
docker volume inspect netscan-cache

# Backup a volume
docker run --rm -v netscan-exports:/data -v $(pwd):/backup \
    alpine tar czf /backup/exports-backup.tar.gz -C /data .

# Restore a volume
docker run --rm -v netscan-exports:/data -v $(pwd):/backup \
    alpine tar xzf /backup/exports-backup.tar.gz -C /data
```

## Web Interface

### Start Web Server

```bash
# Using helper script
./docker.sh web 8080

# Using docker-compose
docker compose --profile web up -d

# Direct docker
docker run -d \
    --name netscan-web \
    -p 8080:8080 \
    netscan -w --port 8080 --host 0.0.0.0
```

### Access
Open http://localhost:8080 in your browser.

### Stop
```bash
docker stop netscan-web
# or
docker compose --profile web down
```

## Examples

### Interactive Session
```bash
./docker.sh run
# or
docker run -it --rm --network host --cap-add NET_RAW --cap-add NET_ADMIN netscan --menu
```

### Batch MAC Lookup
```bash
echo "00:11:22:33:44:55
AA:BB:CC:DD:EE:FF
11:22:33:44:55:66" | docker run -i --rm netscan -f -
```

### Export Scan Results
```bash
# Scan and export to volume
docker run -it --rm \
    --network host \
    --cap-add NET_RAW \
    -v netscan-exports:/app/exports \
    netscan -s 192.168.1.0/24 --export json

# Copy from volume to host
docker cp netscan:/app/exports/scan_results.json ./
```

### Scheduled Scanning (with cron)
```bash
# Add to crontab
0 */6 * * * docker run --rm --network host --cap-add NET_RAW netscan -s 192.168.1.0/24 -q >> /var/log/netscan.log
```

## Troubleshooting

### "Permission denied" for network operations
```bash
# Make sure you're using the required capabilities
docker run --cap-add NET_RAW --cap-add NET_ADMIN ...
```

### Can't see local network devices
```bash
# Use host network mode
docker run --network host ...
```

### Container exits immediately
```bash
# Use -it for interactive mode
docker run -it ...

# Or check logs
docker logs netscan
```

### Slow first run
The first run may be slow as it:
1. Downloads the OUI database
2. Builds the vendor cache
3. Initializes the database

Subsequent runs will be faster due to cached data in volumes.

### Web interface not accessible
```bash
# Make sure port is published
docker run -p 8080:8080 ...

# Check if container is running
docker ps

# Check container logs
docker logs netscan-web
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NETSCAN_HOME` | `/app` | Application directory |
| `TZ` | `UTC` | Timezone for logs |

## Security Considerations

⚠️ **Running with `--network host` and `--cap-add NET_RAW`** gives the container significant network access. Only run trusted images.

For enhanced security:
1. Build the image yourself (don't use untrusted images)
2. Run as non-root user when possible
3. Use read-only volumes where appropriate
4. Limit resource usage with `--memory` and `--cpus`

## CI/CD Integration

### GitHub Actions
```yaml
- name: Build NetScan
  run: docker build -t netscan .

- name: Run scan
  run: |
    docker run --rm netscan -l 00:11:22:33:44:55
```

### GitLab CI
```yaml
build:
  script:
    - docker build -t netscan .
    
test:
  script:
    - docker run --rm netscan --help
```
