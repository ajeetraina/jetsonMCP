# JetsonMCP Examples

Practical examples of using JetsonMCP for common edge AI and system management tasks.

## 🔋 Hardware Management

### Power Management

**Check current power mode:**
> "What power mode is my Jetson currently using?"

*Expected response: Current power mode information with available options*

**Switch to power-efficient mode:**
> "Switch my Jetson to 5W power mode to save battery"

*Expected response: Power mode changed confirmation*

**Optimize for performance:**
> "Set my Jetson to maximum performance mode for AI training"

*Expected response: MAXN mode activation*

### Temperature Monitoring

**Check current temperatures:**
> "What's the temperature of my Jetson Nano right now?"

*Expected response: CPU, GPU, and other thermal zone readings*

**Monitor thermal conditions:**
> "Monitor my Jetson's temperature for the next 2 minutes while I run this model"

*Expected response: Time-series temperature data with analysis*

**Set up thermal alerts:**
> "Alert me if my Jetson gets too hot during this AI workload"

*Expected response: Temperature monitoring with threshold warnings*

### GPU and Memory Management

**Check GPU status:**
> "Show me detailed information about my Jetson's GPU"

*Expected response: GPU model, memory, utilization, and capabilities*

**Monitor memory usage:**
> "How much GPU memory is available for my next AI model?"

*Expected response: Current memory usage and available space*

**Check CUDA installation:**
> "Verify that CUDA is properly installed and working"

*Expected response: CUDA version, GPU accessibility, and framework compatibility*

## 🤖 AI/ML Workloads

### Framework Installation

**Set up TensorFlow:**
> "Install TensorFlow with GPU support on my Jetson Nano"

*Expected response: Installation progress and verification*

**Install PyTorch for computer vision:**
> "I need PyTorch for a computer vision project. Can you install it with CUDA support?"

*Expected response: PyTorch installation with GPU verification*

**Check installed frameworks:**
> "What AI frameworks are currently installed on my Jetson?"

*Expected response: List of installed frameworks with versions*

### Model Deployment

**Deploy a YOLOv5 model:**
> "Download and deploy YOLOv5 model for object detection"

*Command:*
```python
{
  "action": "deploy_model",
  "model_name": "yolov5s",
  "model_url": "https://github.com/ultralytics/yolov5/releases/download/v6.0/yolov5s.pt"
}
```

**Deploy custom ONNX model:**
> "I have a custom ONNX model at ~/models/my_model.onnx. Can you deploy it for inference?"

*Expected response: Model deployment with optimization suggestions*

**List deployed models:**
> "Show me all AI models currently deployed on my Jetson"

*Expected response: Model inventory with sizes and types*

### Performance Optimization

**Optimize model for inference:**
> "Convert my PyTorch model to TensorRT for faster inference"

*Expected response: Model conversion with performance benchmarks*

**Benchmark model performance:**
> "Run a performance benchmark on my deployed YOLOv5 model"

*Expected response: Latency, throughput, and resource utilization metrics*

**Memory optimization:**
> "My model is running out of GPU memory. Can you help optimize it?"

*Expected response: Memory analysis and optimization recommendations*

## 📦 Container Management

### Docker Setup

**Install Docker with GPU support:**
> "Set up Docker with NVIDIA GPU support for AI containers"

*Expected response: Docker and NVIDIA Container Toolkit installation*

**Run GPU-accelerated container:**
> "Start a TensorFlow container with GPU access for development"

*Command example:*
```bash
docker run --gpus all -it tensorflow/tensorflow:latest-gpu-jupyter
```

**Deploy model serving container:**
> "Deploy my trained model in a TensorFlow Serving container"

*Expected response: Container deployment with API endpoints*

### Container Orchestration

**Set up edge Kubernetes:**
> "Install K3s lightweight Kubernetes for edge AI workloads"

*Expected response: K3s installation and configuration*

**Deploy distributed inference:**
> "Deploy my object detection model across multiple Jetson devices"

*Expected response: Multi-node deployment configuration*

## 🗺️ System Administration

### Package Management

**System updates:**
> "Update all packages on my Jetson Nano to the latest versions"

*Expected response: Update process with package counts*

**Install development tools:**
> "Install essential development tools for AI projects"

*Expected response: Installation of build tools, editors, and utilities*

**Clean up disk space:**
> "My Jetson is running low on storage. Help me clean up unnecessary files"

*Expected response: Disk usage analysis and cleanup recommendations*

### Service Management

**Check system services:**
> "Show me the status of all important services on my Jetson"

*Expected response: Service list with status indicators*

**Restart networking:**
> "I'm having network issues. Can you restart the networking service?"

*Expected response: Service restart confirmation*

**Set up auto-start service:**
> "Configure my AI inference script to start automatically on boot"

*Expected response: Systemd service creation and enablement*

### Network Configuration

**Check network status:**
> "Show me my Jetson's network configuration and connectivity"

*Expected response: IP addresses, interfaces, and routing information*

**Configure static IP:**
> "Set up a static IP address for my Jetson Nano"

*Expected response: Network configuration update*

## 🔍 Monitoring and Diagnostics

### System Health

**Comprehensive health check:**
> "Run a complete health check on my Jetson Nano system"

*Expected response: CPU, memory, storage, temperature, and service status*

**Performance monitoring:**
> "Monitor system performance while I run my AI training job"

*Expected response: Real-time resource utilization tracking*

**Log analysis:**
> "Check system logs for any errors or warnings"

*Expected response: Log summary with important messages highlighted*

### AI Workload Monitoring

**Model inference monitoring:**
> "Monitor GPU utilization while my object detection model processes this video"

*Expected response: Real-time GPU metrics during inference*

**Training progress monitoring:**
> "Track system resources during my neural network training session"

*Expected response: CPU, GPU, memory, and thermal monitoring*

## 🔧 Development Workflows

### Jupyter Setup

**Remote Jupyter access:**
> "Set up Jupyter Notebook for remote AI development on my Jetson"

*Expected response: Jupyter installation and remote access configuration*

**Create AI development environment:**
> "Prepare a complete Python environment for computer vision development"

*Expected response: Package installation and environment setup*

### Model Development Pipeline

**Complete ML pipeline setup:**
> "Set up a complete machine learning pipeline from data preprocessing to model deployment"

*Expected response: End-to-end pipeline configuration*

**Automated model testing:**
> "Create an automated testing setup for my AI models"

*Expected response: Testing framework and CI/CD pipeline setup*

## 🚑 Emergency and Recovery

### System Recovery

**Emergency cool-down:**
> "My Jetson is overheating! Put it in emergency cool-down mode"

*Expected response: Immediate power mode reduction and fan control*

**Service recovery:**
> "My AI service crashed. Can you restart it and check what went wrong?"

*Expected response: Service restart with error analysis*

**System reboot:**
> "I need to reboot my Jetson safely. Can you do this properly?"

*Expected response: Graceful system shutdown and reboot*

### Backup and Restore

**Create system backup:**
> "Create a backup of my current Jetson configuration and models"

*Expected response: Backup creation with storage location*

**Restore from backup:**
> "Restore my Jetson from the backup I created last week"

*Expected response: System restoration process*

## 📊 Advanced Use Cases

### Edge AI Fleet Management

**Multi-device deployment:**
> "Deploy the same AI model across 5 different Jetson devices"

*Expected response: Coordinated deployment across multiple devices*

**Load balancing:**
> "Set up load balancing for inference requests across my Jetson cluster"

*Expected response: Load balancer configuration and traffic distribution*

### IoT Integration

**Sensor data processing:**
> "Set up real-time processing for data from my IoT sensors"

*Expected response: Data pipeline configuration with edge processing*

**Edge-to-cloud sync:**
> "Configure automatic synchronization of AI results to the cloud"

*Expected response: Cloud integration and data sync setup*

### Custom Applications

**Build custom AI application:**
> "Help me build a custom real-time video analytics application"

*Expected response: Application framework and component setup*

**Optimize for specific use case:**
> "Optimize my Jetson for autonomous drone applications"

*Expected response: Hardware and software optimization for drone use case*

---

## 📝 Tips for Effective Usage

### 1. Be Specific
- ✅ "Switch to 10W power mode for balanced performance"
- ❌ "Change power settings"

### 2. Provide Context
- ✅ "Install TensorFlow for my computer vision project"
- ❌ "Install TensorFlow"

### 3. Ask for Explanations
- ✅ "Explain why my GPU memory usage is high and how to optimize it"
- ❌ "Fix GPU memory"

### 4. Request Monitoring
- ✅ "Monitor temperatures while I run this intensive AI workload"
- ❌ "Check temperature"

### 5. Combine Operations
- ✅ "Install PyTorch, set up Jupyter, and create a sample computer vision notebook"
- Multiple related tasks in one request

These examples demonstrate the power and flexibility of JetsonMCP for managing edge AI systems through natural language interaction with Claude!
