#!/bin/bash
#
# NetScan Installer Builder
# Creates professional installers for macOS (.pkg) and Windows (.exe)
# with options to install GUI, CLI, or both
#
# Usage: ./build-installers.sh [version]
#

set -e

VERSION="${1:-2.1.0}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$SCRIPT_DIR/build"
OUTPUT_DIR="$SCRIPT_DIR/output"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

print_banner() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║     🔧 NetScan Installer Builder v${VERSION}                    ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
}

# Clean and create directories
setup_directories() {
    log "Setting up build directories..."
    rm -rf "$BUILD_DIR"
    mkdir -p "$BUILD_DIR"/{macos,windows}
    mkdir -p "$OUTPUT_DIR"
}

# Build macOS installer
build_macos_installer() {
    log "Building macOS installer..."
    
    local MAC_BUILD="$BUILD_DIR/macos"
    local PKG_ROOT="$MAC_BUILD/pkg-root"
    local SCRIPTS="$MAC_BUILD/scripts"
    local RESOURCES="$MAC_BUILD/resources"
    
    mkdir -p "$PKG_ROOT"/{cli,gui}
    mkdir -p "$SCRIPTS"/{cli,gui,combined}
    mkdir -p "$RESOURCES"
    
    # === Prepare CLI component ===
    log "Preparing CLI component..."
    mkdir -p "$PKG_ROOT/cli/usr/local/bin"
    mkdir -p "$PKG_ROOT/cli/usr/local/share/netscan"/{lib,helpers,data}
    
    # Copy CLI files
    cp "$PROJECT_ROOT/netscan" "$PKG_ROOT/cli/usr/local/bin/"
    cp -r "$PROJECT_ROOT/lib/"* "$PKG_ROOT/cli/usr/local/share/netscan/lib/"
    cp -r "$PROJECT_ROOT/helpers/"* "$PKG_ROOT/cli/usr/local/share/netscan/helpers/"
    cp "$PROJECT_ROOT/mac.xml" "$PKG_ROOT/cli/usr/local/share/netscan/data/" 2>/dev/null || true
    
    # Create CLI wrapper that points to installed location
    cat > "$PKG_ROOT/cli/usr/local/bin/netscan" << 'WRAPPER'
#!/bin/bash
# NetScan CLI Wrapper
export NETSCAN_HOME="/usr/local/share/netscan"
export NETSCAN_LIB="$NETSCAN_HOME/lib"
export NETSCAN_HELPERS="$NETSCAN_HOME/helpers"

# Source the main library
source "$NETSCAN_LIB/scanner.sh"

# Run main function
main "$@"
WRAPPER
    chmod +x "$PKG_ROOT/cli/usr/local/bin/netscan"
    
    # === Prepare GUI component ===
    log "Preparing GUI component..."
    if [[ -d "$PROJECT_ROOT/netscan-gui/dist/mac-arm64/NetScan.app" ]]; then
        cp -r "$PROJECT_ROOT/netscan-gui/dist/mac-arm64/NetScan.app" "$PKG_ROOT/gui/"
    elif [[ -d "$PROJECT_ROOT/netscan-gui/dist/mac/NetScan.app" ]]; then
        cp -r "$PROJECT_ROOT/netscan-gui/dist/mac/NetScan.app" "$PKG_ROOT/gui/"
    else
        warn "GUI app not found. Build with 'cd netscan-gui && npm run build:mac' first"
    fi
    
    # === Create postinstall scripts ===
    
    # CLI postinstall
    cat > "$SCRIPTS/cli/postinstall" << 'SCRIPT'
#!/bin/bash
chmod +x /usr/local/bin/netscan
chmod -R +x /usr/local/share/netscan/helpers/*.py
echo "NetScan CLI installed successfully!"
echo "Run 'netscan' to start."
exit 0
SCRIPT
    chmod +x "$SCRIPTS/cli/postinstall"
    
    # GUI postinstall  
    cat > "$SCRIPTS/gui/postinstall" << 'SCRIPT'
#!/bin/bash
# Remove quarantine attribute
xattr -dr com.apple.quarantine /Applications/NetScan.app 2>/dev/null || true
echo "NetScan GUI installed successfully!"
exit 0
SCRIPT
    chmod +x "$SCRIPTS/gui/postinstall"
    
    # === Create distribution XML ===
    cat > "$MAC_BUILD/distribution.xml" << DISTXML
<?xml version="1.0" encoding="utf-8"?>
<installer-gui-script minSpecVersion="2">
    <title>NetScan ${VERSION}</title>
    <organization>com.netscan</organization>
    <welcome file="welcome.html"/>
    <readme file="readme.html"/>
    <license file="license.html"/>
    <conclusion file="conclusion.html"/>
    <background file="background.png" alignment="bottomleft" scaling="none"/>
    
    <options customize="always" require-scripts="false" hostArchitectures="x86_64,arm64"/>
    
    <choices-outline>
        <line choice="cli"/>
        <line choice="gui"/>
    </choices-outline>
    
    <choice id="cli" 
            title="Command Line Tools" 
            description="Install the NetScan CLI for terminal-based network scanning. Includes all Python helpers and bash libraries."
            selected="true">
        <pkg-ref id="com.netscan.cli"/>
    </choice>
    
    <choice id="gui" 
            title="Desktop Application" 
            description="Install the NetScan GUI desktop application with modern interface, dashboard, and visual network tools."
            selected="true">
        <pkg-ref id="com.netscan.gui"/>
    </choice>
    
    <pkg-ref id="com.netscan.cli" 
             version="${VERSION}" 
             installKBytes="2048">
        NetScan-CLI.pkg
    </pkg-ref>
    
    <pkg-ref id="com.netscan.gui" 
             version="${VERSION}" 
             installKBytes="200000">
        NetScan-GUI.pkg
    </pkg-ref>
</installer-gui-script>
DISTXML

    # === Create installer resources ===
    
    # Welcome page
    cat > "$RESOURCES/welcome.html" << 'HTML'
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 20px; background: #ffffff; color: #1a1a2e; margin: 0; }
        h1 { font-size: 28px; margin-bottom: 10px; color: #1a1a2e; }
        .version { color: #228be6; font-size: 14px; font-weight: 500; }
        p { line-height: 1.6; color: #495057; }
        ul { padding-left: 20px; }
        li { margin: 8px 0; color: #495057; }
        strong { color: #1a1a2e; }
    </style>
</head>
<body>
    <h1>🔍 Welcome to NetScan</h1>
    <p class="version">Version 2.1.0 - Network Intelligence Suite</p>
    
    <p>NetScan is a powerful network discovery and monitoring tool that helps you:</p>
    
    <ul>
        <li>🔍 Discover all devices on your network</li>
        <li>📊 Monitor network activity in real-time</li>
        <li>🔒 Run security audits</li>
        <li>🏭 Identify device manufacturers</li>
        <li>🗺️ Visualize network topology</li>
        <li>⚡ Wake devices with Wake-on-LAN</li>
    </ul>
    
    <p>Click <strong>Continue</strong> to proceed with the installation.</p>
</body>
</html>
HTML

    # Readme page
    cat > "$RESOURCES/readme.html" << 'HTML'
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; padding: 20px; }
        h2 { color: #228be6; }
        .component { background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #228be6; }
        .component h3 { margin-top: 0; }
        code { background: #e9ecef; padding: 2px 6px; border-radius: 4px; font-size: 13px; }
    </style>
</head>
<body>
    <h2>Installation Components</h2>
    
    <div class="component">
        <h3>📟 Command Line Tools (CLI)</h3>
        <p>Terminal-based network scanner with full feature set:</p>
        <ul>
            <li>Network device discovery</li>
            <li>MAC address lookup</li>
            <li>Port scanning</li>
            <li>Export to CSV/JSON</li>
        </ul>
        <p>After installation, run <code>netscan</code> in Terminal.</p>
    </div>
    
    <div class="component">
        <h3>🖥️ Desktop Application (GUI)</h3>
        <p>Modern graphical interface with:</p>
        <ul>
            <li>Visual dashboard</li>
            <li>Network topology map</li>
            <li>Real-time monitoring</li>
            <li>Security audit tools</li>
            <li>Dark/Light themes</li>
        </ul>
        <p>Find <strong>NetScan</strong> in your Applications folder.</p>
    </div>
    
    <h2>System Requirements</h2>
    <ul>
        <li>macOS 10.13 (High Sierra) or later</li>
        <li>Python 3.6+ (for CLI helpers)</li>
        <li>Administrator privileges for network scanning</li>
    </ul>
</body>
</html>
HTML

    # License page
    cat > "$RESOURCES/license.html" << 'HTML'
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; padding: 20px; font-size: 12px; }
        h2 { color: #228be6; }
        pre { background: #f8f9fa; padding: 15px; border-radius: 8px; overflow-x: auto; font-size: 11px; }
    </style>
</head>
<body>
    <h2>MIT License</h2>
    <pre>
Copyright (c) 2026 G1A1B1E

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
    </pre>
</body>
</html>
HTML

    # Conclusion page
    cat > "$RESOURCES/conclusion.html" << 'HTML'
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; padding: 20px; background: #ffffff; color: #1a1a2e; margin: 0; }
        h1 { color: #40c057; }
        .success { background: #d3f9d8; border: 1px solid #40c057; padding: 20px; border-radius: 8px; margin: 20px 0; }
        code { background: #e9ecef; padding: 4px 8px; border-radius: 4px; color: #1a1a2e; }
        a { color: #228be6; }
        h3 { color: #1a1a2e; }
        p { color: #495057; }
    </style>
</head>
<body>
    <h1>✅ Installation Complete!</h1>
    
    <div class="success">
        <p><strong>NetScan has been successfully installed.</strong></p>
    </div>
    
    <h3>Getting Started</h3>
    <p><strong>CLI:</strong> Open Terminal and run <code>netscan</code></p>
    <p><strong>GUI:</strong> Open <strong>NetScan</strong> from Applications</p>
    
    <h3>Documentation</h3>
    <p>Visit <a href="https://g1a1b1e.github.io/NetScan/">https://g1a1b1e.github.io/NetScan/</a></p>
    
    <h3>Support</h3>
    <p>Report issues at <a href="https://github.com/G1A1B1E/NetScan/issues">GitHub Issues</a></p>
    
    <p style="margin-top: 30px; color: #868e96;">Thank you for installing NetScan!</p>
</body>
</html>
HTML

    # Create background image (simple gradient PNG using ImageMagick if available)
    if command -v magick &> /dev/null; then
        magick -size 620x420 gradient:'#1a1a2e'-'#16213e' "$RESOURCES/background.png"
    else
        # Create a simple 1x1 pixel placeholder
        printf '\x89PNG\r\n\x1a\n' > "$RESOURCES/background.png"
    fi
    
    # === Build component packages ===
    log "Building CLI package..."
    pkgbuild --root "$PKG_ROOT/cli" \
             --scripts "$SCRIPTS/cli" \
             --identifier "com.netscan.cli" \
             --version "$VERSION" \
             --install-location "/" \
             "$MAC_BUILD/NetScan-CLI.pkg"
    
    if [[ -d "$PKG_ROOT/gui/NetScan.app" ]]; then
        log "Building GUI package..."
        pkgbuild --root "$PKG_ROOT/gui" \
                 --scripts "$SCRIPTS/gui" \
                 --identifier "com.netscan.gui" \
                 --version "$VERSION" \
                 --install-location "/Applications" \
                 "$MAC_BUILD/NetScan-GUI.pkg"
    fi
    
    # === Build product archive ===
    log "Building final installer package..."
    productbuild --distribution "$MAC_BUILD/distribution.xml" \
                 --resources "$RESOURCES" \
                 --package-path "$MAC_BUILD" \
                 "$OUTPUT_DIR/NetScan-${VERSION}-Installer.pkg"
    
    success "macOS installer created: $OUTPUT_DIR/NetScan-${VERSION}-Installer.pkg"
}

# Build Windows installer
build_windows_installer() {
    log "Building Windows NSIS installer..."
    
    local WIN_BUILD="$BUILD_DIR/windows"
    
    # Create NSIS script
    cat > "$WIN_BUILD/netscan-installer.nsi" << 'NSIS'
; NetScan Installer Script for NSIS
; Provides options to install CLI, GUI, or both

!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"

; General
Name "NetScan"
OutFile "NetScan-${VERSION}-Setup.exe"
InstallDir "$PROGRAMFILES\NetScan"
InstallDirRegKey HKLM "Software\NetScan" "InstallPath"
RequestExecutionLevel admin
Unicode True

; Version info
VIProductVersion "${VERSION}.0"
VIAddVersionKey "ProductName" "NetScan"
VIAddVersionKey "CompanyName" "G1A1B1E"
VIAddVersionKey "FileDescription" "NetScan Network Intelligence Suite"
VIAddVersionKey "FileVersion" "${VERSION}"
VIAddVersionKey "ProductVersion" "${VERSION}"
VIAddVersionKey "LegalCopyright" "Copyright (c) 2026 G1A1B1E"

; Interface Settings
!define MUI_ABORTWARNING
!define MUI_ICON "icon.ico"
!define MUI_UNICON "icon.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "welcome.bmp"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "header.bmp"
!define MUI_HEADERIMAGE_RIGHT

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Languages
!insertmacro MUI_LANGUAGE "English"

; Component descriptions
LangString DESC_CLI ${LANG_ENGLISH} "Install NetScan command-line tools for terminal-based network scanning. Requires Python 3.6+."
LangString DESC_GUI ${LANG_ENGLISH} "Install the NetScan desktop application with modern UI, dashboard, and visual network tools."

; Installer Sections
Section "Command Line Tools" SecCLI
    SectionIn 1 3
    
    SetOutPath "$INSTDIR\cli"
    
    ; Copy CLI files
    File /r "cli\*.*"
    
    ; Create batch wrapper
    FileOpen $0 "$INSTDIR\cli\netscan.bat" w
    FileWrite $0 "@echo off$\r$\n"
    FileWrite $0 "python $\"%~dp0netscan.py$\" %*$\r$\n"
    FileClose $0
    
    ; Add to PATH
    EnVar::AddValue "PATH" "$INSTDIR\cli"
    
    ; Create Start Menu shortcut
    CreateDirectory "$SMPROGRAMS\NetScan"
    CreateShortcut "$SMPROGRAMS\NetScan\NetScan CLI.lnk" "cmd.exe" '/k "$INSTDIR\cli\netscan.bat"' "$INSTDIR\icon.ico"
SectionEnd

Section "Desktop Application" SecGUI
    SectionIn 1 2
    
    SetOutPath "$INSTDIR\gui"
    
    ; Copy GUI files
    File /r "gui\*.*"
    
    ; Create Start Menu shortcut
    CreateDirectory "$SMPROGRAMS\NetScan"
    CreateShortcut "$SMPROGRAMS\NetScan\NetScan.lnk" "$INSTDIR\gui\NetScan.exe" "" "$INSTDIR\gui\NetScan.exe" 0
    
    ; Create Desktop shortcut
    CreateShortcut "$DESKTOP\NetScan.lnk" "$INSTDIR\gui\NetScan.exe" "" "$INSTDIR\gui\NetScan.exe" 0
SectionEnd

Section "-Common"
    ; Always installed
    SetOutPath "$INSTDIR"
    
    ; Copy icon
    File "icon.ico"
    
    ; Write registry keys
    WriteRegStr HKLM "Software\NetScan" "InstallPath" "$INSTDIR"
    WriteRegStr HKLM "Software\NetScan" "Version" "${VERSION}"
    
    ; Write uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    ; Add to Add/Remove Programs
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\NetScan" "DisplayName" "NetScan"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\NetScan" "UninstallString" '"$INSTDIR\Uninstall.exe"'
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\NetScan" "DisplayIcon" "$INSTDIR\icon.ico"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\NetScan" "DisplayVersion" "${VERSION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\NetScan" "Publisher" "G1A1B1E"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\NetScan" "URLInfoAbout" "https://github.com/G1A1B1E/NetScan"
    
    ; Get installed size
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\NetScan" "EstimatedSize" "$0"
SectionEnd

; Component descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecCLI} $(DESC_CLI)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecGUI} $(DESC_GUI)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Uninstaller
Section "Uninstall"
    ; Remove from PATH
    EnVar::DeleteValue "PATH" "$INSTDIR\cli"
    
    ; Remove files
    RMDir /r "$INSTDIR\cli"
    RMDir /r "$INSTDIR\gui"
    Delete "$INSTDIR\icon.ico"
    Delete "$INSTDIR\Uninstall.exe"
    RMDir "$INSTDIR"
    
    ; Remove shortcuts
    Delete "$SMPROGRAMS\NetScan\*.*"
    RMDir "$SMPROGRAMS\NetScan"
    Delete "$DESKTOP\NetScan.lnk"
    
    ; Remove registry keys
    DeleteRegKey HKLM "Software\NetScan"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\NetScan"
SectionEnd

; Installation types
InstType "Full (GUI + CLI)"
InstType "GUI Only"
InstType "CLI Only"
NSIS

    # Update version in NSIS script
    sed -i.bak "s/\${VERSION}/${VERSION}/g" "$WIN_BUILD/netscan-installer.nsi"
    rm -f "$WIN_BUILD/netscan-installer.nsi.bak"
    
    # === Prepare Windows CLI files ===
    log "Preparing Windows CLI files..."
    mkdir -p "$WIN_BUILD/cli"
    
    # Copy Python helpers
    cp -r "$PROJECT_ROOT/helpers/"*.py "$WIN_BUILD/cli/" 2>/dev/null || true
    
    # Create Python wrapper for Windows
    cat > "$WIN_BUILD/cli/netscan.py" << 'PYWRAPPER'
#!/usr/bin/env python3
"""
NetScan CLI for Windows
Network Intelligence Suite
"""

import sys
import os
import subprocess
import argparse

def main():
    parser = argparse.ArgumentParser(description='NetScan - Network Intelligence Suite')
    parser.add_argument('--scan', '-s', action='store_true', help='Scan network')
    parser.add_argument('--lookup', '-l', metavar='MAC', help='Lookup MAC address')
    parser.add_argument('--export', '-e', metavar='FILE', help='Export results')
    parser.add_argument('--wol', '-w', metavar='MAC', help='Wake-on-LAN')
    parser.add_argument('--version', '-v', action='version', version='NetScan 2.1.0')
    
    args = parser.parse_args()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    if args.scan:
        subprocess.run([sys.executable, os.path.join(script_dir, 'scanner.py')])
    elif args.lookup:
        subprocess.run([sys.executable, os.path.join(script_dir, 'lookup.py'), args.lookup])
    elif args.wol:
        subprocess.run([sys.executable, os.path.join(script_dir, 'wol.py'), '--mac', args.wol])
    elif args.export:
        subprocess.run([sys.executable, os.path.join(script_dir, 'export.py'), '--output', args.export])
    else:
        print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║        🔍 NetScan - Network Intelligence Suite               ║
║                     Version 2.1.0                            ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

Usage:
  netscan --scan           Scan the network
  netscan --lookup MAC     Lookup MAC address vendor
  netscan --wol MAC        Send Wake-on-LAN packet
  netscan --export FILE    Export results to file
  netscan --help           Show this help message

For GUI, launch NetScan from the Start Menu or Desktop.
""")

if __name__ == '__main__':
    main()
PYWRAPPER

    # === Prepare Windows GUI files ===
    log "Preparing Windows GUI files..."
    mkdir -p "$WIN_BUILD/gui"
    
    if [[ -d "$PROJECT_ROOT/netscan-gui/dist/win-unpacked" ]]; then
        cp -r "$PROJECT_ROOT/netscan-gui/dist/win-unpacked/"* "$WIN_BUILD/gui/"
    else
        warn "Windows GUI build not found. Build with 'cd netscan-gui && npm run build:win' first"
    fi
    
    # Copy icon
    if [[ -f "$PROJECT_ROOT/netscan-gui/build/icon.ico" ]]; then
        cp "$PROJECT_ROOT/netscan-gui/build/icon.ico" "$WIN_BUILD/"
    fi
    
    # Create license file
    cat > "$WIN_BUILD/LICENSE.txt" << 'LICENSE'
MIT License

Copyright (c) 2026 G1A1B1E

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
LICENSE

    # Create installer bitmaps if ImageMagick available
    if command -v magick &> /dev/null; then
        # Welcome bitmap (164x314)
        magick -size 164x314 gradient:'#1a1a2e'-'#228be6' "$WIN_BUILD/welcome.bmp"
        # Header bitmap (150x57)
        magick -size 150x57 gradient:'#228be6'-'#1a1a2e' "$WIN_BUILD/header.bmp"
    else
        # Create placeholder BMPs
        touch "$WIN_BUILD/welcome.bmp"
        touch "$WIN_BUILD/header.bmp"
    fi
    
    # Check if NSIS is available
    if command -v makensis &> /dev/null; then
        log "Building Windows installer with NSIS..."
        cd "$WIN_BUILD"
        makensis netscan-installer.nsi
        mv "NetScan-${VERSION}-Setup.exe" "$OUTPUT_DIR/"
        success "Windows installer created: $OUTPUT_DIR/NetScan-${VERSION}-Setup.exe"
    else
        warn "NSIS not found. Windows installer script prepared but not built."
        warn "Install NSIS with: brew install makensis"
        warn "Then run: cd $WIN_BUILD && makensis netscan-installer.nsi"
        
        # Create a simple ZIP as fallback
        log "Creating Windows ZIP package as fallback..."
        cd "$WIN_BUILD"
        zip -r "$OUTPUT_DIR/NetScan-${VERSION}-Windows.zip" cli gui icon.ico LICENSE.txt
        success "Windows ZIP created: $OUTPUT_DIR/NetScan-${VERSION}-Windows.zip"
    fi
}

# Create standalone CLI installer for macOS
build_macos_cli_only() {
    log "Building macOS CLI-only installer..."
    
    local CLI_BUILD="$BUILD_DIR/macos-cli"
    mkdir -p "$CLI_BUILD/root/usr/local/bin"
    mkdir -p "$CLI_BUILD/root/usr/local/share/netscan"/{lib,helpers,data}
    mkdir -p "$CLI_BUILD/scripts"
    
    # Copy files
    cp "$PROJECT_ROOT/netscan" "$CLI_BUILD/root/usr/local/bin/"
    cp -r "$PROJECT_ROOT/lib/"* "$CLI_BUILD/root/usr/local/share/netscan/lib/"
    cp -r "$PROJECT_ROOT/helpers/"* "$CLI_BUILD/root/usr/local/share/netscan/helpers/"
    
    # Create wrapper
    cat > "$CLI_BUILD/root/usr/local/bin/netscan" << 'WRAPPER'
#!/bin/bash
export NETSCAN_HOME="/usr/local/share/netscan"
export NETSCAN_LIB="$NETSCAN_HOME/lib"
export NETSCAN_HELPERS="$NETSCAN_HOME/helpers"
source "$NETSCAN_LIB/scanner.sh"
main "$@"
WRAPPER
    chmod +x "$CLI_BUILD/root/usr/local/bin/netscan"
    
    # Postinstall
    cat > "$CLI_BUILD/scripts/postinstall" << 'SCRIPT'
#!/bin/bash
chmod +x /usr/local/bin/netscan
chmod -R +x /usr/local/share/netscan/helpers/*.py 2>/dev/null || true
exit 0
SCRIPT
    chmod +x "$CLI_BUILD/scripts/postinstall"
    
    pkgbuild --root "$CLI_BUILD/root" \
             --scripts "$CLI_BUILD/scripts" \
             --identifier "com.netscan.cli" \
             --version "$VERSION" \
             --install-location "/" \
             "$OUTPUT_DIR/NetScan-CLI-${VERSION}.pkg"
    
    success "CLI-only installer created: $OUTPUT_DIR/NetScan-CLI-${VERSION}.pkg"
}

# Print summary
print_summary() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                   Build Complete!                            ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "📁 Output Directory: $OUTPUT_DIR"
    echo ""
    echo "📦 Created Installers:"
    ls -lh "$OUTPUT_DIR"/*.pkg "$OUTPUT_DIR"/*.exe "$OUTPUT_DIR"/*.zip 2>/dev/null | while read line; do
        echo "   $line"
    done
    echo ""
    echo "📋 Installation Options:"
    echo "   • Full Install: GUI + CLI"
    echo "   • GUI Only: Desktop application"
    echo "   • CLI Only: Command-line tools"
    echo ""
}

# Main
main() {
    print_banner
    setup_directories
    build_macos_installer
    build_macos_cli_only
    build_windows_installer
    print_summary
}

main "$@"
