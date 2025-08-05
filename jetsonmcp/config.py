"""
JetsonMCP Configuration Management

Handles loading and validation of configuration settings for Jetson Nano connections
and system management parameters.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator


class SSHConfig(BaseModel):
    """SSH connection configuration."""

    host: str = Field(..., description="Jetson Nano IP address or hostname")
    username: str = Field(..., description="SSH username")
    password: Optional[str] = Field(None, description="SSH password")
    key_path: Optional[str] = Field(None, description="Path to SSH private key")
    key_passphrase: Optional[str] = Field(None, description="SSH key passphrase")
    port: int = Field(22, description="SSH port")
    timeout: int = Field(30, description="SSH connection timeout in seconds")
    retries: int = Field(3, description="SSH connection retry attempts")
    strict_host_checking: bool = Field(True, description="Enable SSH host key checking")

    @validator("host")
    def validate_host(cls, v):
        if not v or v.strip() == "":
            raise ValueError("Host cannot be empty")
        return v.strip()

    @validator("username")
    def validate_username(cls, v):
        if not v or v.strip() == "":
            raise ValueError("Username cannot be empty")
        return v.strip()

    @validator("password", "key_path")
    def validate_auth_method(cls, v, values):
        # At least one authentication method must be provided
        if not v and not values.get("password") and not values.get("key_path"):
            raise ValueError("Either password or key_path must be provided")
        return v


class PowerConfig(BaseModel):
    """Power management configuration."""

    default_mode: int = Field(0, description="Default power mode (0=MAXN, 1=5W, 2=10W)")
    temp_warning: int = Field(70, description="Temperature warning threshold (°C)")
    temp_critical: int = Field(80, description="Temperature critical threshold (°C)")
    fan_auto: bool = Field(True, description="Enable automatic fan control")
    fan_min_speed: int = Field(50, description="Minimum fan speed percentage")
    fan_max_speed: int = Field(100, description="Maximum fan speed percentage")

    @validator("default_mode")
    def validate_power_mode(cls, v):
        if v not in [0, 1, 2]:
            raise ValueError("Power mode must be 0 (MAXN), 1 (5W), or 2 (10W)")
        return v

    @validator("temp_warning", "temp_critical")
    def validate_temperature(cls, v):
        if v < 0 or v > 100:
            raise ValueError("Temperature must be between 0 and 100°C")
        return v


class CudaConfig(BaseModel):
    """CUDA and GPU configuration."""

    visible_devices: str = Field("0", description="CUDA visible devices")
    memory_fraction: float = Field(0.8, description="GPU memory fraction for frameworks")
    tensorrt_enabled: bool = Field(True, description="Enable TensorRT optimization")
    tensorrt_precision: str = Field("FP16", description="TensorRT precision mode")

    @validator("memory_fraction")
    def validate_memory_fraction(cls, v):
        if v <= 0 or v > 1:
            raise ValueError("GPU memory fraction must be between 0 and 1")
        return v

    @validator("tensorrt_precision")
    def validate_tensorrt_precision(cls, v):
        valid_precisions = ["FP32", "FP16", "INT8"]
        if v not in valid_precisions:
            raise ValueError(f"TensorRT precision must be one of {valid_precisions}")
        return v


class DockerConfig(BaseModel):
    """Docker and container configuration."""

    enabled: bool = Field(True, description="Enable Docker management")
    buildx_enabled: bool = Field(True, description="Enable Docker Buildx")
    registry: str = Field("localhost:5000", description="Container registry URL")
    registry_enabled: bool = Field(False, description="Enable private registry")
    nvidia_runtime_enabled: bool = Field(True, description="Enable NVIDIA Container Runtime")


class MonitoringConfig(BaseModel):
    """Monitoring and logging configuration."""

    enabled: bool = Field(True, description="Enable system monitoring")
    interval: int = Field(30, description="Monitoring interval in seconds")
    metrics_retention_days: int = Field(7, description="Metrics retention period")
    log_level: str = Field("INFO", description="Logging level")
    log_file: Optional[str] = Field(
        "/var/log/jetsonmcp.log", description="Log file path"
    )
    prometheus_enabled: bool = Field(False, description="Enable Prometheus metrics")
    prometheus_port: int = Field(9090, description="Prometheus port")

    @validator("log_level")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()


class JetPackConfig(BaseModel):
    """JetPack and NVIDIA software configuration."""

    version: str = Field("4.6.1", description="JetPack version")
    auto_update: bool = Field(False, description="Enable automatic JetPack updates")
    nvidia_driver_version: str = Field("35.4.1", description="NVIDIA driver version")
    cuda_version: str = Field("11.4", description="CUDA version")
    l4t_version: str = Field("32.7.1", description="L4T version")


class SecurityConfig(BaseModel):
    """Security and hardening configuration."""

    firewall_enabled: bool = Field(True, description="Enable firewall management")
    allowed_ports: List[int] = Field(
        [22, 80, 443, 8080], description="Allowed firewall ports"
    )
    automatic_updates: bool = Field(True, description="Enable automatic system updates")
    security_patches_only: bool = Field(
        True, description="Install security patches only"
    )


class JetsonConfig(BaseModel):
    """
    Main JetsonMCP configuration class that combines all configuration sections.
    """

    ssh: SSHConfig
    power: PowerConfig = Field(default_factory=PowerConfig)
    cuda: CudaConfig = Field(default_factory=CudaConfig)
    docker: DockerConfig = Field(default_factory=DockerConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    jetpack: JetPackConfig = Field(default_factory=JetPackConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)

    # Development and testing
    debug_mode: bool = Field(False, description="Enable debug mode")
    development_mode: bool = Field(False, description="Enable development mode")
    test_mode: bool = Field(False, description="Enable test mode")
    mock_ssh_connections: bool = Field(False, description="Mock SSH connections for testing")

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "JetsonConfig":
        """
        Load configuration from environment variables and optional config file.

        Args:
            config_path: Optional path to .env file

        Returns:
            JetsonConfig instance
        """
        # Load environment variables
        if config_path and Path(config_path).exists():
            load_dotenv(config_path)
        else:
            # Try to load .env from current directory
            env_path = Path(".env")
            if env_path.exists():
                load_dotenv(env_path)

        # Build configuration from environment variables
        ssh_config = SSHConfig(
            host=os.getenv("JETSON_HOST", ""),
            username=os.getenv("JETSON_USERNAME", ""),
            password=os.getenv("JETSON_PASSWORD"),
            key_path=os.getenv("JETSON_SSH_KEY_PATH"),
            key_passphrase=os.getenv("JETSON_SSH_PASSPHRASE"),
            port=int(os.getenv("JETSON_SSH_PORT", "22")),
            timeout=int(os.getenv("JETSON_SSH_TIMEOUT", "30")),
            retries=int(os.getenv("JETSON_SSH_RETRIES", "3")),
            strict_host_checking=os.getenv("SSH_STRICT_HOST_CHECKING", "true").lower()
            == "true",
        )

        power_config = PowerConfig(
            default_mode=int(os.getenv("JETSON_POWER_MODE", "0")),
            temp_warning=int(os.getenv("JETSON_TEMP_WARNING", "70")),
            temp_critical=int(os.getenv("JETSON_TEMP_CRITICAL", "80")),
            fan_auto=os.getenv("JETSON_FAN_AUTO", "true").lower() == "true",
            fan_min_speed=int(os.getenv("JETSON_FAN_MIN_SPEED", "50")),
            fan_max_speed=int(os.getenv("JETSON_FAN_MAX_SPEED", "100")),
        )

        cuda_config = CudaConfig(
            visible_devices=os.getenv("CUDA_VISIBLE_DEVICES", "0"),
            memory_fraction=float(os.getenv("GPU_MEMORY_FRACTION", "0.8")),
            tensorrt_enabled=os.getenv("TENSORRT_ENABLED", "true").lower() == "true",
            tensorrt_precision=os.getenv("TENSORRT_PRECISION", "FP16"),
        )

        docker_config = DockerConfig(
            enabled=os.getenv("DOCKER_ENABLED", "true").lower() == "true",
            buildx_enabled=os.getenv("DOCKER_BUILDX_ENABLED", "true").lower() == "true",
            registry=os.getenv("DOCKER_REGISTRY", "localhost:5000"),
            registry_enabled=os.getenv("DOCKER_REGISTRY_ENABLED", "false").lower()
            == "true",
            nvidia_runtime_enabled=os.getenv("NVIDIA_RUNTIME_ENABLED", "true").lower()
            == "true",
        )

        monitoring_config = MonitoringConfig(
            enabled=os.getenv("MONITORING_ENABLED", "true").lower() == "true",
            interval=int(os.getenv("MONITORING_INTERVAL", "30")),
            metrics_retention_days=int(os.getenv("METRICS_RETENTION_DAYS", "7")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE", "/var/log/jetsonmcp.log"),
            prometheus_enabled=os.getenv("PROMETHEUS_ENABLED", "false").lower()
            == "true",
            prometheus_port=int(os.getenv("PROMETHEUS_PORT", "9090")),
        )

        jetpack_config = JetPackConfig(
            version=os.getenv("JETPACK_VERSION", "4.6.1"),
            auto_update=os.getenv("JETPACK_AUTO_UPDATE", "false").lower() == "true",
            nvidia_driver_version=os.getenv("NVIDIA_DRIVER_VERSION", "35.4.1"),
            cuda_version=os.getenv("CUDA_VERSION", "11.4"),
            l4t_version=os.getenv("L4T_VERSION", "32.7.1"),
        )

        security_config = SecurityConfig(
            firewall_enabled=os.getenv("FIREWALL_ENABLED", "true").lower() == "true",
            allowed_ports=[
                int(port.strip())
                for port in os.getenv("ALLOWED_PORTS", "22,80,443,8080").split(",")
            ],
            automatic_updates=os.getenv("AUTOMATIC_UPDATES", "true").lower() == "true",
            security_patches_only=os.getenv("SECURITY_PATCHES_ONLY", "true").lower()
            == "true",
        )

        return cls(
            ssh=ssh_config,
            power=power_config,
            cuda=cuda_config,
            docker=docker_config,
            monitoring=monitoring_config,
            jetpack=jetpack_config,
            security=security_config,
            debug_mode=os.getenv("DEBUG_MODE", "false").lower() == "true",
            development_mode=os.getenv("DEVELOPMENT_MODE", "false").lower() == "true",
            test_mode=os.getenv("TEST_MODE", "false").lower() == "true",
            mock_ssh_connections=os.getenv("MOCK_SSH_CONNECTIONS", "false").lower()
            == "true",
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self.dict()

    def validate_configuration(self) -> List[str]:
        """
        Validate the current configuration and return any issues.

        Returns:
            List of validation error messages
        """
        issues = []

        # Validate SSH authentication
        if not self.ssh.password and not self.ssh.key_path:
            issues.append("Either SSH password or key path must be provided")

        # Validate SSH key path exists
        if self.ssh.key_path and not Path(self.ssh.key_path).exists():
            issues.append(f"SSH key file not found: {self.ssh.key_path}")

        # Validate power settings
        if self.power.temp_warning >= self.power.temp_critical:
            issues.append("Temperature warning must be less than critical threshold")

        # Validate monitoring settings
        if self.monitoring.interval < 10:
            issues.append("Monitoring interval should be at least 10 seconds")

        return issues
