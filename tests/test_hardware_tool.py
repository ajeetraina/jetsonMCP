"""
Tests for Hardware Tool functionality.
"""

import pytest
from unittest.mock import patch

from jetsonmcp.tools.hardware import HardwareTool


@pytest.mark.asyncio
async def test_hardware_tool_initialization(mock_config):
    """Test hardware tool initialization."""
    tool = HardwareTool(mock_config)
    assert tool.TOOL_NAME == "manage_hardware"
    
    tools = await tool.list_tools()
    assert len(tools) == 1
    assert tools[0].name == "manage_hardware"


@pytest.mark.asyncio
async def test_can_handle_tool(mock_config):
    """Test tool name handling."""
    tool = HardwareTool(mock_config)
    
    assert await tool.can_handle("manage_hardware") is True
    assert await tool.can_handle("other_tool") is False


@pytest.mark.asyncio
async def test_get_power_mode_mock(mock_config, mock_command_result):
    """Test power mode retrieval in mock mode."""
    tool = HardwareTool(mock_config)
    
    with patch.object(tool, 'execute_command', return_value=mock_command_result):
        result = await tool.execute("manage_hardware", {"action": "get_power_mode"})
        
        assert len(result) == 1
        assert isinstance(result[0], dict)


@pytest.mark.asyncio
async def test_invalid_action(mock_config):
    """Test handling of invalid actions."""
    tool = HardwareTool(mock_config)
    
    result = await tool.execute("manage_hardware", {"action": "invalid_action"})
    
    assert len(result) == 1
    assert "error" in result[0]
    assert "Unknown action" in result[0]["error"]


@pytest.mark.asyncio
async def test_missing_required_parameter(mock_config):
    """Test handling of missing required parameters."""
    tool = HardwareTool(mock_config)
    
    result = await tool.execute("manage_hardware", {"action": "set_power_mode"})
    
    assert len(result) == 1
    assert "error" in result[0]
    assert "power_mode parameter is required" in result[0]["error"]
