#!/bin/bash
# Claude Desktop Integration Setup for JetsonMCP
# This script helps configure Claude Desktop to work with JetsonMCP

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Detect operating system
OS=""
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    CONFIG_DIR="$HOME/Library/Application Support/Claude"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    CONFIG_DIR="$HOME/.config/Claude"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    OS="windows"
    CONFIG_DIR="$APPDATA/Claude"
else
    print_warning "Unknown operating system: $OSTYPE"
    print_warning "Please manually configure Claude Desktop"
    exit 1
fi

print_status "Detected OS: $OS"
print_status "Claude Desktop config directory: $CONFIG_DIR"

# Create config directory if it doesn't exist
mkdir -p "$CONFIG_DIR"

# Get the absolute path to JetsonMCP
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
JETSONMCP_DIR="$(dirname "$SCRIPT_DIR")"
JETSONMCP_ABS_PATH="$(cd "$JETSONMCP_DIR" && pwd)"

print_status "JetsonMCP directory: $JETSONMCP_ABS_PATH"

# Check if JetsonMCP is installed
if [[ ! -f "$JETSONMCP_ABS_PATH/jetsonmcp/__init__.py" ]]; then
    print_warning "JetsonMCP not found in expected location"
    read -p "Enter the full path to your JetsonMCP directory: " JETSONMCP_ABS_PATH
fi

# Create Claude Desktop configuration
CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"

# Backup existing config if it exists
if [[ -f "$CONFIG_FILE" ]]; then
    print_status "Backing up existing Claude Desktop configuration..."
    cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Determine Python command
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    if command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_warning "Python not found in PATH. Using 'python3' in config."
    fi
fi

# Create the configuration
print_status "Creating Claude Desktop configuration..."

cat > "$CONFIG_FILE" << EOF
{
  "mcpServers": {
    "jetsonmcp": {
      "command": "$PYTHON_CMD",
      "args": ["-m", "jetsonmcp.server"],
      "cwd": "$JETSONMCP_ABS_PATH",
      "env": {
        "PYTHONPATH": "$JETSONMCP_ABS_PATH"
      }
    }
  }
}
EOF

print_status "Claude Desktop configuration created successfully!"

# Display configuration
echo ""
print_status "Configuration contents:"
cat "$CONFIG_FILE"

echo ""
print_status "Setup complete! Next steps:"
echo "1. Make sure JetsonMCP is installed: pip install -e ."
echo "2. Configure your .env file with Jetson connection details"
echo "3. Test the connection: jetsonmcp test-connection"
echo "4. Restart Claude Desktop to load the new configuration"
echo ""
print_status "Configuration file location: $CONFIG_FILE"

# Platform-specific instructions
case $OS in
    "macos")
        echo ""
        print_status "macOS specific notes:"
        echo "- Restart Claude Desktop from Applications folder"
        echo "- Check Activity Monitor if you have connection issues"
        ;;
    "linux")
        echo ""
        print_status "Linux specific notes:"
        echo "- Restart Claude Desktop application"
        echo "- Check system logs if you have connection issues"
        ;;
    "windows")
        echo ""
        print_status "Windows specific notes:"
        echo "- Restart Claude Desktop from Start Menu"
        echo "- Check Task Manager if you have connection issues"
        ;;
esac

echo ""
print_status "If you encounter issues:"
echo "1. Check that Python can import jetsonmcp: python -c 'import jetsonmcp'"
echo "2. Verify the working directory path is correct"
echo "3. Check Claude Desktop logs for error messages"
echo "4. Test JetsonMCP directly: python -m jetsonmcp.server"

print_status "Integration setup completed! 🎉"
