"""
Container Management Tool for Jetson Nano

Handles Docker container management, NVIDIA Container Toolkit,
and GPU-accelerated container operations.
"""

import logging
from typing import Any, Dict, List

from mcp.types import Tool

from .base import BaseTool

logger = logging.getLogger(__name__)


class ContainersTool(BaseTool):
    """
    Tool for managing Docker containers and GPU-accelerated workloads.
    """

    TOOL_NAME = "manage_containers"

    async def list_tools(self) -> List[Tool]:
        """List all container management tools."""
        return [
            Tool(
                name=self.TOOL_NAME,
                description="Manage Docker containers, images, and GPU-accelerated workloads on Jetson Nano",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": [
                                "check_docker",
                                "list_containers",
                                "list_images",
                                "run_container",
                                "stop_container",
                                "install_nvidia_runtime",
                                "test_gpu_container",
                            ],
                            "description": "Container management action to perform",
                        },
                        "container_name": {
                            "type": "string",
                            "description": "Name of container to manage",
                        },
                        "image_name": {
                            "type": "string",
                            "description": "Docker image name to run",
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
        """Execute container management commands."""
        if not await self.can_handle(tool_name):
            return [{"error": f"Cannot handle tool: {tool_name}"}]

        action = arguments.get("action")
        
        try:
            if action == "check_docker":
                return await self._check_docker()
            elif action == "list_containers":
                return await self._list_containers()
            elif action == "install_nvidia_runtime":
                return await self._install_nvidia_runtime()
            else:
                return [{"error": f"Action {action} not yet implemented"}]

        except Exception as e:
            logger.error(f"Container tool execution failed: {e}")
            return [{"error": str(e), "action": action}]

    async def _check_docker(self) -> List[Dict[str, Any]]:
        """Check Docker installation and status."""
        try:
            result = await self.execute_command("docker --version", check_return_code=False)
            if result["return_code"] == 0:
                return [{"docker_installed": True, "version": result["stdout"]}]
            else:
                return [{"docker_installed": False, "error": result["stderr"]}]
        except Exception as e:
            return [{"error": f"Failed to check Docker: {e}"}]

    async def _list_containers(self) -> List[Dict[str, Any]]:
        """List Docker containers."""
        try:
            result = await self.execute_command("docker ps -a")
            return [{"containers": result["stdout"]}]
        except Exception as e:
            return [{"error": f"Failed to list containers: {e}"}]

    async def _install_nvidia_runtime(self) -> List[Dict[str, Any]]:
        """Install NVIDIA Container Runtime."""
        return [{"message": "NVIDIA Container Runtime installation not yet implemented"}]
