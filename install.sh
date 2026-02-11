#!/bin/bash
set -e

echo "🤖 Bot Monitor Installation Script"
echo "==================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or later."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Found Python $PYTHON_VERSION"

# Determine installation directory
if [ "$EUID" -eq 0 ]; then
    # Running as root, install system-wide
    INSTALL_DIR="/opt/bot-monitor"
    BIN_DIR="/usr/local/bin"
    echo "📦 Installing system-wide to $INSTALL_DIR"
else
    # User installation
    INSTALL_DIR="$HOME/.local/bot-monitor"
    BIN_DIR="$HOME/.local/bin"
    echo "📦 Installing to $INSTALL_DIR (user-local)"
fi

# Create installation directory
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv "$INSTALL_DIR/venv"

# Activate virtual environment
source "$INSTALL_DIR/venv/bin/activate"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null

# Install package
echo "Installing bot-monitor..."
if [ -f "setup.py" ]; then
    # Installing from source
    pip install -e . > /dev/null
else
    echo "❌ setup.py not found. Please run this script from the repository root."
    exit 1
fi

# Create symlink
echo "Creating executable symlink..."
ln -sf "$INSTALL_DIR/venv/bin/bot-monitor" "$BIN_DIR/bot-monitor"

# Check if bin directory is in PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo ""
    echo "⚠️  $BIN_DIR is not in your PATH"
    echo "   Add this to your ~/.bashrc or ~/.zshrc:"
    echo "   export PATH=\"$BIN_DIR:\$PATH\""
fi

echo ""
echo "✓ Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Run: bot-monitor setup"
echo "  2. Edit config: ~/.config/bot-monitor/config.yaml"
echo "  3. Start monitoring: bot-monitor start"
echo ""
echo "For help: bot-monitor --help"
