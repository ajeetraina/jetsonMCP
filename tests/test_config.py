"""
Tests for JetsonMCP configuration management.
"""

import pytest
from pydantic import ValidationError

from jetsonmcp.config import JetsonConfig, SSHConfig


def test_ssh_config_validation():
    """Test SSH configuration validation."""
    # Valid configuration
    config = SSHConfig(
        host="192.168.1.100",
        username="jetson",
        password="password123"
    )
    assert config.host == "192.168.1.100"
    assert config.username == "jetson"

    # Invalid - empty host
    with pytest.raises(ValidationError):
        SSHConfig(
            host="",
            username="jetson",
            password="password123"
        )

    # Invalid - empty username
    with pytest.raises(ValidationError):
        SSHConfig(
            host="192.168.1.100",
            username="",
            password="password123"
        )


def test_jetson_config_validation():
    """Test full JetsonConfig validation."""
    ssh_config = SSHConfig(
        host="192.168.1.100",
        username="jetson",
        password="password123"
    )
    
    config = JetsonConfig(ssh=ssh_config)
    
    # Test validation
    issues = config.validate_configuration()
    assert isinstance(issues, list)


def test_config_to_dict():
    """Test configuration serialization."""
    ssh_config = SSHConfig(
        host="192.168.1.100",
        username="jetson",
        password="password123"
    )
    
    config = JetsonConfig(ssh=ssh_config)
    config_dict = config.to_dict()
    
    assert isinstance(config_dict, dict)
    assert "ssh" in config_dict
    assert config_dict["ssh"]["host"] == "192.168.1.100"
