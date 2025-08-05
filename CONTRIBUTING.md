# Contributing to JetsonMCP

Thank you for your interest in contributing to JetsonMCP! This guide will help you get started with contributing to the project.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Access to an NVIDIA Jetson Nano for testing
- Basic knowledge of Python, SSH, and edge computing concepts
- Familiarity with MCP (Model Context Protocol)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/jetsonMCP.git
   cd jetsonMCP
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Development Dependencies**
   ```bash
   make install-dev
   # Or manually:
   pip install -e ".[dev,test]"
   pre-commit install
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Jetson Nano connection details
   ```

5. **Test Your Setup**
   ```bash
   make test-conn
   make test
   ```

## 🛠️ Development Workflow

### Code Organization

```
jetsonmcp/
├── server.py          # Main MCP server implementation
├── config.py          # Configuration management
├── tools/             # Individual tool implementations
│   ├── base.py        # Base tool class
│   ├── hardware.py    # Hardware management
│   ├── ai_workloads.py # AI/ML operations
│   ├── containers.py  # Docker management
│   └── ...           # Other specialized tools
├── utils/             # Utility functions
└── cli.py            # Command-line interface
```

### Making Changes

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Follow the existing code style and patterns
   - Add docstrings to all functions and classes
   - Include type hints where appropriate
   - Update tests for any new functionality

3. **Test Your Changes**
   ```bash
   make test           # Run all tests
   make test-cov       # Run with coverage
   make lint          # Check code style
   make format        # Auto-format code
   ```

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add new hardware monitoring feature"
   ```

   Follow [Conventional Commits](https://conventionalcommits.org/):
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `test:` for test additions/modifications
   - `refactor:` for code refactoring

5. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

## 🧪 Testing

### Test Categories

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test tool interactions with real Jetson systems
- **Mock Tests**: Test with simulated SSH connections

### Running Tests

```bash
# All tests
make test

# Unit tests only
make test-unit

# Integration tests (requires Jetson connection)
make test-integration

# With coverage
make test-cov
```

### Writing Tests

```python
import pytest
from jetsonmcp.tools.hardware import HardwareTool
from jetsonmcp.config import JetsonConfig

@pytest.mark.asyncio
async def test_hardware_tool_power_mode():
    """Test power mode management."""
    config = JetsonConfig.load()
    config.test_mode = True  # Enable mock mode
    
    tool = HardwareTool(config)
    result = await tool.execute("manage_hardware", {"action": "get_power_mode"})
    
    assert len(result) == 1
    assert "current_power_mode" in result[0]
```

## 📝 Documentation

### Code Documentation

- Use clear, descriptive docstrings for all public functions
- Include parameter descriptions and return value information
- Add usage examples for complex functions

```python
async def deploy_model(self, model_name: str, model_path: str) -> List[Dict[str, Any]]:
    """
    Deploy an AI model for inference on Jetson Nano.
    
    Args:
        model_name: Unique name for the deployed model
        model_path: Local path to the model file
        
    Returns:
        List containing deployment status and model information
        
    Example:
        >>> tool = AIWorkloadsTool(config)
        >>> result = await tool.deploy_model("yolov5", "/models/yolov5.onnx")
        >>> print(result[0]["success"])
        True
    """
```

### README Updates

- Update the main README.md if you add new features
- Include configuration examples for new options
- Add troubleshooting information for common issues

## 🎯 Contributing Guidelines

### What We're Looking For

- **New Tools**: Additional management capabilities for Jetson systems
- **Hardware Support**: Support for other Jetson platforms (AGX Xavier, Orin)
- **AI Framework Integration**: Support for new ML frameworks and optimization tools
- **Performance Improvements**: Optimizations for SSH connections and command execution
- **Documentation**: Better examples, tutorials, and troubleshooting guides
- **Testing**: Improved test coverage and integration tests

### Code Style

- Follow PEP 8 style guidelines
- Use Black for code formatting (`make format`)
- Use isort for import sorting
- Maximum line length: 88 characters
- Use type hints where possible

### Error Handling

- Always include proper error handling in tools
- Return structured error responses with helpful messages
- Log errors appropriately using the logging framework

```python
try:
    result = await self.execute_command(command)
    return [{"success": True, "data": result["stdout"]}]
except JetsonCommandError as e:
    logger.error(f"Command failed: {e}")
    return [{"error": str(e), "command": command}]
```

## 🐛 Reporting Issues

### Bug Reports

When reporting bugs, please include:

- JetsonMCP version
- Jetson Nano hardware details (RAM, storage, JetPack version)
- Python version and operating system
- Complete error messages and stack traces
- Steps to reproduce the issue
- Expected vs. actual behavior

### Feature Requests

For feature requests, please describe:

- The problem you're trying to solve
- Your proposed solution
- Any alternative solutions you've considered
- How this would benefit other users

## 📋 Pull Request Process

1. **Pre-submission Checklist**
   - [ ] All tests pass
   - [ ] Code is properly formatted
   - [ ] Documentation is updated
   - [ ] Commit messages follow conventional format
   - [ ] No merge conflicts with main branch

2. **Pull Request Description**
   - Clear title describing the change
   - Detailed description of what changed and why
   - Reference any related issues
   - Include testing instructions if applicable

3. **Review Process**
   - At least one maintainer review required
   - All CI checks must pass
   - Address any feedback from reviewers

## 🤝 Community

### Communication

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Email**: ajeetraina@gmail.com for direct contact

### Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please:

- Be respectful and constructive in all interactions
- Welcome newcomers and help them get started
- Focus on what's best for the community
- Show empathy towards other community members

## 🏆 Recognition

Contributors will be:

- Listed in the project's AUTHORS file
- Mentioned in release notes for significant contributions
- Invited to join the maintainer team for sustained contributions

## 📚 Resources

- [NVIDIA Jetson Documentation](https://developer.nvidia.com/embedded/jetson-nano-developer-kit)
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)
- [Python AsyncIO Documentation](https://docs.python.org/3/library/asyncio.html)
- [Paramiko SSH Library Documentation](https://docs.paramiko.org/)

---

Thank you for contributing to JetsonMCP! Your efforts help make edge AI development more accessible to everyone. 🚀
