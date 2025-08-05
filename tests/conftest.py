"""
Pytest configuration and fixtures for JetsonMCP tests.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from jetsonmcp.config import JetsonConfig
from jetsonmcp.tools.base import BaseTool


@pytest.fixture
def mock_config():
    """Provide a mock JetsonConfig for testing."""
    config = JetsonConfig(
        ssh={
            "host": "192.168.1.100",
            "username": "test_user",
            "password": "test_password",
            "port": 22,
            "timeout": 30,
            "retries": 3,
            "strict_host_checking": False,
        },
        test_mode=True,
        mock_ssh_connections=True,
    )
    return config


@pytest.fixture
def mock_ssh_client():
    """Provide a mock SSH client."""
    mock_client = MagicMock()
    mock_client.exec_command = AsyncMock()
    mock_client.close = MagicMock()
    return mock_client


@pytest.fixture
async def base_tool(mock_config):
    """Provide a base tool instance for testing."""
    
    class TestTool(BaseTool):
        async def list_tools(self):
            return []
        
        async def can_handle(self, tool_name: str) -> bool:
            return tool_name == "test_tool"
        
        async def execute(self, tool_name: str, arguments):
            return [{"test": "result"}]
    
    tool = TestTool(mock_config)
    yield tool
    await tool.cleanup()


@pytest.fixture
def mock_command_result():
    """Provide mock command execution results."""
    return {
        "stdout": "mock output",
        "stderr": "",
        "return_code": 0,
    }
