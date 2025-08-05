"""
JetPack Management Tool for Jetson Nano

Handles JetPack SDK installation, updates, and component management.
"""

import logging
from typing import Any, Dict, List

from mcp.types import Tool

from .base import BaseTool

logger = logging.getLogger(__name__)


class JetPackTool(BaseTool):
    """
    Tool for managing JetPack SDK and NVIDIA software components.
    """

    TOOL_NAME = "manage_jetpack"

    async def list_tools(self) -> List[Tool]:
        """List all JetPack management tools."""
        return [
            Tool(
                name=self.TOOL_NAME,
                description="Manage JetPack SDK, CUDA, and NVIDIA software components on Jetson Nano",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": [
                                "check_jetpack_version",
                                "list_components",
                                "update_jetpack",
                                "install_component",
                            ],
                            "description": "JetPack management action to perform",
                        },
                        "component": {
                            "type": "string",
                            "description": "JetPack component to manage",
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
        """Execute JetPack management commands."""
        if not await self.can_handle(tool_name):
            return [{"error": f"Cannot handle tool: {tool_name}"}]

        action = arguments.get("action")
        
        try:
            if action == "check_jetpack_version":
                return await self._check_jetpack_version()
            else:
                return [{"error": f"Action {action} not yet implemented"}]

        except Exception as e:
            logger.error(f"JetPack tool execution failed: {e}")
            return [{"error": str(e), "action": action}]

    async def _check_jetpack_version(self) -> List[Dict[str, Any]]:
        """Check current JetPack version."""
        try:
            result = await self.execute_command("cat /etc/nv_tegra_release", check_return_code=False)
            if result["return_code"] == 0:
                return [{"jetpack_info": result["stdout"]}]
            else:
                return [{"jetpack_info": "Not available"}]
        except Exception as e:
            return [{"error": f"Failed to check JetPack version: {e}"}]
