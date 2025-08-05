"""
Performance Management Tool for Jetson Nano

Handles CPU/GPU governors, frequency scaling, and performance optimization.
"""

import logging
from typing import Any, Dict, List

from mcp.types import Tool

from .base import BaseTool

logger = logging.getLogger(__name__)


class PerformanceTool(BaseTool):
    """
    Tool for managing system performance and optimization.
    """

    TOOL_NAME = "manage_performance"

    async def list_tools(self) -> List[Tool]:
        """List all performance management tools."""
        return [
            Tool(
                name=self.TOOL_NAME,
                description="Manage CPU/GPU performance, governors, and system optimization on Jetson Nano",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": [
                                "get_cpu_info",
                                "get_gpu_freq",
                                "set_cpu_governor",
                                "optimize_performance",
                            ],
                            "description": "Performance management action to perform",
                        },
                        "governor": {
                            "type": "string",
                            "enum": ["performance", "powersave", "ondemand", "conservative"],
                            "description": "CPU governor to set",
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
        """Execute performance management commands."""
        if not await self.can_handle(tool_name):
            return [{"error": f"Cannot handle tool: {tool_name}"}]

        action = arguments.get("action")
        
        try:
            if action == "get_cpu_info":
                return await self._get_cpu_info()
            else:
                return [{"error": f"Action {action} not yet implemented"}]

        except Exception as e:
            logger.error(f"Performance tool execution failed: {e}")
            return [{"error": str(e), "action": action}]

    async def _get_cpu_info(self) -> List[Dict[str, Any]]:
        """Get CPU information and current frequencies."""
        try:
            result = await self.execute_command("cat /proc/cpuinfo | head -20")
            return [{"cpu_info": result["stdout"]}]
        except Exception as e:
            return [{"error": f"Failed to get CPU info: {e}"}]
