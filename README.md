# JetsonMCP

An MCP server that connects AI assistants to NVIDIA Jetson Nano systems for comprehensive edge computing management, AI workload optimization, and system administration.

JetsonMCP enables AI assistants like Claude to help configure and manage Jetson Nano systems through SSH connections. From AI model deployment to system optimization - ask questions in natural language instead of learning complex CUDA and Linux commands.

## 🚀 What Makes JetsonMCP Special

**Built for Edge AI Computing**
- CUDA toolkit management and optimization
- JetPack SDK integration and updates  
- AI framework installation (TensorFlow, PyTorch, TensorRT)
- Model deployment and inference optimization

**Hardware-Specific Optimizations**
- GPU memory management and monitoring
- Power mode configuration (10W/5W modes)
- Temperature monitoring with thermal throttling
- Fan curve management and cooling optimization

**Container & Orchestration**
- Docker container management for AI workloads
- NVIDIA Container Toolkit integration
- Kubernetes edge deployment support
- Multi-architecture container support (ARM64)

## 🎯 How It Works

Natural language requests are translated through Claude Desktop via MCP protocol to optimized commands executed on your Jetson Nano.

### Examples:

**AI & ML Operations:**
- *"Deploy YOLOv5 model for object detection"* - Downloads, optimizes, and runs inference
- *"Check CUDA memory usage"* - Monitors GPU utilization and memory allocation
- *"Switch to 5W power mode"* - Optimizes power consumption for battery operation
- *"Install TensorRT optimization"* - Sets up high-performance inference engine

**System Management:**
- *"Monitor GPU temperature while running inference"* - Real-time thermal monitoring
- *"Update JetPack to latest version"* - Manages NVIDIA software stack updates
- *"Optimize Docker for AI workloads"* - Configures runtime for GPU acceleration

**Edge Computing:**
- *"Deploy lightweight Kubernetes cluster"* - Sets up K3s for edge orchestration
- *"Configure remote model serving"* - Sets up inference endpoints
- *"Monitor system resources during AI tasks"* - Performance profiling and optimization

## 🔧 Key Features

### Edge AI Management
- **CUDA Toolkit Integration** - Automatic CUDA environment setup and management
- **JetPack Management** - SDK updates, component installation, and version control
- **AI Framework Support** - TensorFlow, PyTorch, OpenCV, TensorRT optimization
- **Model Deployment** - Automated model conversion, optimization, and serving

### Hardware Optimization  
- **Power Management** - Dynamic power mode switching (10W/5W/MAXN)
- **Thermal Management** - Temperature monitoring with automatic throttling
- **GPU Monitoring** - Memory usage, utilization, and performance metrics
- **Fan Control** - Custom fan curves and cooling optimization

### Container Orchestration
- **NVIDIA Docker** - GPU-accelerated container runtime management
- **Edge Kubernetes** - K3s deployment for distributed AI workloads  
- **Multi-arch Support** - ARM64 container management and deployment
- **Registry Management** - Private registry setup for edge deployments

### System Administration
- **Remote Management** - SSH-based secure system administration
- **Package Management** - APT and snap package installation/updates
- **Service Management** - Systemd service control and monitoring
- **Backup & Recovery** - System state management and restoration

## 📋 Prerequisites

### Jetson Nano Setup
1. **Fresh JetPack Installation** (4.6+ recommended)
2. **SSH Access Enabled**
3. **Adequate Power Supply** (5V/4A recommended for full performance)
4. **MicroSD Card** (64GB+ recommended) or NVMe SSD
5. **Internet Connectivity** for package installation

### Network Configuration
- Static IP recommended for consistent access
- Firewall configured to allow SSH (port 22)
- Optional: VPN setup for remote access

## ⚡ Quick Start

### 1. Prepare Your Jetson Nano

```bash
# Enable SSH (if not already enabled)
sudo systemctl enable ssh
sudo systemctl start ssh

# Configure passwordless sudo (required for system management)
sudo visudo
# Add: yourusername ALL=(ALL) NOPASSWD:ALL

# Get your Jetson's IP address
hostname -I
```

### 2. Install JetsonMCP

```bash
# Clone repository
git clone https://github.com/ajeetraina/jetsonMCP.git
cd jetsonMCP

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .
```

### 3. Configure Connection

```bash
# Copy configuration template
cp .env.example .env

# Edit with your Jetson's details
nano .env
```

Required `.env` settings:
```bash
JETSON_HOST=192.168.1.100        # Your Jetson's IP address
JETSON_USERNAME=your_username     # SSH username
JETSON_PASSWORD=your_password     # SSH password (or use SSH key)
# JETSON_SSH_KEY_PATH=~/.ssh/id_rsa  # Alternative: SSH key path

# Optional: Advanced Configuration
JETSON_POWER_MODE=0              # 0=MAXN, 1=5W, 2=10W
CUDA_VISIBLE_DEVICES=0           # GPU device selection
DOCKER_REGISTRY=localhost:5000   # Private registry for edge deployments
```

### 4. Claude Desktop Integration

Add to your Claude Desktop configuration:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`  
**Linux:** `~/.config/Claude/claude_desktop_config.json`

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

Restart Claude Desktop to load the server.

## 🛠️ Available Tools

### AI & ML Management
- **`manage_ai_workloads`** - Model deployment, inference optimization, CUDA management
- **`manage_jetpack`** - JetPack SDK installation, updates, component management
- **`manage_frameworks`** - TensorFlow, PyTorch, OpenCV, TensorRT installation

### Hardware Control
- **`manage_hardware`** - Power modes, temperature monitoring, fan control, GPIO
- **`manage_performance`** - CPU/GPU governors, frequency scaling, thermal management
- **`manage_storage`** - SSD optimization, swap configuration, disk management

### Container Operations  
- **`manage_containers`** - Docker management, NVIDIA runtime, GPU acceleration
- **`manage_orchestration`** - Kubernetes/K3s deployment, edge computing setup
- **`manage_registry`** - Private registry setup, multi-arch image management

### System Administration
- **`manage_system`** - Package management, updates, service control, networking
- **`manage_security`** - Firewall, SSH keys, user management, system hardening
- **`manage_monitoring`** - System metrics, logging, alerting, remote monitoring

## 🔧 Advanced Configuration

### Power Management
```bash
# Available power modes
# 0: MAXN (15W) - Maximum performance
# 1: 5W - Power efficient mode  
# 2: 10W - Balanced mode
sudo nvpmodel -m 1  # Switch to 5W mode
```

### CUDA Environment
```bash
# Verify CUDA installation
nvcc --version
nvidia-smi

# Set CUDA paths (automatically configured by JetsonMCP)
export PATH=/usr/local/cuda/bin:$PATH
export LDFLAGS=-L/usr/local/cuda/lib64:$LDFLAGS
```

### Docker GPU Support
```bash
# NVIDIA Container Toolkit (managed by JetsonMCP)
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
```

## 🧪 Testing & Development

### Run Tests
```bash
# Run all tests
make test

# Specific component tests
make test-ai          # AI workload management
make test-hardware    # Hardware control
make test-containers  # Container operations
make test-system      # System administration

# Integration tests
python run_tests.py --integration --coverage
```

### Development Setup
```bash
# Install development dependencies
pip install -e ".[dev]"

# Pre-commit hooks
pre-commit install

# Code formatting
black jetsonmcp/
isort jetsonmcp/

# Type checking
mypy jetsonmcp/
```

## 📊 Monitoring & Observability

### System Metrics
- **CPU/GPU Utilization** - Real-time performance monitoring
- **Memory Usage** - RAM and GPU memory tracking
- **Temperature Sensors** - Thermal monitoring and alerts
- **Power Consumption** - Current power mode and usage metrics

### AI Workload Metrics
- **Inference Latency** - Model performance benchmarking
- **Throughput** - Requests per second for deployed models
- **Resource Utilization** - GPU memory and compute efficiency
- **Model Accuracy** - Performance validation and monitoring

## 🔒 Security Features

### SSH Security
- Host key verification and rotation
- Connection timeouts and retry logic
- Credential management and cleanup
- Audit logging for all operations

### Container Security
- Image vulnerability scanning
- Runtime security policies
- Network isolation and segmentation
- Secrets management for AI models

### System Hardening
- Firewall configuration management
- User privilege separation
- System update automation
- Security patch monitoring

## 🚀 Use Cases

### Edge AI Development
- Rapid prototyping of AI applications
- Model optimization and benchmarking
- Distributed inference deployment
- Real-time computer vision applications

### IoT & Sensor Networks
- Sensor data processing and analysis
- Edge computing orchestration
- Remote device management
- Predictive maintenance systems

### Industrial Applications
- Quality control and inspection
- Predictive analytics
- Autonomous systems development
- Industrial IoT integration

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Priorities
1. **AI Framework Integration** - Support for additional ML frameworks
2. **Edge Orchestration** - Advanced Kubernetes edge deployment
3. **Hardware Abstraction** - Support for other Jetson platforms (AGX, Xavier)
4. **Monitoring Enhancement** - Advanced telemetry and observability

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

## 🔗 Related Projects

- [retroMCP](https://github.com/nbhansen/retroMCP) - MCP server for Raspberry Pi systems
- [NVIDIA JetPack](https://developer.nvidia.com/embedded/jetpack) - Official Jetson development SDK
- [NVIDIA Container Toolkit](https://github.com/NVIDIA/nvidia-docker) - GPU container runtime

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/ajeetraina/jetsonMCP/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ajeetraina/jetsonMCP/discussions)
- **Email**: ajeetraina@gmail.com

---

**Built with ❤️ for the Edge AI Community**

*JetsonMCP - Bringing AI-powered system administration to NVIDIA Jetson Nano*