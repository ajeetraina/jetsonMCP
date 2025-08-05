# Changelog

All notable changes to JetsonMCP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure and architecture
- Core MCP server implementation
- Hardware management tool with power mode control
- AI workloads management with framework installation
- System administration tools
- Container management with Docker support
- Comprehensive configuration management
- SSH connection handling with retry logic
- Test suite with unit and integration tests
- CLI interface for server management
- Setup scripts for Jetson Nano preparation
- Claude Desktop integration scripts

### Changed
- N/A (initial release)

### Deprecated
- N/A (initial release)

### Removed
- N/A (initial release)

### Fixed
- N/A (initial release)

### Security
- SSH host key verification
- Secure credential handling
- Input validation and sanitization

## [1.0.0] - 2025-08-05

### Added
- **Core MCP Server**: Full MCP protocol implementation with tool routing
- **Hardware Tool**: 
  - Power mode management (MAXN, 5W, 10W modes)
  - Temperature monitoring across thermal zones
  - GPU information and memory tracking
  - Fan control and thermal management
  - GPIO pin control and monitoring
  - Voltage and current sensor readings
- **AI Workloads Tool**:
  - CUDA environment verification
  - ML framework installation (TensorFlow, PyTorch, OpenCV)
  - Model deployment and management
  - TensorRT integration
  - Jupyter Notebook setup
- **System Tool**:
  - Package management (apt install/remove/update)
  - Service management (systemctl operations)
  - System information and monitoring
  - Network configuration display
  - Disk space monitoring
- **Container Tool**: Docker management and NVIDIA runtime setup
- **Configuration System**: 
  - Pydantic-based validation
  - Environment variable loading
  - Multi-section configuration
- **Security Features**:
  - SSH key and password authentication
  - Connection timeout and retry logic
  - Command injection prevention
- **Development Tools**:
  - Comprehensive test suite
  - CLI interface
  - Setup and installation scripts
  - Claude Desktop integration

### Technical Details
- Python 3.8+ support
- Async/await based architecture
- SSH connection pooling and management
- Structured error handling and logging
- MCP resource providers
- Extensible tool architecture

### Documentation
- Complete README with setup instructions
- Architecture documentation
- Contributing guidelines
- API documentation for all tools
- Troubleshooting guides

### Testing
- Unit tests for all core components
- Integration tests for SSH operations
- Mock testing capabilities
- 85%+ code coverage target

---

**Legend**:
- `Added` for new features
- `Changed` for changes in existing functionality
- `Deprecated` for soon-to-be removed features
- `Removed` for now removed features
- `Fixed` for any bug fixes
- `Security` in case of vulnerabilities
