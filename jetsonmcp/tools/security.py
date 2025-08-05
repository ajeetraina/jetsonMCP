"""
Security Management Tool for Jetson Nano

Handles firewall configuration, SSH security, and system hardening.
"""

import logging
from typing import Any, Dict, List

from mcp.types import Tool

from .base import BaseTool

logger = logging.getLogger(__name__)


class SecurityTool(BaseTool):
    """
    Tool for managing system security and hardening.
    """

    TOOL_NAME = "manage_security"

    async def list_tools(self) -> List[Tool]:
        """List all security management tools."""
        return [
            Tool(
                name=self.TOOL_NAME,
                description="Manage firewall, SSH security, and system hardening on Jetson Nano",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": [
                                "check_firewall",
                                "configure_firewall",
                                "check_ssh_security",
                                "harden_system",
                            ],
                            "description": "Security management action to perform",
                        },
                        "port": {
                            "type": "integer",
                            "description": "Port number for firewall rules",
                        },
                        "protocol": {
                            "type": "string",
                            "enum": ["tcp", "udp"],
                            "description": "Protocol for firewall rules",
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
        """Execute security management commands."""
        if not await self.can_handle(tool_name):
            return [{"error": f"Cannot handle tool: {tool_name}"}]

        action = arguments.get("action")
        
        try:
            if action == "check_firewall":
                return await self._check_firewall()
            else:
                return [{"error": f"Action {action} not yet implemented"}]

        except Exception as e:
            logger.error(f"Security tool execution failed: {e}")
            return [{"error": str(e), "action": action}]

    async def _check_firewall(self) -> List[Dict[str, Any]]:
        """Check firewall status."""
        try:
            result = await self.execute_command("sudo ufw status", sudo=True, check_return_code=False)
            return [{"firewall_status": result["stdout"]}]
        except Exception as e:
            return [{"error": f"Failed to check firewall: {e}"}]
