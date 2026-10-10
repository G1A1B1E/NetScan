// =============================================================================
// NetScan Documentation - Wrapped Content Module
// =============================================================================

window.NETSCAN_CONTENT = `
<!-- Top Navigation -->
    <header class="top-nav">
        <div class="nav-container">
            <a href="#overview" class="logo">
                <span class="logo-icon">⌘</span>
                <span class="logo-text">NetScan</span>
            </a>
            <nav class="nav-links">
                <a href="#overview" class="active">Overview</a>
                <a href="#installation">Installation</a>
                <a href="#quickstart">Quick Start</a>
                <a href="#scanning">Scanning</a>
                <a href="#security">Security</a>
                <a href="#cli-reference">CLI Reference</a>
                <a href="#api">API</a>
                <a href="https://github.com/G1A1B1E/NetScan" target="_blank" class="github-link">
                    <svg height="20" width="20" viewBox="0 0 16 16" fill="currentColor">
                        <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
                    </svg>
                    GitHub
                </a>
            </nav>
            <button class="mobile-menu-btn" aria-label="Toggle menu">
                <span></span>
                <span></span>
                <span></span>
            </button>
        </div>
    </header>

    <div class="main-wrapper">
        <!-- Sidebar Navigation -->
        <aside class="sidebar">
            <div class="sidebar-content">
                <div class="search-box">
                    <input type="text" placeholder="Filter documentation..." id="search-input" autocomplete="off">
                    <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="11" cy="11" r="8"></circle>
                        <path d="M21 21l-4.35-4.35"></path>
                    </svg>
                </div>

                <nav class="sidebar-nav">
                    <div class="nav-section">
                        <h3>Getting Started</h3>
                        <ul>
                            <li><a href="#overview" class="active">Overview & Downloads</a></li>
                            <li><a href="#installation">Installation Guide</a></li>
                            <li><a href="#quickstart">Quick Start Tutorial</a></li>
                        </ul>
                    </div>

                    <div class="nav-section">
                        <h3>Core Features</h3>
                        <ul>
                            <li><a href="#usage">Interactive CLI Menu</a></li>
                            <li><a href="#scanning">Network Scanning</a></li>
                            <li><a href="#mac-lookup">MAC & Vendor Lookup</a></li>
                            <li><a href="#monitoring">Real-Time Monitor</a></li>
                            <li><a href="#web-interface">Web UI & REST API</a></li>
                        </ul>
                    </div>

                    <div class="nav-section">
                        <h3>Intelligence Suite</h3>
                        <ul>
                            <li><a href="#fingerprinting">Device Fingerprinting</a></li>
                            <li><a href="#topology">Network Topology</a></li>
                            <li><a href="#security">Security Audit</a></li>
                            <li><a href="#scheduler">Scheduled Scans</a></li>
                            <li><a href="#wol">Wake-on-LAN</a></li>
                            <li><a href="#export">Export & Reports</a></li>
                        </ul>
                    </div>

                    <div class="nav-section">
                        <h3>Advanced</h3>
                        <ul>
                            <li><a href="#configuration">Configuration</a></li>
                            <li><a href="#api">Python API Reference</a></li>
                            <li><a href="#performance">Rust Acceleration</a></li>
                            <li><a href="#docker">Docker Deployment</a></li>
                        </ul>
                    </div>

                    <div class="nav-section">
                        <h3>Reference</h3>
                        <ul>
                            <li><a href="#cli-reference">CLI Reference Table</a></li>
                            <li><a href="#troubleshooting">Troubleshooting & FAQ</a></li>
                            <li><a href="#changelog">Changelog</a></li>
                            <li><a href="#contributing">Contributing</a></li>
                        </ul>
                    </div>
                </nav>
            </div>
        </aside>

        <!-- Main Content -->
        <main class="content">
            <article class="doc-content">

                <!-- HERO SECTION -->
                <section class="hero" id="overview">
                    <div class="badge-container" style="display:flex; justify-content:center; gap:8px; flex-wrap:wrap; margin-bottom:16px;">
                        <span class="badge" style="background:#0066cc; color:#fff; padding:4px 10px; border-radius:12px; font-size:12px; font-weight:600;">v3.0.0</span>
                        <span class="badge" style="background:#28a745; color:#fff; padding:4px 10px; border-radius:12px; font-size:12px; font-weight:600;">Electron 28 GUI</span>
                        <span class="badge" style="background:#17a2b8; color:#fff; padding:4px 10px; border-radius:12px; font-size:12px; font-weight:600;">Bash 3.2+ & Python 3.7+</span>
                        <span class="badge" style="background:#6c757d; color:#fff; padding:4px 10px; border-radius:12px; font-size:12px; font-weight:600;">Rust Accelerated</span>
                        <span class="badge" style="background:#ffc107; color:#222; padding:4px 10px; border-radius:12px; font-size:12px; font-weight:600;">MIT License</span>
                    </div>
                    <h1>NetScan</h1>
                    <p class="lead">All-in-one Network Intelligence Suite. Discover devices, resolve MAC vendors with SQLite caching, map network topology, audit security risks, and automate monitoring — via an interactive CLI or modern Desktop GUI.</p>

                    <div class="hero-buttons">
                        <a href="#installation" class="btn btn-primary">Download & Install</a>
                        <a href="#quickstart" class="btn btn-secondary">5-Minute Quick Start</a>
                        <a href="#cli-reference" class="btn btn-secondary">CLI Reference</a>
                    </div>

                    <div class="code-block" style="margin-top:24px; text-align:left;">
                        <div class="code-header">
                            <span>One-Line CLI Install</span>
                            <button class="copy-btn">Copy</button>
                        </div>
                        <pre><code class="language-bash">curl -fsSL https://raw.githubusercontent.com/G1A1B1E/NetScan/main/install.sh | bash</code></pre>
                    </div>

                    <div class="features-grid" style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:16px; margin-top:32px; text-align:left;">
                        <div class="feature-card" style="padding:16px; background:var(--color-bg-secondary); border:1px solid var(--color-border); border-radius:var(--radius-md);">
                            <div style="font-size:24px; margin-bottom:8px;">⚡</div>
                            <h4 style="margin:0 0 4px 0;">Async Discovery</h4>
                            <p style="margin:0; font-size:14px; color:var(--color-text-light);">Concurrent ping sweeps, ARP table inspection, and port probes across full subnets in seconds.</p>
                        </div>
                        <div class="feature-card" style="padding:16px; background:var(--color-bg-secondary); border:1px solid var(--color-border); border-radius:var(--radius-md);">
                            <div style="font-size:24px; margin-bottom:8px;">🏷️</div>
                            <h4 style="margin:0 0 4px 0;">MAC Vendor Lookup</h4>
                            <p style="margin:0; font-size:14px; color:var(--color-text-light);">Instant OUI normalization with SQLite caching (30-day TTL) and online API fallback.</p>
                        </div>
                        <div class="feature-card" style="padding:16px; background:var(--color-bg-secondary); border:1px solid var(--color-border); border-radius:var(--radius-md);">
                            <div style="font-size:24px; margin-bottom:8px;">🗺️</div>
                            <h4 style="margin:0 0 4px 0;">Topology Mapping</h4>
                            <p style="margin:0; font-size:14px; color:var(--color-text-light);">Gateway and subnet discovery with ASCII trees, Graphviz DOT exports, and interactive vis.js HTML graphs.</p>
                        </div>
                        <div class="feature-card" style="padding:16px; background:var(--color-bg-secondary); border:1px solid var(--color-border); border-radius:var(--radius-md);">
                            <div style="font-size:24px; margin-bottom:8px;">🛡️</div>
                            <h4 style="margin:0 0 4px 0;">Security Auditing</h4>
                            <p style="margin:0; font-size:14px; color:var(--color-text-light);">Detect exposed databases, insecure Telnet/FTP, expired SSL certs, and missing HTTP security headers.</p>
                        </div>
                    </div>
                </section>

                <!-- INSTALLATION SECTION -->
                <section id="installation">
                    <h2>Installation Guide</h2>
                    <p class="lead">NetScan is available as a Desktop GUI (macOS and Windows) or a standalone CLI tool for macOS, Linux, and Windows.</p>

                    <h3>1. Desktop GUI Installers</h3>
                    <table class="download-table" style="width:100%; border-collapse:collapse; margin-bottom:20px;">
                        <thead>
                            <tr style="border-bottom:2px solid var(--color-border);">
                                <th style="text-align:left; padding:8px;">Platform</th>
                                <th style="text-align:left; padding:8px;">Package</th>
                                <th style="text-align:left; padding:8px;">Description</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr style="border-bottom:1px solid var(--color-border);">
                                <td style="padding:8px;"><strong>macOS (Full Package)</strong></td>
                                <td style="padding:8px;"><a href="https://github.com/G1A1B1E/NetScan/releases/download/v3.0.0/NetScan-3.0.0-Installer.pkg">NetScan-3.0.0-Installer.pkg</a></td>
                                <td style="padding:8px;">Complete installer with GUI + CLI tools</td>
                            </tr>
                            <tr style="border-bottom:1px solid var(--color-border);">
                                <td style="padding:8px;"><strong>macOS (Apple Silicon)</strong></td>
                                <td style="padding:8px;"><a href="https://github.com/G1A1B1E/NetScan/releases/download/v3.0.0/NetScan-3.0.0-arm64.dmg">NetScan-3.0.0-arm64.dmg</a></td>
                                <td style="padding:8px;">Drag-and-drop DMG for M1/M2/M3/M4 Macs</td>
                            </tr>
                            <tr style="border-bottom:1px solid var(--color-border);">
                                <td style="padding:8px;"><strong>macOS (Intel)</strong></td>
                                <td style="padding:8px;"><a href="https://github.com/G1A1B1E/NetScan/releases/download/v3.0.0/NetScan-3.0.0.dmg">NetScan-3.0.0.dmg</a></td>
                                <td style="padding:8px;">Drag-and-drop DMG for Intel Macs</td>
                            </tr>
                            <tr style="border-bottom:1px solid var(--color-border);">
                                <td style="padding:8px;"><strong>Windows Setup</strong></td>
                                <td style="padding:8px;"><a href="https://github.com/G1A1B1E/NetScan/releases/download/v3.0.0/NetScan-3.0.0-Setup.exe">NetScan-3.0.0-Setup.exe</a></td>
                                <td style="padding:8px;">Windows NSIS installer wizard</td>
                            </tr>
                            <tr style="border-bottom:1px solid var(--color-border);">
                                <td style="padding:8px;"><strong>Windows Portable</strong></td>
                                <td style="padding:8px;"><a href="https://github.com/G1A1B1E/NetScan/releases/download/v3.0.0/NetScan-3.0.0-Windows.zip">NetScan-3.0.0-Windows.zip</a></td>
                                <td style="padding:8px;">Zero-install portable ZIP archive</td>
                            </tr>
                        </tbody>
                    </table>

                    <h3>2. CLI Installation (macOS & Linux)</h3>
                    <p>The automated script checks dependencies and configures the environment:</p>

                    <div class="code-block">
                        <div class="code-header">
                            <span>Global Install (System-Wide, requires sudo)</span>
                            <button class="copy-btn">Copy</button>
                        </div>
                        <pre><code class="language-bash">curl -fsSL https://raw.githubusercontent.com/G1A1B1E/NetScan/main/install.sh | bash</code></pre>
                    </div>

                    <div class="code-block">
                        <div class="code-header">
                            <span>User-Only Install (No sudo, installs to ~/.local/bin)</span>
                            <button class="copy-btn">Copy</button>
                        </div>
                        <pre><code class="language-bash">bash &lt;(curl -fsSL https://raw.githubusercontent.com/G1A1B1E/NetScan/main/install.sh) --local</code></pre>
                    </div>

                    <h3>3. Package Manager Manual Setup</h3>
                    <p>Install prerequisites using your platform's package manager:</p>

                    <div class="code-block">
                        <div class="code-header"><span>macOS (Homebrew)</span><button class="copy-btn">Copy</button></div>
                        <pre><code class="language-bash">brew install python@3 nmap arp-scan
git clone https://github.com/G1A1B1E/NetScan.git ~/.netscan
cd ~/.netscan && ./install.sh --local</code></pre>
                    </div>

                    <div class="code-block">
                        <div class="code-header"><span>Ubuntu / Debian</span><button class="copy-btn">Copy</button></div>
                        <pre><code class="language-bash">sudo apt update && sudo apt install -y python3 python3-pip nmap arp-scan git curl
git clone https://github.com/G1A1B1E/NetScan.git ~/.netscan
cd ~/.netscan && ./install.sh</code></pre>
                    </div>

                    <div class="code-block">
                        <div class="code-header"><span>Fedora / RHEL</span><button class="copy-btn">Copy</button></div>
                        <pre><code class="language-bash">sudo dnf install -y python3 python3-pip nmap arp-scan git curl
git clone https://github.com/G1A1B1E/NetScan.git ~/.netscan
cd ~/.netscan && ./install.sh</code></pre>
                    </div>

                    <h3>4. Windows CLI Setup</h3>
                    <p>NetScan provides a native PowerShell 5.1+ port located in the <code>windows/</code> directory:</p>
                    <div class="code-block">
                        <div class="code-header"><span>PowerShell (Run as Administrator)</span><button class="copy-btn">Copy</button></div>
                        <pre><code class="language-powershell">git clone https://github.com/G1A1B1E/NetScan.git
cd NetScan\windows
.\install.ps1</code></pre>
                    </div>
                </section>

                <!-- QUICK START SECTION -->
                <section id="quickstart">
                    <h2>Quick Start Tutorial</h2>
                    <p class="lead">Get up and running with NetScan in 5 minutes.</p>

                    <h3>Option A: Using the Desktop GUI</h3>
                    <ol>
                        <li>Launch the <strong>NetScan</strong> application from your Applications menu or desktop shortcut.</li>
                        <li>The application auto-detects your primary network adapter (e.g., <code>192.168.1.0/24</code>).</li>
                        <li>Click the <strong>Quick Scan</strong> button in the top right header.</li>
                        <li>Discovered devices appear with IP, MAC, Vendor, Hostname, and status in real time.</li>
                        <li>Use the sidebar to jump to <strong>Topology</strong> for a visual map or <strong>Security</strong> for risk analysis.</li>
                    </ol>

                    <h3>Option B: Using the CLI</h3>
                    <p>Launch the interactive terminal interface with a single command:</p>
                    <div class="code-block">
                        <pre><code class="language-bash">netscan</code></pre>
                    </div>

                    <p>Or perform direct non-interactive scans and queries right from your shell:</p>
                    <div class="code-block">
                        <div class="code-header"><span>Quick Subnet Sweep</span><button class="copy-btn">Copy</button></div>
                        <pre><code class="language-bash"># Quick scan local subnet and display devices
netscan -s

# Scan a specific subnet
netscan -s -t 192.168.1.0/24

# Look up vendor for any MAC address
netscan -l 00:50:56:C0:00:08

# Start the built-in browser web UI on port 8080
netscan -w</code></pre>
                    </div>

                    <h3>Working with Sample Files</h3>
                    <p>NetScan includes sample data files to test without scanning a live network:</p>
                    <div class="code-block">
                        <pre><code class="language-bash"># Load sample devices CSV
netscan example/devices.csv

# Load sample network JSON
netscan example/network.json</code></pre>
                    </div>
                </section>

                <!-- INTERACTIVE CLI MENU -->
                <section id="usage">
                    <h2>Interactive CLI Menu</h2>
                    <p class="lead">When launched without arguments, <code>netscan</code> displays an interactive terminal menu with hotkeys.</p>

                    <table class="data-table" style="width:100%; border-collapse:collapse; margin-bottom:20px;">
                        <thead>
                            <tr style="border-bottom:2px solid var(--color-border);">
                                <th style="text-align:left; padding:8px;">Key</th>
                                <th style="text-align:left; padding:8px;">Action</th>
                                <th style="text-align:left; padding:8px;">Description</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr style="border-bottom:1px solid var(--color-border);"><td style="padding:8px;"><code>1</code></td><td style="padding:8px;">Load file</td><td style="padding:8px;">Load and parse Nmap XML, ARP table, CSV, JSON, or text file</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td style="padding:8px;"><code>2</code></td><td style="padding:8px;">Load multiple files</td><td style="padding:8px;">Merge scan files with intelligent deduplication</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td style="padding:8px;"><code>3</code></td><td style="padding:8px;">List all devices</td><td style="padding:8px;">Formatted display of all loaded devices with vendor resolution</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td style="padding:8px;"><code>4</code></td><td style="padding:8px;">Search devices</td><td style="padding:8px;">Search across hostname, IP, MAC, or vendor fields</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td style="padding:8px;"><code>5</code></td><td style="padding:8px;">Search by vendor</td><td style="padding:8px;">Filter devices by manufacturer name (e.g. Apple, Cisco)</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td style="padding:8px;"><code>6</code></td><td style="padding:8px;">Find IP by hostname</td><td style="padding:8px;">Reverse hostname lookup in loaded dataset</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td style="padding:8px;"><code>7</code></td><td style="padding:8px;">Find IP by MAC</td><td style="padding:8px;">Locate device IP matching a MAC address</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td style="padding:8px;"><code>8</code></td><td style="padding:8px;">Network summary</td><td style="padding:8px;">Device counts, vendor distribution statistics, and subnet metrics</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td style="padding:8px;"><code>9</code></td><td style="padding:8px;">Export to CSV</td><td style="padding:8px;">Export normalized device table to spreadsheet format</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td style="padding:8px;"><code>s</code></td><td style="padding:8px;">Network Scanning</td><td style="padding:8px;">Open the scanning sub-menu (quick, Nmap, Python async, security)</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td style="padding:8px;"><code>e</code></td><td style="padding:8px;">Load examples</td><td style="padding:8px;">Quickly load included sample files from <code>example/</code></td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td style="padding:8px;"><code>r</code></td><td style="padding:8px;">Refresh vendors</td><td style="padding:8px;">Re-query online API for missing vendor entries</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td style="padding:8px;"><code>c</code></td><td style="padding:8px;">Capabilities</td><td style="padding:8px;">Inspect system tools, Python helpers, and Rust acceleration status</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td style="padding:8px;"><code>0</code> / <code>q</code></td><td style="padding:8px;">Exit</td><td style="padding:8px;">Clean up temporary files and close session</td></tr>
                        </tbody>
                    </table>

                    <h3>Supported File Formats</h3>
                    <p>NetScan's parser engine automatically identifies and extracts IP, MAC, and hostname records from:</p>
                    <ul>
                        <li><strong>Nmap XML:</strong> Output from <code>nmap -oX scan.xml</code></li>
                        <li><strong>ARP Tables:</strong> Standard output from <code>arp -a</code></li>
                        <li><strong>CSV:</strong> Tables with <code>ip,mac,hostname,vendor</code> headers</li>
                        <li><strong>JSON:</strong> Array of objects or structured NetScan scan results</li>
                        <li><strong>Plain Text:</strong> Freeform logs containing IP and MAC addresses</li>
                    </ul>
                </section>

                <!-- NETWORK SCANNING -->
                <section id="scanning">
                    <h2>Network Scanning & Discovery</h2>
                    <p class="lead">Built-in discovery engines support everything from lightweight passive ARP lookups to concurrent multi-port sweeps.</p>

                    <h3>1. Quick Scans</h3>
                    <div class="code-block">
                        <pre><code class="language-bash"># ARP cache dump (instant, zero network traffic)
netscan -s --arp-only

# Ping sweep (ICMP discovery across local subnet)
netscan -s -t 192.168.1.0/24</code></pre>
                    </div>

                    <h3>2. Python Async Scanner (<code>async_scanner.py</code>)</h3>
                    <p>High-concurrency network discovery using Python <code>asyncio</code>:</p>
                    <div class="code-block">
                        <div class="code-header"><span>Async Network Scanner</span><button class="copy-btn">Copy</button></div>
                        <pre><code class="language-bash"># Scan CIDR subnet with 100 concurrent workers
python3 helpers/async_scanner.py --target 192.168.1.0/24

# Output structured JSON results to file
python3 helpers/async_scanner.py --target 10.0.0.0/24 --json --output scan.json

# Scan with open port discovery on top services
python3 helpers/async_scanner.py --target 192.168.1.0/24 --ports 22,80,443,445,3389</code></pre>
                    </div>

                    <h3>3. Nmap Profiles</h3>
                    <p>When Nmap is installed, NetScan provides preset scanning modes:</p>
                    <ul>
                        <li><strong>Host Discovery (<code>-sn</code>):</strong> Ping sweep without port scanning.</li>
                        <li><strong>Quick Scan:</strong> Probes top 100 common ports.</li>
                        <li><strong>Standard Scan:</strong> Probes top 1,000 common ports.</li>
                        <li><strong>Service Detection (<code>-sV</code>):</strong> Interrogates listening ports for software versions.</li>
                        <li><strong>Aggressive (<code>-A</code>):</strong> OS detection, service versions, script scanning, and traceroute.</li>
                        <li><strong>Vulnerability Audit:</strong> Runs Nmap NSE vulnerability detection scripts.</li>
                    </ul>
                </section>

                <!-- MAC & VENDOR LOOKUP -->
                <section id="mac-lookup">
                    <h2>MAC Address & Vendor Lookup</h2>
                    <p class="lead">Normalize MAC addresses and resolve device manufacturers with offline SQLite caching.</p>

                    <div class="code-block">
                        <div class="code-header"><span>MAC Lookup CLI</span><button class="copy-btn">Copy</button></div>
                        <pre><code class="language-bash"># Query individual MAC address (any common format)
netscan -l 00:50:56:C0:00:08
netscan -l 00-50-56-C0-00-08
netscan -l 005056C00008

# Batch resolve from a file containing one MAC per line
netscan -b example/macs.txt -o resolved_vendors.json</code></pre>
                    </div>

                    <h3>Caching Architecture</h3>
                    <p>To prevent hitting API rate limits and enable offline work, NetScan stores lookups in a local SQLite database (<code>~/.local/share/netscan/cache/vendor_cache.db</code>):</p>
                    <ul>
                        <li><strong>30-Day Expiry:</strong> Cached entries are automatically kept fresh.</li>
                        <li><strong>OUI Extraction:</strong> Matches against the 24-bit organizationally unique identifier (first 3 octets).</li>
                        <li><strong>Batch Caching:</strong> Pre-fetches in parallel for entire subnets.</li>
                    </ul>

                    <div class="code-block">
                        <div class="code-header"><span>Vendor Cache Helper</span><button class="copy-btn">Copy</button></div>
                        <pre><code class="language-bash"># View cache statistics (total records, hit rate)
python3 helpers/vendor_cache.py --stats

# Clean expired entries
python3 helpers/vendor_cache.py --cleanup</code></pre>
                    </div>
                </section>

                <!-- REAL-TIME MONITOR -->
                <section id="monitoring">
                    <h2>Real-Time Network Monitoring</h2>
                    <p class="lead">Continuously track connected devices, log state changes, and receive desktop alerts when unknown devices join your network.</p>

                    <div class="code-block">
                        <div class="code-header"><span>Monitor CLI</span><button class="copy-btn">Copy</button></div>
                        <pre><code class="language-bash"># Start real-time network monitor with 60-second intervals
netscan -m

# Enable native OS desktop notifications
netscan -m --notify

# Custom interval and log file
netscan -m --interval 30 --log ~/.netscan/monitor.log</code></pre>
                    </div>

                    <h3>Detection Capabilities</h3>
                    <ul>
                        <li><strong>New Devices:</strong> Alerts immediately when a previously unseen MAC appears.</li>
                        <li><strong>Departed Devices:</strong> Flags devices that have stopped responding after a grace period.</li>
                        <li><strong>IP Reassignments:</strong> Logs when an existing device changes DHCP IP addresses.</li>
                        <li><strong>Device History:</strong> All events are recorded in SQLite (<code>device_history</code> table) for auditing.</li>
                    </ul>
                </section>

                <!-- WEB INTERFACE & REST API -->
                <section id="web-interface">
                    <h2>Web UI & REST API</h2>
                    <p class="lead">NetScan includes a standalone, zero-dependency browser interface and REST API powered by Python's built-in HTTP server.</p>

                    <div class="code-block">
                        <div class="code-header"><span>Start Web Server</span><button class="copy-btn">Copy</button></div>
                        <pre><code class="language-bash"># Start web interface on default port 8080 (http://localhost:8080)
netscan -w

# Bind to custom port and network interface
python3 helpers/web_server.py --port 9000 --bind 0.0.0.0</code></pre>
                    </div>

                    <h3>REST API Endpoints</h3>
                    <table class="data-table" style="width:100%; border-collapse:collapse; margin-bottom:20px;">
                        <thead>
                            <tr style="border-bottom:2px solid var(--color-border);">
                                <th style="text-align:left; padding:8px;">Endpoint</th>
                                <th style="text-align:left; padding:8px;">Method</th>
                                <th style="text-align:left; padding:8px;">Description</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr style="border-bottom:1px solid var(--color-border);"><td><code>/api/devices</code></td><td>GET</td><td>Returns list of all active network devices in JSON format</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td><code>/api/scan</code></td><td>POST</td><td>Triggers a fresh network discovery scan</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td><code>/api/lookup/&lt;mac&gt;</code></td><td>GET</td><td>Looks up vendor for the specified MAC address</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td><code>/api/status</code></td><td>GET</td><td>Server uptime, scan timestamps, and device counts</td></tr>
                        </tbody>
                    </table>

                    <div class="code-block">
                        <div class="code-header"><span>Curl Example</span><button class="copy-btn">Copy</button></div>
                        <pre><code class="language-bash">curl -s http://localhost:8080/api/devices | jq .</code></pre>
                    </div>
                </section>

                <!-- DEVICE FINGERPRINTING -->
                <section id="fingerprinting">
                    <h2>Device Fingerprinting</h2>
                    <p class="lead">Classify device types and operating systems using TTL heuristics, MAC vendor signatures, and port probes.</p>

                    <div class="code-block">
                        <div class="code-header"><span>Fingerprint Command</span><button class="copy-btn">Copy</button></div>
                        <pre><code class="language-bash"># Fingerprint a single host
python3 helpers/fingerprint.py --target 192.168.1.1 --verbose

# Fingerprint entire network and export JSON
python3 helpers/fingerprint.py --scan-network --output fingerprints.json

# Fingerprint existing scan results without re-scanning
python3 helpers/fingerprint.py --input scan_results.json</code></pre>
                    </div>

                    <h3>Supported Classifications</h3>
                    <table class="data-table" style="width:100%; border-collapse:collapse;">
                        <thead>
                            <tr style="border-bottom:2px solid var(--color-border);">
                                <th style="text-align:left; padding:8px;">Category</th>
                                <th style="text-align:left; padding:8px;">Identification Heuristics</th>
                                <th style="text-align:left; padding:8px;">Example Devices</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr style="border-bottom:1px solid var(--color-border);"><td>🌐 <strong>Routers & APs</strong></td><td>Ports 80/443/53/67, TTL=64, OUI</td><td>TP-Link, Netgear, UniFi, ASUS</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td>🖥️ <strong>Servers</strong></td><td>SSH (22), Web (80/443), SMB (445), DB ports</td><td>Linux Servers, Windows Server, NAS</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td>📺 <strong>Smart TVs / Media</strong></td><td>Chromecast (8008), AirPlay (7000), DIAL</td><td>Apple TV, Roku, Samsung Tizen, LG WebOS</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td>📹 <strong>IP Cameras</strong></td><td>RTSP (554), ONVIF (8000), HTTP</td><td>Hikvision, Dahua, Reolink</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td>🖨️ <strong>Printers</strong></td><td>IPP (631), LPD (515), RAW (9100)</td><td>HP, Canon, Brother, Epson</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td>📱 <strong>Mobile Devices</strong></td><td>TTL characteristics, mDNS, vendor OUI</td><td>iPhones, iPads, Android devices</td></tr>
                        </tbody>
                    </table>
                </section>

                <!-- NETWORK TOPOLOGY -->
                <section id="topology">
                    <h2>Network Topology Mapping</h2>
                    <p class="lead">Visualize relationships between gateways, subnets, routers, and connected hosts.</p>

                    <div class="code-block">
                        <div class="code-header"><span>Topology CLI</span><button class="copy-btn">Copy</button></div>
                        <pre><code class="language-bash"># Render ASCII network tree in terminal
python3 helpers/topology.py --scan --ascii

# Generate interactive vis.js HTML map
python3 helpers/topology.py --scan --html --output network_topology.html

# Generate Graphviz DOT file and render PNG
python3 helpers/topology.py --scan --dot --output network.dot
dot -Tpng network.dot -o network.png</code></pre>
                    </div>

                    <h3>Sample ASCII Topology Output</h3>
                    <div class="code-block">
                        <pre><code class="language-text">Gateway: 192.168.1.1 (Cisco Router)
├── [Subnet 192.168.1.0/24]
│   ├── 192.168.1.10  (File Server)      [Ports: 22, 445]
│   ├── 192.168.1.25  (Office Printer)   [Ports: 631, 9100]
│   ├── 192.168.1.50  (Smart TV)         [Ports: 8008]
│   └── 192.168.1.102 (MacBook Pro)      [Ports: 22]</code></pre>
                    </div>
                </section>

                <!-- SECURITY AUDIT -->
                <section id="security">
                    <h2>Security Audit & Risk Assessment</h2>
                    <p class="lead">Perform vulnerability checks, audit exposed services, check SSL validity, and calculate risk scores.</p>

                    <div class="code-block">
                        <div class="code-header"><span>Security Audit CLI</span><button class="copy-btn">Copy</button></div>
                        <pre><code class="language-bash"># Audit local network with console summary
python3 helpers/security.py --scan

# Generate visual HTML security report with charts
python3 helpers/security.py --scan --html --output security_audit.html

# Export structured JSON security findings
python3 helpers/security.py --scan --json --output audit_findings.json</code></pre>
                    </div>

                    <h3>Risk Checks Performed</h3>
                    <ul>
                        <li>🔴 <strong>Critical:</strong> Unencrypted Telnet (23), open remote shells (512-514), exposed unauthenticated databases (Redis 6379, MongoDB 27017, Elasticsearch 9200), vulnerable SMB v1.</li>
                        <li>🟠 <strong>High:</strong> Cleartext FTP (21), POP3 (110), IMAP (143), exposed internal databases (MySQL 3306, Postgres 5432, MSSQL 1433), exposed VNC (5900) or RDP (3389).</li>
                        <li>🟡 <strong>Medium:</strong> Unencrypted HTTP (80) on management interfaces, open mail relays (25).</li>
                        <li>🔵 <strong>Low / Info:</strong> Expiring SSL/TLS certificates, missing security headers (HSTS, CSP, X-Frame-Options).</li>
                    </ul>
                </section>

                <!-- WAKE-ON-LAN -->
                <section id="wol">
                    <h2>Wake-on-LAN (WoL)</h2>
                    <p class="lead">Wake sleeping computers and servers remotely using magic UDP packets with favorites management.</p>

                    <div class="code-block">
                        <div class="code-header"><span>Wake-on-LAN CLI</span><button class="copy-btn">Copy</button></div>
                        <pre><code class="language-bash"># Wake device by MAC address
python3 helpers/wol.py --mac 00:11:22:33:44:55

# Send to custom broadcast subnet
python3 helpers/wol.py --mac 00:11:22:33:44:55 --broadcast 192.168.1.255

# Save to favorites list
python3 helpers/wol.py --add-favorite "Workstation" --mac 00:11:22:33:44:55 --ip 192.168.1.50

# Wake saved favorite by name
python3 helpers/wol.py --wake "Workstation"

# Wake and verify with ping confirmation
python3 helpers/wol.py --wake "Workstation" --verify --timeout 60</code></pre>
                    </div>
                </section>

                <!-- SCHEDULED SCANS -->
                <section id="scheduler">
                    <h2>Scheduled Scans</h2>
                    <p class="lead">Automate routine network scans using standard system daemons (cron on Linux, launchd on macOS).</p>

                    <div class="code-block">
                        <div class="code-header"><span>Scheduler CLI</span><button class="copy-btn">Copy</button></div>
                        <pre><code class="language-bash"># Create daily scan job with email notification on network changes
python3 helpers/scheduler.py --create daily_check \
    --schedule daily \
    --notify admin@example.com \
    --notify-on changes

# Weekly full scan generating HTML report
python3 helpers/scheduler.py --create weekly_audit \
    --schedule weekly \
    --scan-type full \
    --format html

# List and manage active jobs
python3 helpers/scheduler.py --list
python3 helpers/scheduler.py --run daily_check    # Run immediately
python3 helpers/scheduler.py --remove daily_check # Delete job</code></pre>
                    </div>
                </section>

                <!-- EXPORT & REPORTS -->
                <section id="export">
                    <h2>Export & Reports</h2>
                    <p class="lead">Generate spreadsheets, JSON datasets, styled HTML pages, and PDF summary reports with charts.</p>

                    <div class="code-block">
                        <div class="code-header"><span>Export Formats</span><button class="copy-btn">Copy</button></div>
                        <pre><code class="language-bash"># Export to spreadsheet CSV
python3 helpers/export.py --format csv --input scan.json --output devices.csv

# Generate interactive HTML report
python3 helpers/export.py --format html --input scan.json --output report.html

# Generate PDF report (requires reportlab)
python3 helpers/report_generator.py scan.json --pdf --output network_report.pdf

# Diff two scans to see new and departed devices
python3 helpers/report_generator.py current.json --compare previous.json --html > diff.html</code></pre>
                    </div>
                </section>

                <!-- CONFIGURATION -->
                <section id="configuration">
                    <h2>Configuration</h2>
                    <p class="lead">Customize default directories, timeouts, thread counts, and network profiles.</p>

                    <h3>Configuration File (<code>~/.netscan/config.json</code>)</h3>
                    <div class="code-block">
                        <pre><code class="language-json">{
  "default_interface": "auto",
  "default_target": "auto",
  "scan_timeout": 3,
  "threads": 50,
  "cache_expiry_days": 30,
  "web_port": 8080,
  "web_bind": "127.0.0.1",
  "notifications": true
}</code></pre>
                    </div>

                    <h3>Environment Variables</h3>
                    <table class="data-table" style="width:100%; border-collapse:collapse;">
                        <thead>
                            <tr style="border-bottom:2px solid var(--color-border);">
                                <th style="text-align:left; padding:8px;">Variable</th>
                                <th style="text-align:left; padding:8px;">Default</th>
                                <th style="text-align:left; padding:8px;">Description</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr style="border-bottom:1px solid var(--color-border);"><td><code>NETSCAN_DATA_DIR</code></td><td><code>~/.local/share/netscan</code></td><td>Base directory for logs, cache, exports</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td><code>NETSCAN_TIMEOUT</code></td><td><code>3</code></td><td>Socket timeout in seconds</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td><code>DEBUG</code></td><td><code>0</code></td><td>Set to <code>1</code> for detailed debug logging</td></tr>
                        </tbody>
                    </table>
                </section>

                <!-- PYTHON API REFERENCE -->
                <section id="api">
                    <h2>Python API Reference</h2>
                    <p class="lead">Embed NetScan's core discovery, auditing, and normalization modules directly into your Python tools.</p>

                    <div class="code-block">
                        <div class="code-header"><span>Async Scanner API</span><button class="copy-btn">Copy</button></div>
                        <pre><code class="language-python">import asyncio
from helpers.async_scanner import AsyncScanner

async def run_discovery():
    scanner = AsyncScanner(timeout=1.0, max_concurrent=100)
    # Expand subnet and scan
    hosts = scanner.expand_cidr("192.168.1.0/24")
    devices = await scanner.scan_hosts(hosts)
    for dev in devices:
        print(f"Host: {dev.ip} | MAC: {dev.mac} | Vendor: {dev.vendor}")

asyncio.run(run_discovery())</code></pre>
                    </div>

                    <div class="code-block">
                        <div class="code-header"><span>Vendor Cache API</span><button class="copy-btn">Copy</button></div>
                        <pre><code class="language-python">from helpers.vendor_cache import VendorCache

cache = VendorCache()
# Resolves from local SQLite if available, otherwise queries macvendors.com
vendor = cache.get("00:50:56:C0:00:08")
print(f"Vendor: {vendor}") # VMware, Inc.</code></pre>
                    </div>

                    <div class="code-block">
                        <div class="code-header"><span>Security Auditor API</span><button class="copy-btn">Copy</button></div>
                        <pre><code class="language-python">from helpers.security import SecurityAuditor

auditor = SecurityAuditor(timeout=3.0)
findings = auditor.audit_host("192.168.1.1")
for f in findings:
    print(f"[{f.severity.upper()}] {f.title}: {f.recommendation}")</code></pre>
                    </div>
                </section>

                <!-- RUST PERFORMANCE CORE -->
                <section id="performance">
                    <h2>Rust Performance Core</h2>
                    <p class="lead">NetScan includes an optional Rust C-extension (<code>netscan_core</code> via PyO3) that accelerates CPU-intensive operations by 10–100x.</p>

                    <table class="data-table" style="width:100%; border-collapse:collapse; margin-bottom:20px;">
                        <thead>
                            <tr style="border-bottom:2px solid var(--color-border);">
                                <th style="text-align:left; padding:8px;">Operation</th>
                                <th style="text-align:left; padding:8px;">Pure Python</th>
                                <th style="text-align:left; padding:8px;">Rust Core</th>
                                <th style="text-align:left; padding:8px;">Speedup</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr style="border-bottom:1px solid var(--color-border);"><td>MAC normalization (1,000 MACs)</td><td>~50 ms</td><td>~0.5 ms</td><td><strong>100x</strong></td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td>CIDR expansion (/16 = 65,534 IPs)</td><td>~200 ms</td><td>~5 ms</td><td><strong>40x</strong></td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td>OUI database file parsing (30k entries)</td><td>~500 ms</td><td>~10 ms</td><td><strong>50x</strong></td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td>TCP connect scan (254 hosts, 10 ports)</td><td>~30 s</td><td>~3 s</td><td><strong>10x</strong></td></tr>
                        </tbody>
                    </table>

                    <div class="code-block">
                        <div class="code-header"><span>Build Rust Module</span><button class="copy-btn">Copy</button></div>
                        <pre><code class="language-bash"># Compile and link Rust performance module
./build_rust.sh

# Verify acceleration status
python3 helpers/fast_core.py</code></pre>
                    </div>
                </section>

                <!-- DOCKER DEPLOYMENT -->
                <section id="docker">
                    <h2>Docker Deployment</h2>
                    <p class="lead">Run NetScan in a contained environment with all dependencies pre-installed.</p>

                    <div class="code-block">
                        <div class="code-header"><span>Docker Commands</span><button class="copy-btn">Copy</button></div>
                        <pre><code class="language-bash"># Run interactive CLI container with host networking
docker run --rm -it --network host --cap-add NET_RAW netscan

# Run background web interface on port 8080
docker run -d --name netscan-web -p 8080:8080 --network host --cap-add NET_RAW netscan -w

# Using Docker Compose
docker compose up -d</code></pre>
                    </div>
                </section>

                <!-- CLI REFERENCE -->
                <section id="cli-reference">
                    <h2>Complete CLI Reference</h2>
                    <p class="lead">Reference of all flags and options supported by the <code>netscan</code> binary.</p>

                    <table class="data-table" style="width:100%; border-collapse:collapse; margin-bottom:20px;">
                        <thead>
                            <tr style="border-bottom:2px solid var(--color-border);">
                                <th style="text-align:left; padding:8px;">Flag</th>
                                <th style="text-align:left; padding:8px;">Argument</th>
                                <th style="text-align:left; padding:8px;">Description</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr style="border-bottom:1px solid var(--color-border);"><td><code>-s, --scan</code></td><td><em>None</em></td><td>Perform quick network sweep</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td><code>-f, --full</code></td><td><em>None</em></td><td>Full port scan on active hosts</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td><code>-l, --lookup</code></td><td><code>&lt;MAC&gt;</code></td><td>Lookup vendor for specified MAC address</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td><code>-b, --batch</code></td><td><code>&lt;FILE&gt;</code></td><td>Batch lookup MACs from file</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td><code>-m, --monitor</code></td><td><em>None</em></td><td>Start continuous real-time monitor</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td><code>-w, --web</code></td><td><em>None</em></td><td>Launch web interface and REST API</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td><code>-t, --target</code></td><td><code>&lt;CIDR/IP&gt;</code></td><td>Specify target network (e.g. <code>192.168.1.0/24</code>)</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td><code>-i, --interface</code></td><td><code>&lt;IFACE&gt;</code></td><td>Network interface to use (e.g. <code>en0</code>, <code>eth0</code>)</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td><code>-o, --output</code></td><td><code>&lt;FILE&gt;</code></td><td>Save results to file</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td><code>--json</code></td><td><em>None</em></td><td>Format output as JSON</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td><code>--csv</code></td><td><em>None</em></td><td>Format output as CSV</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td><code>-v, --verbose</code></td><td><em>None</em></td><td>Enable verbose diagnostic output</td></tr>
                            <tr style="border-bottom:1px solid var(--color-border);"><td><code>-h, --help</code></td><td><em>None</em></td><td>Show usage help</td></tr>
                        </tbody>
                    </table>
                </section>

                <!-- TROUBLESHOOTING -->
                <section id="troubleshooting">
                    <h2>Troubleshooting & FAQ</h2>
                    <p class="lead">Solutions for common issues and environment configurations.</p>

                    <h4>Permission Denied during ARP / Raw Sockets</h4>
                    <p>Raw socket discovery and Layer 2 ARP scanning require root privileges on Linux and macOS:</p>
                    <div class="code-block">
                        <pre><code class="language-bash">sudo netscan -s</code></pre>
                    </div>

                    <h4>Python ModuleNotFoundError</h4>
                    <p>If optional Python helpers indicate missing packages:</p>
                    <div class="code-block">
                        <pre><code class="language-bash">pip3 install --user requests reportlab matplotlib</code></pre>
                    </div>

                    <h4>macOS BSD vs GNU Tools</h4>
                    <p>NetScan v3.0.0 is engineered to be 100% compatible with macOS default BSD utilities (<code>sed</code>, <code>awk</code>, <code>grep</code>) and Bash 3.2. No GNU coreutils or Bash 4+ upgrades are required.</p>
                </section>

                <!-- CHANGELOG -->
                <section id="changelog">
                    <h2>Changelog</h2>
                    <ul>
                        <li><strong>v3.0.0:</strong> Desktop GUI Application (Electron 28), macOS & Windows native installers, Bash 3.2 compatibility, <code>~/.netscan</code> config directory.</li>
                        <li><strong>v2.1.0:</strong> Device fingerprinting, Wake-on-LAN, Network topology mapping, Security audit module, cron/launchd scheduler, and desktop notifications.</li>
                        <li><strong>v2.0.0:</strong> Python Async Network Scanner (<code>async_scanner.py</code>), SQLite vendor cache, multi-file merging.</li>
                        <li><strong>v1.0.0:</strong> Initial interactive Bash CLI, XML/ARP/CSV/JSON parsers, and online vendor lookup.</li>
                    </ul>
                </section>

                <!-- CONTRIBUTING -->
                <section id="contributing">
                    <h2>Contributing</h2>
                    <p>Contributions are welcome! Please open issues or pull requests on <a href="https://github.com/G1A1B1E/NetScan" target="_blank">GitHub</a>.</p>
                </section>

            </article>

            <!-- Footer -->
            <footer class="doc-footer" style="padding:40px var(--spacing-2xl); border-top:1px solid var(--color-border); margin-top:60px;">
                <div class="footer-meta" style="text-align:center;">
                    <p>© 2026 NetScan. Released under the MIT License.</p>
                    <p>
                        <a href="https://github.com/G1A1B1E/NetScan">GitHub</a> · 
                        <a href="https://github.com/G1A1B1E/NetScan/issues">Report Issue</a> · 
                        <a href="#overview">Back to Top ↑</a>
                    </p>
                </div>
            </footer>
        </main>
    </div>
`;
