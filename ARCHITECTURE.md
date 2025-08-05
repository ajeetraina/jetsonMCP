# JetsonMCP Architecture

This document describes the technical architecture and design decisions behind JetsonMCP.

## Overview

JetsonMCP is built using a hexagonal (ports and adapters) architecture that separates business logic from external concerns. This design allows for easy testing, maintainability, and extensibility.

## Core Components

### 1. MCP Server (`server.py`)

**Responsibility**: Main orchestration layer that handles MCP protocol communication and coordinates between tools.

**Key Features**:
- MCP protocol compliance
- Tool registration and routing
- Resource management
- Error handling and recovery

### 2. Configuration Management (`config.py`)

**Responsibility**: Centralized configuration handling with validation and type safety.

**Features**:
- Pydantic-based validation
- Environment variable loading
- Configuration sections for different domains
- Runtime configuration validation

### 3. Tool Architecture (`tools/`)

**Base Tool (`base.py`)**:
- Abstract base class for all tools
- SSH connection management
- Common command execution patterns
- Resource cleanup handling

**Specialized Tools**:
- `HardwareTool`: Power management, temperature monitoring, GPIO control
- `AIWorkloadsTool`: ML framework management, model deployment
- `ContainersTool`: Docker and GPU container management
- `SystemTool`: Basic system administration
- Additional tools for specific domains

### 4. Utility Layer (`utils/`)

**Logger (`logger.py`)**:
- Centralized logging configuration
- Multiple output handlers (console, file)
- Level-based filtering

## Design Patterns

### 1. Command Pattern

Each tool implements a command pattern where:
- Actions are discrete, named operations
- Parameters are validated using JSON schemas
- Results are consistently structured

```python
async def execute(self, tool_name: str, arguments: Dict[str, Any]) -> List[Any]:
    action = arguments.get("action")
    if action == "get_temperature":
        return await self._get_temperature()
    # ... other actions
```

### 2. Factory Pattern

The server uses a factory pattern to instantiate and manage tools:

```python
def _setup_tools(self) -> None:
    self._tools["hardware"] = HardwareTool(self.config)
    self._tools["ai_workloads"] = AIWorkloadsTool(self.config)
    # ... other tools
```

### 3. Strategy Pattern

SSH connection management uses different strategies based on configuration:
- Password authentication
- Key-based authentication
- Mock connections for testing

### 4. Observer Pattern

Resource monitoring and state management use observer patterns for:
- Temperature alerts
- Resource utilization thresholds
- System state changes

## Data Flow

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Claude AI     │───▶│  MCP Server  │───▶│   Tool Router   │
│                 │    │              │    │                 │
└─────────────────┘    └──────────────┘    └─────────────────┘
                                                      │
                                                      ▼
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Jetson Nano   │◀───│  SSH Client  │◀───│  Specific Tool  │
│                 │    │              │    │                 │
└─────────────────┘    └──────────────┘    └─────────────────┘
```

1. **Request Phase**:
   - Claude sends MCP request to server
   - Server validates and routes to appropriate tool
   - Tool executes SSH commands on Jetson

2. **Processing Phase**:
   - Commands execute on Jetson hardware
   - Results are processed and structured
   - Error handling and recovery

3. **Response Phase**:
   - Structured data returned through tool
   - Server formats MCP response
   - Claude receives actionable information

## Error Handling Strategy

### 1. Layered Error Handling

```
Application Layer  ──▶ User-friendly messages
     │
Tool Layer        ──▶ Domain-specific errors  
     │
SSH Layer         ──▶ Connection/command errors
     │
Transport Layer   ──▶ Network/protocol errors
```

### 2. Error Types

- **Configuration Errors**: Invalid settings, missing credentials
- **Connection Errors**: SSH failures, network issues
- **Command Errors**: Failed command execution, permission issues
- **Hardware Errors**: Device-specific failures, thermal issues

### 3. Recovery Strategies

- **Retry Logic**: Exponential backoff for transient failures
- **Fallback Commands**: Alternative approaches for common operations
- **Graceful Degradation**: Partial functionality when components fail

## Security Architecture

### 1. Authentication

- SSH key-based authentication (preferred)
- Password authentication (fallback)
- Host key verification
- Connection timeouts

### 2. Authorization

- Sudo privilege management
- Command validation and sanitization
- Path traversal protection
- Resource access controls

### 3. Data Protection

- Credential encryption in transit
- Secure credential storage
- Audit logging
- Session management

## Performance Considerations

### 1. Connection Pooling

- SSH connection reuse
- Connection health monitoring
- Automatic reconnection
- Resource cleanup

### 2. Command Optimization

- Batched operations where possible
- Caching for expensive operations
- Parallel execution for independent tasks
- Result streaming for large outputs

### 3. Resource Management

- Memory-conscious data structures
- Lazy loading for large datasets
- Garbage collection optimization
- Connection lifecycle management

## Testing Strategy

### 1. Test Categories

- **Unit Tests**: Individual function testing
- **Integration Tests**: Tool interaction testing
- **End-to-End Tests**: Full workflow testing
- **Performance Tests**: Load and stress testing

### 2. Mock Strategy

```python
# Mock SSH connections for unit testing
if self.config.test_mode and self.config.mock_ssh_connections:
    return {"stdout": "mock output", "stderr": "", "return_code": 0}
```

### 3. Test Infrastructure

- Pytest-based test suite
- Docker containers for isolation
- CI/CD integration
- Coverage reporting

## Extensibility

### 1. Adding New Tools

1. Inherit from `BaseTool`
2. Implement required abstract methods
3. Register in server configuration
4. Add tests and documentation

### 2. Hardware Platform Support

- Abstract hardware interfaces
- Platform-specific implementations
- Feature detection and fallbacks
- Configuration-driven behavior

### 3. Protocol Extensions

- MCP resource providers
- Custom message types
- Streaming capabilities
- Notification systems

## Deployment Architecture

### 1. Development Setup

```
Developer Machine     Jetson Nano
┌───────────────┐    ┌──────────────┐
│   Claude      │    │              │
│   Desktop     │    │   SSH Server │
│               │    │              │
│   JetsonMCP   │───▶│   Hardware   │
│   Server      │    │   AI Worklds │
│               │    │   Containers │
└───────────────┘    └──────────────┘
```

### 2. Production Setup

```
Edge Network
┌─────────────────────────────────────────┐
│  Edge Gateway          Jetson Cluster   │
│  ┌─────────────┐      ┌──────────────┐  │
│  │  JetsonMCP  │─────▶│  Jetson #1   │  │
│  │   Proxy     │      │  Jetson #2   │  │
│  │             │      │  Jetson #3   │  │
│  └─────────────┘      └──────────────┘  │
└─────────────────────────────────────────┘
                │
                ▼
         Cloud Management
         ┌──────────────┐
         │   Monitoring │
         │   Analytics  │
         │   Updates    │
         └──────────────┘
```

## Future Architecture Considerations

### 1. Scalability

- Multi-Jetson management
- Load balancing across devices
- Distributed model serving
- Edge cluster orchestration

### 2. AI/ML Pipeline Integration

- MLOps workflow integration
- Model versioning and deployment
- A/B testing frameworks
- Performance monitoring

### 3. IoT Integration

- Sensor data ingestion
- Real-time processing pipelines
- Edge-to-cloud data sync
- Device fleet management

## Conclusion

JetsonMCP's architecture prioritizes:

- **Modularity**: Clear separation of concerns
- **Testability**: Comprehensive testing strategy
- **Extensibility**: Easy addition of new capabilities
- **Reliability**: Robust error handling and recovery
- **Security**: Multi-layered security approach
- **Performance**: Optimized for edge computing constraints

This architecture provides a solid foundation for edge AI system management while remaining flexible enough to adapt to future requirements.
