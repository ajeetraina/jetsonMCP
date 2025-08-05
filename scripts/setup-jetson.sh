#!/bin/bash
# JetsonMCP Jetson Nano Setup Script
# This script prepares a Jetson Nano for use with JetsonMCP

set -e

echo "🚀 Setting up Jetson Nano for JetsonMCP..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Jetson
if [[ ! -f /etc/nv_tegra_release ]]; then
    print_error "This script should be run on an NVIDIA Jetson device"
    exit 1
fi

print_status "Detected Jetson device:"
cat /etc/nv_tegra_release

# Enable SSH if not already enabled
print_status "Configuring SSH service..."
sudo systemctl enable ssh
sudo systemctl start ssh

# Update system packages
print_status "Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install essential packages
print_status "Installing essential packages..."
sudo apt install -y \
    python3-pip \
    python3-venv \
    curl \
    wget \
    git \
    htop \
    iotop \
    vim \
    build-essential

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    print_status "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
else
    print_status "Docker is already installed"
fi

# Install NVIDIA Container Runtime
print_status "Setting up NVIDIA Container Runtime..."
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt update
sudo apt install -y nvidia-docker2
sudo systemctl restart docker

# Test NVIDIA Docker
print_status "Testing NVIDIA Docker setup..."
sudo docker run --rm --gpus all nvidia/cuda:11.4-base-ubuntu20.04 nvidia-smi || print_warning "NVIDIA Docker test failed - this is normal if no display is connected"

# Create jetson user if it doesn't exist
if ! id "jetson" &>/dev/null; then
    print_status "Creating jetson user..."
    sudo useradd -m -s /bin/bash jetson
    sudo usermod -aG sudo,docker jetson
    print_warning "Please set a password for the jetson user: sudo passwd jetson"
fi

# Set up passwordless sudo (OPTIONAL - for convenience)
read -p "Enable passwordless sudo for current user? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "$USER ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/$USER-nopasswd
    print_status "Passwordless sudo enabled for $USER"
fi

# Create directories for JetsonMCP
print_status "Creating JetsonMCP directories..."
mkdir -p ~/jetsonmcp
mkdir -p ~/models
mkdir -p ~/notebooks
mkdir -p ~/logs

# Install Python packages commonly used for AI
print_status "Installing common Python packages..."
pip3 install --user \
    numpy \
    matplotlib \
    jupyter \
    ipython \
    pillow

# Set up Jupyter for remote access
print_status "Configuring Jupyter for remote access..."
jupyter notebook --generate-config 2>/dev/null || true

# Add Jupyter configuration
cat >> ~/.jupyter/jupyter_notebook_config.py << EOF
# JetsonMCP Jupyter Configuration
c.NotebookApp.ip = '0.0.0.0'
c.NotebookApp.port = 8888
c.NotebookApp.open_browser = False
c.NotebookApp.allow_root = True
EOF

# Display system information
print_status "System Information:"
echo "Hostname: $(hostname)"
echo "IP Address: $(hostname -I | awk '{print $1}')"
echo "JetPack Version: $(cat /etc/nv_tegra_release)"
echo "CUDA Version: $(nvcc --version 2>/dev/null | grep release || echo 'Not found')"
echo "Python Version: $(python3 --version)"
echo "Docker Version: $(docker --version)"

# Set up firewall rules
print_status "Configuring firewall..."
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 8888/tcp  # Jupyter
sudo ufw allow 8080/tcp  # General development

print_status "🎉 Jetson Nano setup complete!"
print_status "Next steps:"
echo "1. Set up SSH key authentication (recommended)"
echo "2. Configure JetsonMCP with your Jetson's IP address"
echo "3. Test the connection: jetsonmcp test-connection"
echo ""
print_status "Jetson access information:"
echo "SSH: ssh $USER@$(hostname -I | awk '{print $1}')"
echo "Jupyter: http://$(hostname -I | awk '{print $1}'):8888"
echo ""
print_warning "If you enabled passwordless sudo, consider disabling it after JetsonMCP setup for security"

echo "Setup completed successfully! 🚀"
