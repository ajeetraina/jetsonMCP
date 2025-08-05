# JetsonMCP Quick Start Guide

Get up and running with JetsonMCP in 15 minutes!

## 🏁 Prerequisites

- **Jetson Nano** with JetPack 4.6+ installed
- **Development Machine** with Python 3.8+
- **Network Connection** between your machine and Jetson
- **Claude Desktop** installed on your development machine

## 🚀 Step 1: Prepare Your Jetson Nano

### Option A: Automatic Setup (Recommended)

```bash
# On your Jetson Nano, run:
wget -O - https://raw.githubusercontent.com/ajeetraina/jetsonMCP/main/scripts/setup-jetson.sh | bash
```

### Option B: Manual Setup

```bash
# Enable SSH
sudo systemctl enable ssh
sudo systemctl start ssh

# Configure passwordless sudo (for system management)
sudo visudo
# Add: yourusername ALL=(ALL) NOPASSWD:ALL

# Get your Jetson's IP address
hostname -I
```

## 📋 Step 2: Install JetsonMCP

### On Your Development Machine:

```bash
# Clone the repository
git clone https://github.com/ajeetraina/jetsonMCP.git
cd jetsonMCP

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install JetsonMCP
pip install -e .
```

## ⚙️ Step 3: Configure Connection

```bash
# Copy configuration template
cp .env.example .env

# Edit configuration
nano .env  # or your preferred editor
```

**Minimum required settings in `.env`:**

```bash
JETSON_HOST=192.168.1.100        # Your Jetson's IP address
JETSON_USERNAME=your_username     # SSH username
JETSON_PASSWORD=your_password     # SSH password
```

## 🧪 Step 4: Test Connection

```bash
# Test SSH connection to your Jetson
jetsonmcp test-connection

# Should show: ✅ Connection successful!
```

## 🔗 Step 5: Configure Claude Desktop

### Option A: Automatic Setup

```bash
# Run the integration script
./scripts/install-claude-desktop.sh
```

### Option B: Manual Setup

Add to your Claude Desktop configuration:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "jetsonmcp": {
      "command": "python",
      "args": ["-m", "jetsonmcp.server"],
      "cwd": "/absolute/path/to/jetsonMCP"
    }
  }
}
```

## 🎉 Step 6: Start Using JetsonMCP

1. **Restart Claude Desktop** to load the new configuration

2. **Test the integration** by asking Claude:

> "What's the current temperature on my Jetson Nano?"

> "Switch my Jetson to 5W power mode"

> "Check if CUDA is working on my Jetson"

> "Install TensorFlow on my Jetson Nano"

## 📋 Common First Commands

### System Information
- "Get system information from my Jetson"
- "Check disk space on my Jetson Nano"
- "What services are running on my Jetson?"

### Hardware Management
- "What's the current power mode?"
- "Monitor GPU temperature for 30 seconds"
- "Check GPU memory usage"

### AI/ML Setup
- "Check if CUDA is installed and working"
- "Install PyTorch on my Jetson"
- "Set up Jupyter Notebook for remote access"

### Container Operations
- "Check if Docker is running"
- "Install NVIDIA Container Runtime"
- "List all Docker containers"

## 🔧 Troubleshooting

### Connection Issues

**Problem**: ❌ Connection failed

**Solutions**:
1. Verify Jetson IP address: `hostname -I` (on Jetson)
2. Test SSH manually: `ssh username@jetson-ip`
3. Check firewall: `sudo ufw status` (on Jetson)
4. Verify SSH service: `sudo systemctl status ssh` (on Jetson)

### Permission Issues

**Problem**: "sudo: no password" errors

**Solution**: Configure passwordless sudo on Jetson:
```bash
sudo visudo
# Add: yourusername ALL=(ALL) NOPASSWD:ALL
```

### Claude Desktop Issues

**Problem**: Claude doesn't recognize JetsonMCP

**Solutions**:
1. Verify configuration file location
2. Check that Python can import jetsonmcp: `python -c "import jetsonmcp"`
3. Restart Claude Desktop completely
4. Check Claude Desktop logs

### Python Import Errors

**Problem**: "ModuleNotFoundError: No module named 'jetsonmcp'"

**Solution**: Install in development mode:
```bash
cd jetsonMCP
pip install -e .
```

## 📄 Next Steps

### Explore Advanced Features
- Set up model deployment workflows
- Configure container-based AI workloads
- Set up monitoring and alerting
- Explore GPIO control capabilities

### Development
- Read the [Architecture Guide](ARCHITECTURE.md)
- Check out [Contributing Guidelines](../CONTRIBUTING.md)
- Run the test suite: `make test`

### Production Deployment
- Set up SSH key authentication
- Configure system monitoring
- Set up automated backups
- Review security settings

## 📞 Support

If you encounter issues:

1. **Check the logs**: Look for error messages in the console
2. **Test components**: Use `jetsonmcp test-connection` and `make test`
3. **Search issues**: Check [GitHub Issues](https://github.com/ajeetraina/jetsonMCP/issues)
4. **Ask for help**: Create a new issue with:
   - Your setup details
   - Error messages
   - Steps to reproduce

---

**Congratulations! 🎉 You're now ready to manage your Jetson Nano with AI assistance through JetsonMCP!**

For more advanced usage, check out the complete [README](../README.md) and [documentation](/).
