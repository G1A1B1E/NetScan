#!/bin/bash
# Build release assets for NetScan
# Usage: ./build-release.sh v1.0.0

VERSION="${1:-v1.0.0}"
RELEASE_DIR="release-${VERSION}"

echo "🚀 Building NetScan ${VERSION} release assets..."

# Create release directory
rm -rf "$RELEASE_DIR"
mkdir -p "$RELEASE_DIR"

# ============================================
# 1. Linux Package
# ============================================
echo "📦 Building Linux package..."
LINUX_DIR="netscan-${VERSION}-linux"
mkdir -p "$LINUX_DIR"

cp -r helpers/ "$LINUX_DIR/"
cp -r data/ "$LINUX_DIR/" 2>/dev/null || mkdir -p "$LINUX_DIR/data"
cp scanner.sh "$LINUX_DIR/netscan"
cp install.sh "$LINUX_DIR/"
cp README.md "$LINUX_DIR/"
chmod +x "$LINUX_DIR/netscan" "$LINUX_DIR/install.sh"

tar -czvf "$RELEASE_DIR/netscan-${VERSION}-linux.tar.gz" "$LINUX_DIR"
rm -rf "$LINUX_DIR"

# ============================================
# 2. macOS Package (same as Linux)
# ============================================
echo "📦 Building macOS package..."
MACOS_DIR="netscan-${VERSION}-macos"
mkdir -p "$MACOS_DIR"

cp -r helpers/ "$MACOS_DIR/"
cp -r data/ "$MACOS_DIR/" 2>/dev/null || mkdir -p "$MACOS_DIR/data"
cp scanner.sh "$MACOS_DIR/netscan"
cp install.sh "$MACOS_DIR/"
cp README.md "$MACOS_DIR/"
chmod +x "$MACOS_DIR/netscan" "$MACOS_DIR/install.sh"

tar -czvf "$RELEASE_DIR/netscan-${VERSION}-macos.tar.gz" "$MACOS_DIR"
rm -rf "$MACOS_DIR"

# ============================================
# 3. Windows Package
# ============================================
echo "📦 Building Windows package..."
WINDOWS_DIR="netscan-${VERSION}-windows"
mkdir -p "$WINDOWS_DIR"

cp -r windows/* "$WINDOWS_DIR/"
cp README.md "$WINDOWS_DIR/"

zip -r "$RELEASE_DIR/netscan-${VERSION}-windows.zip" "$WINDOWS_DIR"
rm -rf "$WINDOWS_DIR"

# ============================================
# 4. Standalone installer script
# ============================================
echo "📦 Creating standalone installer..."
cp install.sh "$RELEASE_DIR/netscan-install.sh"

# ============================================
# 5. Docker Compose file
# ============================================
echo "📦 Copying Docker files..."
cp docker-compose.yml "$RELEASE_DIR/" 2>/dev/null || echo "No docker-compose.yml found"

# ============================================
# 6. Download OUI database
# ============================================
echo "📦 Downloading OUI database..."
curl -fsSL "https://standards-oui.ieee.org/oui/oui.txt" -o "$RELEASE_DIR/oui.txt" 2>/dev/null || echo "Could not download OUI"

# ============================================
# Summary
# ============================================
echo ""
echo "✅ Release assets created in $RELEASE_DIR/"
echo ""
ls -lh "$RELEASE_DIR/"
echo ""
echo "📋 Upload these files to GitHub Release:"
echo "   - netscan-${VERSION}-linux.tar.gz"
echo "   - netscan-${VERSION}-macos.tar.gz"
echo "   - netscan-${VERSION}-windows.zip"
echo "   - netscan-install.sh"
echo "   - docker-compose.yml"
echo "   - oui.txt"
