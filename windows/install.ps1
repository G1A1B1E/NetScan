#Requires -Version 5.1
<#
.SYNOPSIS
    NetScan Windows Installer

.DESCRIPTION
    Installs NetScan to your Windows system with all dependencies.
    Run as Administrator for system-wide installation, or as regular user for user-only install.

.PARAMETER InstallPath
    Custom installation path (default: %LOCALAPPDATA%\NetScan or %ProgramFiles%\NetScan)

.PARAMETER SystemWide
    Install for all users (requires Administrator)

.PARAMETER Uninstall
    Remove NetScan from the system

.EXAMPLE
    .\install.ps1
    .\install.ps1 -SystemWide
    .\install.ps1 -Uninstall
#>

param(
    [string]$InstallPath,
    [switch]$SystemWide,
    [switch]$Uninstall
)

$ErrorActionPreference = "Stop"

# ========================
# Configuration
# ========================
$AppName = "NetScan"
$Version = "1.0.0"
$OuiUrl = "https://standards-oui.ieee.org/oui/oui.txt"
$GitHubRepo = "https://github.com/G1A1B1E/NetScan"

# Colors
function Write-Title { param($msg) Write-Host "`n=== $msg ===" -ForegroundColor Cyan }
function Write-Info { param($msg) Write-Host "[*] $msg" -ForegroundColor Blue }
function Write-Success { param($msg) Write-Host "[+] $msg" -ForegroundColor Green }
function Write-Warning { param($msg) Write-Host "[!] $msg" -ForegroundColor Yellow }
function Write-ErrorMsg { param($msg) Write-Host "[-] $msg" -ForegroundColor Red }

# ========================
# Check Admin Rights
# ========================
function Test-Administrator {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

$IsAdmin = Test-Administrator

# ========================
# Determine Install Path
# ========================
if (-not $InstallPath) {
    if ($SystemWide -and $IsAdmin) {
        $InstallPath = "$env:ProgramFiles\$AppName"
    } else {
        $InstallPath = "$env:LOCALAPPDATA\$AppName"
    }
}

# ========================
# Uninstall
# ========================
if ($Uninstall) {
    Write-Title "Uninstalling $AppName"
    
    # Remove from PATH
    $pathType = if ($IsAdmin) { "Machine" } else { "User" }
    $currentPath = [Environment]::GetEnvironmentVariable("Path", $pathType)
    if ($currentPath -like "*$InstallPath*") {
        $newPath = ($currentPath -split ';' | Where-Object { $_ -ne $InstallPath }) -join ';'
        [Environment]::SetEnvironmentVariable("Path", $newPath, $pathType)
        Write-Success "Removed from PATH"
    }
    
    # Remove installation directory
    if (Test-Path $InstallPath) {
        Remove-Item -Path $InstallPath -Recurse -Force
        Write-Success "Removed installation directory: $InstallPath"
    }
    
    Write-Success "$AppName has been uninstalled"
    exit 0
}

# ========================
# Banner
# ========================
Write-Host @"

  _   _      _   ____                  
 | \ | | ___| |_/ ___|  ___ __ _ _ __  
 |  \| |/ _ \ __\___ \ / __/ _` | '_ \ 
 | |\  |  __/ |_ ___) | (_| (_| | | | |
 |_| \_|\___|\__|____/ \___\__,_|_| |_|
                                       
       Windows Installer v$Version

"@ -ForegroundColor Cyan

Write-Info "Installation Path: $InstallPath"
Write-Info "Install Type: $(if ($SystemWide) { 'System-wide' } else { 'User-only' })"
Write-Info "Administrator: $(if ($IsAdmin) { 'Yes' } else { 'No' })"

if ($SystemWide -and -not $IsAdmin) {
    Write-ErrorMsg "System-wide installation requires Administrator privileges"
    Write-Info "Please run PowerShell as Administrator, or remove -SystemWide flag"
    exit 1
}

# ========================
# Check Prerequisites
# ========================
Write-Title "Checking Prerequisites"

# Python
$pythonCmd = $null
foreach ($cmd in @("python3", "python", "py")) {
    try {
        $version = & $cmd --version 2>&1
        if ($version -match "Python 3\.([0-9]+)") {
            if ([int]$matches[1] -ge 6) {
                $pythonCmd = $cmd
                Write-Success "Found $version"
                break
            }
        }
    } catch {}
}

if (-not $pythonCmd) {
    Write-ErrorMsg "Python 3.6+ is required but not found"
    Write-Info "Download from: https://www.python.org/downloads/"
    Write-Info "Make sure to check 'Add Python to PATH' during installation"
    
    $response = Read-Host "Would you like to open the Python download page? (y/n)"
    if ($response -eq 'y') {
        Start-Process "https://www.python.org/downloads/"
    }
    exit 1
}

# pip
try {
    & $pythonCmd -m pip --version | Out-Null
    Write-Success "pip is available"
} catch {
    Write-Warning "pip not found, attempting to install..."
    & $pythonCmd -m ensurepip --upgrade
}

# nmap (optional)
$hasNmap = $false
try {
    $nmapVersion = nmap --version 2>&1 | Select-Object -First 1
    Write-Success "Found $nmapVersion"
    $hasNmap = $true
} catch {
    Write-Warning "nmap not found (optional - enables advanced scanning)"
    Write-Info "Download from: https://nmap.org/download.html"
}

# ========================
# Create Directories
# ========================
Write-Title "Creating Directories"

$directories = @(
    $InstallPath,
    "$InstallPath\helpers",
    "$InstallPath\data",
    "$InstallPath\cache",
    "$InstallPath\logs"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Info "Created: $dir"
    }
}

# ========================
# Copy Files
# ========================
Write-Title "Installing Files"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Copy main scripts
$filesToCopy = @(
    "netscan.ps1",
    "netscan.bat"
)

foreach ($file in $filesToCopy) {
    $sourcePath = Join-Path $scriptDir $file
    if (Test-Path $sourcePath) {
        Copy-Item -Path $sourcePath -Destination $InstallPath -Force
        Write-Info "Installed: $file"
    }
}

# Copy helpers
$helpersDir = Join-Path $scriptDir "helpers"
if (Test-Path $helpersDir) {
    Copy-Item -Path "$helpersDir\*" -Destination "$InstallPath\helpers" -Force -Recurse
    Write-Info "Installed: Python helpers"
}

Write-Success "Files installed to $InstallPath"

# ========================
# Install Python Dependencies
# ========================
Write-Title "Installing Python Dependencies"

$requirements = @(
    "requests>=2.25.0",
    "flask>=2.0.0",
    "psutil>=5.8.0"
)

$requirementsFile = "$InstallPath\requirements.txt"
$requirements | Out-File -FilePath $requirementsFile -Encoding UTF8

Write-Info "Installing Python packages..."
& $pythonCmd -m pip install -r $requirementsFile --quiet --user

if ($LASTEXITCODE -eq 0) {
    Write-Success "Python dependencies installed"
} else {
    Write-Warning "Some Python dependencies may have failed to install"
}

# ========================
# Download OUI Database
# ========================
Write-Title "Downloading OUI Database"

$ouiPath = "$InstallPath\data\oui.txt"

if (Test-Path $ouiPath) {
    $age = (Get-Date) - (Get-Item $ouiPath).LastWriteTime
    if ($age.Days -lt 30) {
        Write-Info "OUI database is recent (${age.Days} days old), skipping download"
    } else {
        Write-Info "OUI database is ${age.Days} days old, updating..."
        $downloadOui = $true
    }
} else {
    $downloadOui = $true
}

if ($downloadOui) {
    Write-Info "Downloading from IEEE..."
    try {
        # Use TLS 1.2
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        
        $webClient = New-Object System.Net.WebClient
        $webClient.DownloadFile($OuiUrl, $ouiPath)
        
        $size = (Get-Item $ouiPath).Length / 1MB
        Write-Success "Downloaded OUI database (${size:N2} MB)"
    } catch {
        Write-Warning "Failed to download OUI database: $_"
        Write-Info "You can manually download from: $OuiUrl"
    }
}

# ========================
# Add to PATH
# ========================
Write-Title "Configuring PATH"

$pathType = if ($IsAdmin -and $SystemWide) { "Machine" } else { "User" }
$currentPath = [Environment]::GetEnvironmentVariable("Path", $pathType)

if ($currentPath -notlike "*$InstallPath*") {
    $newPath = "$currentPath;$InstallPath"
    [Environment]::SetEnvironmentVariable("Path", $newPath, $pathType)
    $env:Path = "$env:Path;$InstallPath"
    Write-Success "Added to PATH ($pathType)"
} else {
    Write-Info "Already in PATH"
}

# ========================
# Create Shortcut
# ========================
Write-Title "Creating Shortcuts"

try {
    $WshShell = New-Object -ComObject WScript.Shell
    
    # Desktop shortcut
    $shortcutPath = "$env:USERPROFILE\Desktop\NetScan.lnk"
    $shortcut = $WshShell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = "powershell.exe"
    $shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$InstallPath\netscan.ps1`" -Menu"
    $shortcut.WorkingDirectory = $InstallPath
    $shortcut.IconLocation = "shell32.dll,13"
    $shortcut.Description = "NetScan Network Tool"
    $shortcut.Save()
    Write-Success "Created desktop shortcut"
    
    # Start Menu shortcut
    $startMenuPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\NetScan.lnk"
    $shortcut = $WshShell.CreateShortcut($startMenuPath)
    $shortcut.TargetPath = "powershell.exe"
    $shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$InstallPath\netscan.ps1`" -Menu"
    $shortcut.WorkingDirectory = $InstallPath
    $shortcut.IconLocation = "shell32.dll,13"
    $shortcut.Description = "NetScan Network Tool"
    $shortcut.Save()
    Write-Success "Created Start Menu shortcut"
} catch {
    Write-Warning "Could not create shortcuts: $_"
}

# ========================
# Create config file
# ========================
$configPath = "$InstallPath\config.json"
if (-not (Test-Path $configPath)) {
    $config = @{
        version = $Version
        installed = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
        oui_path = "$InstallPath\data\oui.txt"
        cache_dir = "$InstallPath\cache"
        log_dir = "$InstallPath\logs"
        web_port = 5555
        scan_timeout = 30
        nmap_available = $hasNmap
    }
    $config | ConvertTo-Json | Out-File -FilePath $configPath -Encoding UTF8
    Write-Info "Created configuration file"
}

# ========================
# Completion
# ========================
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "NetScan has been installed to: $InstallPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "Usage:" -ForegroundColor Yellow
Write-Host "  netscan -Lookup 00:11:22:33:44:55    # Look up MAC vendor"
Write-Host "  netscan -Scan                        # Scan local network"
Write-Host "  netscan -Web                         # Start web interface"
Write-Host "  netscan -Menu                        # Interactive menu"
Write-Host "  netscan -Help                        # Show all options"
Write-Host ""

if (-not $hasNmap) {
    Write-Host "Tip: Install nmap for advanced scanning features" -ForegroundColor Yellow
    Write-Host "     https://nmap.org/download.html" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "NOTE: You may need to restart your terminal for PATH changes to take effect" -ForegroundColor Yellow
Write-Host ""

# Open new terminal option
$response = Read-Host "Would you like to open a new terminal with NetScan ready? (y/n)"
if ($response -eq 'y') {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$InstallPath'; Write-Host 'NetScan is ready! Type: netscan -Help' -ForegroundColor Green"
}
