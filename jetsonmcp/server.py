"""
JetsonMCP Server Implementation

Main MCP server that provides AI assistants with tools to manage and control
NVIDIA Jetson Nano systems via SSH connections.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool

from .config import JetsonConfig
from .tools import (
    AIWorkloadsTool,
    ContainersTool,
    HardwareTool,
    JetPackTool,
    MonitoringTool,
    PerformanceTool,
    SecurityTool,
    StorageTool,
    SystemTool,
)
from .utils.logger import setup_logger

logger = logging.getLogger(__name__)


class JetsonMCPServer:
    """
    Main JetsonMCP server that orchestrates all Jetson Nano management tools.
    """

    def __init__(self, config: JetsonConfig):
        self.config = config
        self.server = Server("jetsonmcp")
        self._tools: Dict[str, Any] = {}
        self._setup_tools()
        self._register_handlers()

    def _setup_tools(self) -> None:
        """Initialize all Jetson management tools."""
        try:
            # Core system management
            self._tools["system"] = SystemTool(self.config)
            self._tools["hardware"] = HardwareTool(self.config)
            self._tools["performance"] = PerformanceTool(self.config)
            self._tools["storage"] = StorageTool(self.config)

            # AI and edge computing tools
            self._tools["ai_workloads"] = AIWorkloadsTool(self.config)
            self._tools["jetpack"] = JetPackTool(self.config)

            # Container and orchestration
            self._tools["containers"] = ContainersTool(self.config)

            # Monitoring and security
            self._tools["monitoring"] = MonitoringTool(self.config)
            self._tools["security"] = SecurityTool(self.config)

            logger.info("All JetsonMCP tools initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize tools: {e}")
            raise

    def _register_handlers(self) -> None:
        """Register MCP protocol handlers."""

        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List all available tools."""
            tools = []
            for tool_name, tool_instance in self._tools.items():
                tools.extend(await tool_instance.list_tools())
            return tools

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[Any]:
            """Handle tool execution requests."""
            logger.info(f"Executing tool: {name} with arguments: {arguments}")

            # Route tool calls to appropriate handlers
            for tool_instance in self._tools.values():
                if await tool_instance.can_handle(name):
                    try:
                        result = await tool_instance.execute(name, arguments)
                        return result
                    except Exception as e:
                        logger.error(f"Tool execution failed for {name}: {e}")
                        return [{"error": str(e), "tool": name}]

            logger.error(f"No handler found for tool: {name}")
            return [{"error": f"Unknown tool: {name}"}]

        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """List available system resources and status."""
            resources = []
            for tool_instance in self._tools.values():
                if hasattr(tool_instance, "list_resources"):
                    resources.extend(await tool_instance.list_resources())
            return resources

        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read system resource information."""
            for tool_instance in self._tools.values():
                if hasattr(tool_instance, "can_read_resource") and hasattr(
                    tool_instance, "read_resource"
                ):
                    if await tool_instance.can_read_resource(uri):
                        return await tool_instance.read_resource(uri)

            logger.error(f"No handler found for resource: {uri}")
            return f"Resource not found: {uri}"

    async def start(self) -> None:
        """Start the MCP server."""
        logger.info("Starting JetsonMCP Server...")

        # Validate connection to Jetson Nano
        system_tool = self._tools.get("system")
        if system_tool:
            try:
                await system_tool.validate_connection()
                logger.info("Successfully connected to Jetson Nano")
            except Exception as e:
                logger.error(f"Failed to connect to Jetson Nano: {e}")
                raise

        logger.info("JetsonMCP Server started successfully")

    async def stop(self) -> None:
        """Stop the MCP server and cleanup resources."""
        logger.info("Stopping JetsonMCP Server...")

        # Cleanup all tools
        for tool_name, tool_instance in self._tools.items():
            try:
                if hasattr(tool_instance, "cleanup"):
                    await tool_instance.cleanup()
            except Exception as e:
                logger.warning(f"Error cleaning up {tool_name}: {e}")

        logger.info("JetsonMCP Server stopped")


def create_server(config_path: Optional[str] = None) -> JetsonMCPServer:
    """
    Create and configure a JetsonMCP server instance.

    Args:
        config_path: Optional path to configuration file

    Returns:
        Configured JetsonMCPServer instance
    """
    # Setup logging
    setup_logger()

    # Load configuration
    config = JetsonConfig.load(config_path)

    # Create server instance
    server = JetsonMCPServer(config)

    return server


async def main() -> None:
    """
    Main entry point for running JetsonMCP server.
    """
    try:
        # Create server
        jetson_server = create_server()

        # Start server components
        await jetson_server.start()

        # Run MCP stdio server
        async with stdio_server() as (read_stream, write_stream):
            await jetson_server.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="jetsonmcp",
                    server_version="1.0.0",
                    capabilities=jetson_server.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )

    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        if "jetson_server" in locals():
            await jetson_server.stop()


if __name__ == "__main__":
    # Run the server
    asyncio.run(main())
