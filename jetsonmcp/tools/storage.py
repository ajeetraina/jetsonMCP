"""
Storage Management Tool for Jetson Nano

Handles storage optimization, swap configuration, and disk management.
"""

import logging
from typing import Any, Dict, List

from mcp.types import Tool

from .base import BaseTool

logger = logging.getLogger(__name__)


class StorageTool(BaseTool):
    """
    Tool for managing storage and disk operations.
    """

    TOOL_NAME = "manage_storage"

    async def list_tools(self) -> List[Tool]:
        """List all storage management tools."""
        return [
            Tool(
                name=self.TOOL_NAME,
                description="Manage storage, swap, and disk operations on Jetson Nano",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": [
                                "check_disk_usage",
                                "manage_swap",
                                "optimize_storage",
                                "mount_nvme",
                            ],
                            "description": "Storage management action to perform",
                        },
                        "swap_size": {
                            "type": "string",
                            "description": "Swap file size (e.g., '4G', '2G')",
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
        """Execute storage management commands."""
        if not await self.can_handle(tool_name):
            return [{"error": f"Cannot handle tool: {tool_name}"}]

        action = arguments.get("action")
        
        try:
            if action == "check_disk_usage":
                return await self._check_disk_usage()
            else:
                return [{"error": f"Action {action} not yet implemented"}]

        except Exception as e:
            logger.error(f"Storage tool execution failed: {e}")
            return [{"error": str(e), "action": action}]

    async def _check_disk_usage(self) -> List[Dict[str, Any]]:
        """Check disk usage across all filesystems."""
        try:
            result = await self.execute_command("df -h")
            return [{"disk_usage": result["stdout"]}]
        except Exception as e:
            return [{"error": f"Failed to check disk usage: {e}"}]
