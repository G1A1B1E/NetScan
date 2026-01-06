<#
.SYNOPSIS
    NetScan - Network Discovery & MAC Lookup Tool for Windows
.DESCRIPTION
    Discover devices on your network, look up MAC address vendors, and monitor network changes.
.PARAMETER Lookup
    Look up vendor for a MAC address
.PARAMETER Scan
    Perform a quick network scan
.PARAMETER Full
    Perform a full scan with port detection
.PARAMETER Monitor
    Start network monitoring
.PARAMETER Web
    Start web interface
.PARAMETER Target
    Target network (e.g., 192.168.1.0/24)
.PARAMETER Interface
    Network interface to use
.PARAMETER Output
    Output file path
.PARAMETER Json
    Output in JSON format
.PARAMETER Csv
    Output in CSV format
.PARAMETER Port
    Web server port (default: 8080)
.PARAMETER UpdateOui
    Update OUI database
.PARAMETER Version
    Show version
.EXAMPLE
    .\netscan.ps1 -Lookup "00:50:56:C0:00:08"
.EXAMPLE
    .\netscan.ps1 -Scan
.EXAMPLE
    .\netscan.ps1 -Scan -Target "192.168.1.0/24" -Json
#>

[CmdletBinding(DefaultParameterSetName='Menu')]
param(
    [Parameter(ParameterSetName='Lookup')]
    [Alias("l")]
    [string]$Lookup,

    [Parameter(ParameterSetName='Scan')]
    [Alias("s")]
    [switch]$Scan,

    [Parameter(ParameterSetName='Full')]
    [Alias("f")]
    [switch]$Full,

    [Parameter(ParameterSetName='Monitor')]
    [Alias("m")]
    [switch]$Monitor,

    [Parameter(ParameterSetName='Web')]
    [Alias("w")]
    [switch]$Web,

    [Parameter(ParameterSetName='Batch')]
    [Alias("b")]
    [string]$Batch,

    [Alias("t")]
    [string]$Target,

    [Alias("i")]
    [string]$Interface,

    [Alias("o")]
    [string]$Output,

    [switch]$Json,
    [switch]$Csv,

    [Alias("p")]
    [int]$Port = 8080,

    [switch]$UpdateOui,
    [switch]$Version,
    [switch]$Help,

    [Alias("v")]
    [switch]$Verbose
)

# Script configuration
$script:NETSCAN_VERSION = "2.0.0"
$script:NETSCAN_HOME = if ($env:NETSCAN_HOME) { $env:NETSCAN_HOME } else { "$env:LOCALAPPDATA\NetScan" }
$script:SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$script:PYTHON = "python"

# Colors for output
$script:Colors = @{
    Success = "Green"
    Error = "Red"
    Warning = "Yellow"
    Info = "Cyan"
    Muted = "Gray"
}

function Write-Banner {
    $banner = @"

    _   __     __  _____                
   / | / /__  / /_/ ___/_________ _____ 
  /  |/ / _ \/ __/\__ \/ ___/ __ `/ __ \
 / /|  /  __/ /_ ___/ / /__/ /_/ / / / /
/_/ |_/\___/\__//____/\___/\__,_/_/ /_/ 
                                        
    Network Discovery & MAC Lookup Tool
    Windows Edition v$script:NETSCAN_VERSION

"@
    Write-Host $banner -ForegroundColor Cyan
}

function Write-Status {
    param([string]$Message, [string]$Type = "Info")
    $color = $script:Colors[$Type]
    $prefix = switch ($Type) {
        "Success" { "[+]" }
        "Error"   { "[-]" }
        "Warning" { "[!]" }
        default   { "[*]" }
    }
    Write-Host "$prefix $Message" -ForegroundColor $color
}

function Test-PythonInstalled {
    try {
        $null = & $script:PYTHON --version 2>&1
        return $true
    } catch {
        return $false
    }
}

function Test-Administrator {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Get-NetworkInterfaces {
    Get-NetAdapter | Where-Object { $_.Status -eq "Up" } | ForEach-Object {
        [PSCustomObject]@{
            Name = $_.Name
            Description = $_.InterfaceDescription
            MacAddress = $_.MacAddress
            Status = $_.Status
            Speed = "$([math]::Round($_.LinkSpeed / 1GB, 1)) Gbps"
        }
    }
}

function Get-LocalNetworkInfo {
    $adapter = Get-NetAdapter | Where-Object { $_.Status -eq "Up" } | Select-Object -First 1
    if (-not $adapter) {
        return $null
    }
    
    $ipConfig = Get-NetIPAddress -InterfaceIndex $adapter.ifIndex -AddressFamily IPv4 | Select-Object -First 1
    if (-not $ipConfig) {
        return $null
    }
    
    $ip = $ipConfig.IPAddress
    $prefix = $ipConfig.PrefixLength
    
    # Calculate network address
    $ipBytes = [System.Net.IPAddress]::Parse($ip).GetAddressBytes()
    $maskBytes = @(0,0,0,0)
    for ($i = 0; $i -lt $prefix; $i++) {
        $maskBytes[[math]::Floor($i/8)] = $maskBytes[[math]::Floor($i/8)] -bor (128 -shr ($i % 8))
    }
    
    $networkBytes = @()
    for ($i = 0; $i -lt 4; $i++) {
        $networkBytes += $ipBytes[$i] -band $maskBytes[$i]
    }
    
    $network = ($networkBytes -join ".") + "/$prefix"
    
    return @{
        Interface = $adapter.Name
        IP = $ip
        Network = $network
        Gateway = (Get-NetRoute -InterfaceIndex $adapter.ifIndex -DestinationPrefix "0.0.0.0/0" -ErrorAction SilentlyContinue).NextHop
    }
}

function Invoke-MacLookup {
    param([string]$MacAddress)
    
    # Try Python helper first
    $pythonScript = Join-Path $script:SCRIPT_DIR "helpers\mac_lookup.py"
    if (Test-Path $pythonScript) {
        & $script:PYTHON $pythonScript --lookup $MacAddress
        return
    }
    
    # Fallback to built-in lookup
    $mac = $MacAddress.ToUpper() -replace '[:-]', '' -replace '(.{2})', '$1:' -replace ':$', ''
    $oui = $mac.Substring(0, 8)
    
    # Check local OUI database
    $ouiFile = Join-Path $script:NETSCAN_HOME "data\oui.txt"
    if (Test-Path $ouiFile) {
        $searchOui = $oui -replace ':', '-'
        $match = Select-String -Path $ouiFile -Pattern "^$searchOui" -SimpleMatch | Select-Object -First 1
        if ($match) {
            $vendor = ($match.Line -split '\t')[-1].Trim()
            Write-Host ""
            Write-Host "MAC Address: $mac" -ForegroundColor White
            Write-Host "Vendor: $vendor" -ForegroundColor Green
            Write-Host "OUI: $oui" -ForegroundColor Gray
            return
        }
    }
    
    Write-Host ""
    Write-Host "MAC Address: $mac" -ForegroundColor White
    Write-Host "Vendor: Unknown" -ForegroundColor Yellow
}

function Invoke-NetworkScan {
    param(
        [string]$TargetNetwork,
        [switch]$FullScan,
        [switch]$JsonOutput,
        [switch]$CsvOutput
    )
    
    # Try Python helper first
    $pythonScript = Join-Path $script:SCRIPT_DIR "helpers\scanner.py"
    if (Test-Path $pythonScript) {
        $args = @($pythonScript)
        if ($FullScan) { $args += "--full" } else { $args += "--scan" }
        if ($TargetNetwork) { $args += "--target", $TargetNetwork }
        if ($JsonOutput) { $args += "--json" }
        if ($CsvOutput) { $args += "--csv" }
        & $script:PYTHON @args
        return
    }
    
    # Fallback to native Windows scanning
    Write-Status "Starting network scan..." "Info"
    
    if (-not $TargetNetwork) {
        $netInfo = Get-LocalNetworkInfo
        if ($netInfo) {
            $TargetNetwork = $netInfo.Network
            Write-Status "Auto-detected network: $TargetNetwork" "Info"
        } else {
            Write-Status "Could not detect network. Please specify -Target" "Error"
            return
        }
    }
    
    Write-Host ""
    Write-Host "Scanning $TargetNetwork..." -ForegroundColor Cyan
    Write-Host ""
    
    # Get ARP table
    $arpOutput = & arp -a 2>&1
    $devices = @()
    
    foreach ($line in $arpOutput) {
        if ($line -match '^\s*(\d+\.\d+\.\d+\.\d+)\s+([\da-f-]+)\s+(\w+)') {
            $ip = $matches[1]
            $mac = $matches[2].ToUpper() -replace '-', ':'
            $type = $matches[3]
            
            if ($mac -ne "FF:FF:FF:FF:FF:FF" -and $type -eq "dynamic") {
                # Look up vendor
                $vendor = "Unknown"
                $oui = $mac.Substring(0, 8) -replace ':', '-'
                $ouiFile = Join-Path $script:NETSCAN_HOME "data\oui.txt"
                if (Test-Path $ouiFile) {
                    $match = Select-String -Path $ouiFile -Pattern "^$oui" -SimpleMatch | Select-Object -First 1
                    if ($match) {
                        $vendor = ($match.Line -split '\t')[-1].Trim()
                        if ($vendor.Length -gt 25) { $vendor = $vendor.Substring(0, 22) + "..." }
                    }
                }
                
                # Try to resolve hostname
                $hostname = "-"
                try {
                    $dns = [System.Net.Dns]::GetHostEntry($ip)
                    $hostname = $dns.HostName
                    if ($hostname.Length -gt 20) { $hostname = $hostname.Substring(0, 17) + "..." }
                } catch {}
                
                $devices += [PSCustomObject]@{
                    IP = $ip
                    MAC = $mac
                    Hostname = $hostname
                    Vendor = $vendor
                }
            }
        }
    }
    
    # Output results
    if ($JsonOutput) {
        $output = @{
            scan_info = @{
                timestamp = (Get-Date -Format "o")
                target = $TargetNetwork
                scan_type = if ($FullScan) { "full" } else { "quick" }
            }
            devices = $devices
            summary = @{
                total_devices = $devices.Count
            }
        }
        $output | ConvertTo-Json -Depth 10
    }
    elseif ($CsvOutput) {
        $devices | ConvertTo-Csv -NoTypeInformation
    }
    else {
        # Table output
        Write-Host ("IP Address".PadRight(16) + "MAC Address".PadRight(20) + "Hostname".PadRight(22) + "Vendor") -ForegroundColor White
        Write-Host ("-" * 80) -ForegroundColor Gray
        
        foreach ($device in $devices | Sort-Object { [version]($_.IP -replace '(\d+)', '00$1' -replace '0*(\d{3})', '$1') }) {
            Write-Host ($device.IP.PadRight(16)) -NoNewline -ForegroundColor Cyan
            Write-Host ($device.MAC.PadRight(20)) -NoNewline -ForegroundColor Yellow
            Write-Host ($device.Hostname.PadRight(22)) -NoNewline -ForegroundColor Gray
            Write-Host $device.Vendor -ForegroundColor Green
        }
        
        Write-Host ""
        Write-Host "Found $($devices.Count) devices" -ForegroundColor White
    }
}

function Invoke-NetworkMonitor {
    param([string]$TargetNetwork)
    
    Write-Status "Starting network monitor..." "Info"
    Write-Status "Press Ctrl+C to stop" "Info"
    Write-Host ""
    
    $knownDevices = @{}
    
    while ($true) {
        $arpOutput = & arp -a 2>&1
        $currentDevices = @{}
        
        foreach ($line in $arpOutput) {
            if ($line -match '^\s*(\d+\.\d+\.\d+\.\d+)\s+([\da-f-]+)\s+dynamic') {
                $ip = $matches[1]
                $mac = $matches[2].ToUpper()
                if ($mac -ne "FF-FF-FF-FF-FF-FF") {
                    $currentDevices[$mac] = $ip
                }
            }
        }
        
        # Check for new devices
        foreach ($mac in $currentDevices.Keys) {
            if (-not $knownDevices.ContainsKey($mac)) {
                $ip = $currentDevices[$mac]
                $timestamp = Get-Date -Format "HH:mm:ss"
                Write-Host "[$timestamp] " -NoNewline -ForegroundColor Gray
                Write-Host "NEW: " -NoNewline -ForegroundColor Green
                Write-Host "$ip ($($mac -replace '-', ':'))" -ForegroundColor White
            }
        }
        
        # Check for offline devices
        foreach ($mac in $knownDevices.Keys) {
            if (-not $currentDevices.ContainsKey($mac)) {
                $ip = $knownDevices[$mac]
                $timestamp = Get-Date -Format "HH:mm:ss"
                Write-Host "[$timestamp] " -NoNewline -ForegroundColor Gray
                Write-Host "OFFLINE: " -NoNewline -ForegroundColor Red
                Write-Host "$ip ($($mac -replace '-', ':'))" -ForegroundColor White
            }
        }
        
        $knownDevices = $currentDevices.Clone()
        Start-Sleep -Seconds 30
    }
}

function Start-WebInterface {
    param([int]$WebPort = 8080)
    
    $pythonScript = Join-Path $script:SCRIPT_DIR "helpers\web_server.py"
    if (Test-Path $pythonScript) {
        Write-Status "Starting web interface on http://localhost:$WebPort" "Info"
        & $script:PYTHON $pythonScript --port $WebPort
    } else {
        Write-Status "Web server module not found" "Error"
    }
}

function Update-OuiDatabase {
    Write-Status "Updating OUI database..." "Info"
    
    $dataDir = Join-Path $script:NETSCAN_HOME "data"
    if (-not (Test-Path $dataDir)) {
        New-Item -ItemType Directory -Path $dataDir -Force | Out-Null
    }
    
    $ouiUrl = "http://standards-oui.ieee.org/oui/oui.txt"
    $ouiFile = Join-Path $dataDir "oui.txt"
    
    try {
        Write-Status "Downloading from IEEE..." "Info"
        Invoke-WebRequest -Uri $ouiUrl -OutFile $ouiFile -UseBasicParsing
        $size = (Get-Item $ouiFile).Length / 1MB
        Write-Status "Downloaded OUI database ($([math]::Round($size, 1)) MB)" "Success"
    } catch {
        Write-Status "Failed to download OUI database: $_" "Error"
    }
}

function Show-Menu {
    Write-Banner
    
    while ($true) {
        Write-Host ""
        Write-Host "  1) MAC Address Lookup        - Look up vendor by MAC address" -ForegroundColor White
        Write-Host "  2) Scan Network (Quick)      - Fast network discovery" -ForegroundColor White
        Write-Host "  3) Scan Network (Full)       - Deep scan with ports" -ForegroundColor White
        Write-Host "  4) View Network Interfaces   - Show available interfaces" -ForegroundColor White
        Write-Host "  5) Monitor Network           - Real-time monitoring" -ForegroundColor White
        Write-Host "  6) Export Results            - Export to file" -ForegroundColor White
        Write-Host "  7) Start Web Interface       - Launch browser UI" -ForegroundColor White
        Write-Host "  8) Update OUI Database       - Download latest vendor data" -ForegroundColor White
        Write-Host "  9) Settings                  - Configure NetScan" -ForegroundColor White
        Write-Host "  0) Exit" -ForegroundColor White
        Write-Host ""
        
        $choice = Read-Host "Enter choice"
        
        switch ($choice) {
            "1" {
                $mac = Read-Host "Enter MAC address"
                if ($mac) { Invoke-MacLookup -MacAddress $mac }
            }
            "2" { Invoke-NetworkScan }
            "3" { Invoke-NetworkScan -FullScan }
            "4" {
                Write-Host ""
                Get-NetworkInterfaces | Format-Table -AutoSize
            }
            "5" { Invoke-NetworkMonitor }
            "6" {
                $file = Read-Host "Enter output filename"
                if ($file) { Invoke-NetworkScan -JsonOutput | Out-File $file }
                Write-Status "Saved to $file" "Success"
            }
            "7" { Start-WebInterface -WebPort $Port }
            "8" { Update-OuiDatabase }
            "9" {
                Write-Host ""
                Write-Host "NETSCAN_HOME: $script:NETSCAN_HOME" -ForegroundColor Cyan
                Write-Host "Script Dir: $script:SCRIPT_DIR" -ForegroundColor Cyan
                Write-Host "Python: $script:PYTHON" -ForegroundColor Cyan
            }
            "0" { 
                Write-Host "Goodbye!" -ForegroundColor Cyan
                return 
            }
        }
    }
}

function Show-Help {
    Write-Banner
    Write-Host "USAGE:" -ForegroundColor Yellow
    Write-Host "    .\netscan.ps1 [OPTIONS]" -ForegroundColor White
    Write-Host ""
    Write-Host "OPTIONS:" -ForegroundColor Yellow
    Write-Host "    -Lookup, -l <MAC>     Look up vendor for MAC address" -ForegroundColor White
    Write-Host "    -Scan, -s             Quick network scan" -ForegroundColor White
    Write-Host "    -Full, -f             Full scan with port detection" -ForegroundColor White
    Write-Host "    -Monitor, -m          Start network monitoring" -ForegroundColor White
    Write-Host "    -Web, -w              Start web interface" -ForegroundColor White
    Write-Host "    -Batch, -b <FILE>     Batch MAC lookup from file" -ForegroundColor White
    Write-Host "    -Target, -t <NET>     Target network (e.g., 192.168.1.0/24)" -ForegroundColor White
    Write-Host "    -Interface, -i <IF>   Network interface" -ForegroundColor White
    Write-Host "    -Output, -o <FILE>    Output file" -ForegroundColor White
    Write-Host "    -Json                 Output in JSON format" -ForegroundColor White
    Write-Host "    -Csv                  Output in CSV format" -ForegroundColor White
    Write-Host "    -Port, -p <PORT>      Web server port (default: 8080)" -ForegroundColor White
    Write-Host "    -UpdateOui            Update OUI database" -ForegroundColor White
    Write-Host "    -Version              Show version" -ForegroundColor White
    Write-Host "    -Help                 Show this help" -ForegroundColor White
    Write-Host ""
    Write-Host "EXAMPLES:" -ForegroundColor Yellow
    Write-Host "    .\netscan.ps1 -l 00:50:56:C0:00:08" -ForegroundColor Gray
    Write-Host "    .\netscan.ps1 -Scan" -ForegroundColor Gray
    Write-Host "    .\netscan.ps1 -Scan -Target 192.168.1.0/24 -Json" -ForegroundColor Gray
    Write-Host "    .\netscan.ps1 -Full -Output results.json" -ForegroundColor Gray
    Write-Host ""
}

# Main execution
if ($Version) {
    Write-Host "NetScan v$script:NETSCAN_VERSION (Windows)" -ForegroundColor Cyan
    exit 0
}

if ($Help) {
    Show-Help
    exit 0
}

if ($UpdateOui) {
    Update-OuiDatabase
    exit 0
}

if ($Lookup) {
    Invoke-MacLookup -MacAddress $Lookup
    exit 0
}

if ($Scan) {
    Invoke-NetworkScan -TargetNetwork $Target -JsonOutput:$Json -CsvOutput:$Csv
    exit 0
}

if ($Full) {
    Invoke-NetworkScan -TargetNetwork $Target -FullScan -JsonOutput:$Json -CsvOutput:$Csv
    exit 0
}

if ($Monitor) {
    Invoke-NetworkMonitor -TargetNetwork $Target
    exit 0
}

if ($Web) {
    Start-WebInterface -WebPort $Port
    exit 0
}

if ($Batch) {
    if (Test-Path $Batch) {
        Get-Content $Batch | ForEach-Object {
            if ($_.Trim()) {
                Invoke-MacLookup -MacAddress $_.Trim()
            }
        }
    } else {
        Write-Status "File not found: $Batch" "Error"
    }
    exit 0
}

# Default: show interactive menu
Show-Menu
