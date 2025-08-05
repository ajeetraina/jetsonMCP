"""
Monitoring Tool for Jetson Nano

Handles system monitoring, metrics collection, and alerting.
"""

import logging
from typing import Any, Dict, List

from mcp.types import Tool

from .base import BaseTool

logger = logging.getLogger(__name__)


class MonitoringTool(BaseTool):
    """
    Tool for system monitoring and metrics collection.
    """

    TOOL_NAME = "manage_monitoring"

    async def list_tools(self) -> List[Tool]:
        """List all monitoring tools."""
        return [
            Tool(
                name=self.TOOL_NAME,
                description="Monitor system resources, collect metrics, and manage alerts on Jetson Nano",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": [
                                "get_system_stats",
                                "monitor_resources",
                                "setup_prometheus",
                                "check_alerts",
                            ],
                            "description": "Monitoring action to perform",
                        },
                        "duration": {
                            "type": "integer",
                            "default": 60,
                            "description": "Monitoring duration in seconds",
                        },
                    },
                    "required": ["action"],
                },
            )
        ]

    async def can_handle(self, tool_name: str) -> bool:
        """Check if this tool can handle the given tool name."""
        return tool_name == self.TOOL_NAME

    async def execute(self, tool_name: str, arguments: Dict[str, Any]) -> List[Any]:
        """Execute monitoring commands."""
        if not await self.can_handle(tool_name):
            return [{"error": f"Cannot handle tool: {tool_name}"}]

        action = arguments.get("action")
        
        try:
            if action == "get_system_stats":
                return await self._get_system_stats()
            else:
                return [{"error": f"Action {action} not yet implemented"}]

        except Exception as e:
            logger.error(f"Monitoring tool execution failed: {e}")
            return [{"error": str(e), "action": action}]

    async def _get_system_stats(self) -> List[Dict[str, Any]]:
        """Get current system statistics."""
        try:
            # Get CPU usage
            cpu_result = await self.execute_command("top -bn1 | grep 'Cpu(s)' | head -1")
            
            # Get memory usage
            mem_result = await self.execute_command("free -m")
            
            return [{
                "cpu_usage": cpu_result["stdout"],
                "memory_usage": mem_result["stdout"]
            }]
        except Exception as e:
            return [{"error": f"Failed to get system stats: {e}"}]
