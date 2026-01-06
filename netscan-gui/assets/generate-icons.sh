#!/bin/bash
# Icon generation script for NetScan GUI
# Requires ImageMagick (convert) and iconutil (macOS)

ASSETS_DIR="$(cd "$(dirname "$0")" && pwd)"
SVG_FILE="$ASSETS_DIR/icon.svg"

echo "🎨 NetScan Icon Generator"
echo "========================="

# Check for required tools
check_tool() {
    if ! command -v "$1" &> /dev/null; then
        echo "⚠️  Warning: $1 not found"
        return 1
    fi
    return 0
}

# Generate PNG files from SVG
generate_pngs() {
    echo ""
    echo "📦 Generating PNG files..."
    
    if check_tool convert; then
        local sizes=(16 32 64 128 256 512 1024)
        for size in "${sizes[@]}"; do
            convert -background none -resize ${size}x${size} "$SVG_FILE" "$ASSETS_DIR/icon_${size}.png"
            echo "  ✓ icon_${size}.png"
        done
        
        # Create @2x versions for macOS
        convert -background none -resize 32x32 "$SVG_FILE" "$ASSETS_DIR/icon_16@2x.png"
        convert -background none -resize 64x64 "$SVG_FILE" "$ASSETS_DIR/icon_32@2x.png"
        convert -background none -resize 256x256 "$SVG_FILE" "$ASSETS_DIR/icon_128@2x.png"
        convert -background none -resize 512x512 "$SVG_FILE" "$ASSETS_DIR/icon_256@2x.png"
        convert -background none -resize 1024x1024 "$SVG_FILE" "$ASSETS_DIR/icon_512@2x.png"
        echo "  ✓ @2x retina versions"
    else
        echo "  ⚠️  Skipping PNG generation (ImageMagick not installed)"
        echo "  Install with: brew install imagemagick"
    fi
}

# Generate macOS .icns file
generate_icns() {
    echo ""
    echo "🍎 Generating macOS icon (icon.icns)..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if check_tool iconutil; then
            # Create iconset directory
            local ICONSET="$ASSETS_DIR/icon.iconset"
            mkdir -p "$ICONSET"
            
            # Check if PNG files exist
            if [[ -f "$ASSETS_DIR/icon_16.png" ]]; then
                cp "$ASSETS_DIR/icon_16.png" "$ICONSET/icon_16x16.png"
                cp "$ASSETS_DIR/icon_16@2x.png" "$ICONSET/icon_16x16@2x.png"
                cp "$ASSETS_DIR/icon_32.png" "$ICONSET/icon_32x32.png"
                cp "$ASSETS_DIR/icon_32@2x.png" "$ICONSET/icon_32x32@2x.png"
                cp "$ASSETS_DIR/icon_128.png" "$ICONSET/icon_128x128.png"
                cp "$ASSETS_DIR/icon_128@2x.png" "$ICONSET/icon_128x128@2x.png"
                cp "$ASSETS_DIR/icon_256.png" "$ICONSET/icon_256x256.png"
                cp "$ASSETS_DIR/icon_256@2x.png" "$ICONSET/icon_256x256@2x.png"
                cp "$ASSETS_DIR/icon_512.png" "$ICONSET/icon_512x512.png"
                cp "$ASSETS_DIR/icon_512@2x.png" "$ICONSET/icon_512x512@2x.png"
                
                # Generate icns
                iconutil -c icns "$ICONSET" -o "$ASSETS_DIR/icon.icns"
                rm -rf "$ICONSET"
                echo "  ✓ icon.icns created"
            else
                echo "  ⚠️  PNG files not found. Run generate_pngs first."
            fi
        fi
    else
        echo "  ⚠️  Skipping .icns (macOS only)"
    fi
}

# Generate Windows .ico file
generate_ico() {
    echo ""
    echo "🪟 Generating Windows icon (icon.ico)..."
    
    if check_tool convert; then
        if [[ -f "$ASSETS_DIR/icon_16.png" ]]; then
            convert "$ASSETS_DIR/icon_16.png" \
                    "$ASSETS_DIR/icon_32.png" \
                    "$ASSETS_DIR/icon_64.png" \
                    "$ASSETS_DIR/icon_128.png" \
                    "$ASSETS_DIR/icon_256.png" \
                    "$ASSETS_DIR/icon.ico"
            echo "  ✓ icon.ico created"
        else
            echo "  ⚠️  PNG files not found. Run generate_pngs first."
        fi
    else
        echo "  ⚠️  Skipping .ico generation (ImageMagick not installed)"
    fi
}

# Cleanup temporary PNG files
cleanup() {
    echo ""
    echo "🧹 Cleaning up temporary files..."
    rm -f "$ASSETS_DIR"/icon_*.png
    echo "  ✓ Temporary files removed"
}

# Main execution
main() {
    if [[ ! -f "$SVG_FILE" ]]; then
        echo "❌ Error: icon.svg not found in $ASSETS_DIR"
        exit 1
    fi
    
    generate_pngs
    generate_icns
    generate_ico
    
    echo ""
    echo "💡 Tip: For production builds, consider using:"
    echo "   - electron-icon-builder: npm install -g electron-icon-builder"
    echo "   - Then run: electron-icon-builder --input=assets/icon.svg --output=assets"
    
    read -p "
Remove temporary PNG files? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cleanup
    fi
    
    echo ""
    echo "✅ Icon generation complete!"
}

# Run
main "$@"
