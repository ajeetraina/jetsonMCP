"""
Base Tool Class for JetsonMCP

Provides common functionality and SSH connection management for all Jetson management tools.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import paramiko
from mcp.types import Resource, Tool
from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import JetsonConfig

logger = logging.getLogger(__name__)


class SSHConnectionError(Exception):
    """Raised when SSH connection fails."""

    pass


class JetsonCommandError(Exception):
    """Raised when a command execution fails on Jetson."""

    pass


class BaseTool(ABC):
    """
    Abstract base class for all JetsonMCP tools.

    Provides SSH connection management, command execution, and common utilities
    for interacting with Jetson Nano systems.
    """

    def __init__(self, config: JetsonConfig):
        self.config = config
        self._ssh_client: Optional[paramiko.SSHClient] = None
        self._connection_lock = asyncio.Lock()

    async def _ensure_connection(self) -> paramiko.SSHClient:
        """
        Ensure SSH connection is established and return the client.

        Returns:
            paramiko.SSHClient: Active SSH connection

        Raises:
            SSHConnectionError: If connection cannot be established
        """
        async with self._connection_lock:
            if self._ssh_client is None or not self._is_connection_active():
                await self._connect()
            return self._ssh_client

    def _is_connection_active(self) -> bool:
        """Check if the current SSH connection is still active."""
        if self._ssh_client is None:
            return False

        try:
            # Try to get the transport
            transport = self._ssh_client.get_transport()
            return transport is not None and transport.is_active()
        except Exception:
            return False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _connect(self) -> None:
        """
        Establish SSH connection to Jetson Nano.

        Raises:
            SSHConnectionError: If connection fails after retries
        """
        try:
            if self.config.test_mode and self.config.mock_ssh_connections:
                logger.info("Mock SSH connection enabled for testing")
                return

            # Close existing connection if any
            if self._ssh_client:
                self._ssh_client.close()

            # Create new SSH client
            self._ssh_client = paramiko.SSHClient()

            # Configure host key policy
            if self.config.ssh.strict_host_checking:
                self._ssh_client.load_system_host_keys()
                self._ssh_client.load_host_keys(os.path.expanduser("~/.ssh/known_hosts"))
            else:
                self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect using appropriate authentication method
            connect_kwargs = {
                "hostname": self.config.ssh.host,
                "port": self.config.ssh.port,
                "username": self.config.ssh.username,
                "timeout": self.config.ssh.timeout,
            }

            if self.config.ssh.password:
                connect_kwargs["password"] = self.config.ssh.password
            elif self.config.ssh.key_path:
                connect_kwargs["key_filename"] = self.config.ssh.key_path
                if self.config.ssh.key_passphrase:
                    connect_kwargs["passphrase"] = self.config.ssh.key_passphrase

            # Execute connection in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._ssh_client.connect, **connect_kwargs)

            logger.info(f"Successfully connected to Jetson at {self.config.ssh.host}")

        except Exception as e:
            logger.error(f"Failed to connect to Jetson: {e}")
            if self._ssh_client:
                self._ssh_client.close()
                self._ssh_client = None
            raise SSHConnectionError(f"SSH connection failed: {e}")

    async def execute_command(
        self,
        command: str,
        timeout: int = 30,
        check_return_code: bool = True,
        sudo: bool = False,
    ) -> Dict[str, Any]:
        """
        Execute a command on the Jetson Nano via SSH.

        Args:
            command: Command to execute
            timeout: Command timeout in seconds
            check_return_code: Whether to raise exception on non-zero return code
            sudo: Whether to execute with sudo privileges

        Returns:
            Dict containing stdout, stderr, and return_code

        Raises:
            JetsonCommandError: If command execution fails
        """
        if self.config.test_mode and self.config.mock_ssh_connections:
            logger.info(f"Mock command execution: {command}")
            return {"stdout": "mock output", "stderr": "", "return_code": 0}

        try:
            ssh_client = await self._ensure_connection()

            # Prepare command with sudo if requested
            if sudo:
                command = f"sudo {command}"

            logger.debug(f"Executing command: {command}")

            # Execute command
            stdin, stdout, stderr = ssh_client.exec_command(command, timeout=timeout)

            # Read outputs
            stdout_data = stdout.read().decode("utf-8").strip()
            stderr_data = stderr.read().decode("utf-8").strip()
            return_code = stdout.channel.recv_exit_status()

            result = {
                "stdout": stdout_data,
                "stderr": stderr_data,
                "return_code": return_code,
            }

            logger.debug(
                f"Command result: return_code={return_code}, "
                f"stdout_len={len(stdout_data)}, stderr_len={len(stderr_data)}"
            )

            if check_return_code and return_code != 0:
                raise JetsonCommandError(
                    f"Command failed with return code {return_code}: {stderr_data}"
                )

            return result

        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            raise JetsonCommandError(f"Failed to execute command '{command}': {e}")

    async def file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists on the Jetson.

        Args:
            file_path: Path to check

        Returns:
            True if file exists, False otherwise
        """
        try:
            result = await self.execute_command(
                f"test -f {file_path}", check_return_code=False
            )
            return result["return_code"] == 0
        except Exception:
            return False

    async def directory_exists(self, dir_path: str) -> bool:
        """
        Check if a directory exists on the Jetson.

        Args:
            dir_path: Directory path to check

        Returns:
            True if directory exists, False otherwise
        """
        try:
            result = await self.execute_command(
                f"test -d {dir_path}", check_return_code=False
            )
            return result["return_code"] == 0
        except Exception:
            return False

    async def get_system_info(self) -> Dict[str, Any]:
        """
        Get basic system information from the Jetson.

        Returns:
            Dict containing system information
        """
        try:
            # Get multiple system information in parallel
            commands = {
                "hostname": "hostname",
                "uptime": "uptime",
                "kernel": "uname -r",
                "architecture": "uname -m",
                "cpu_info": "cat /proc/cpuinfo | grep 'model name' | head -1",
                "memory_info": "free -h",
                "disk_usage": "df -h /",
                "jetson_release": "cat /etc/nv_tegra_release 2>/dev/null || echo 'N/A'",
            }

            results = {}
            for key, cmd in commands.items():
                try:
                    result = await self.execute_command(cmd, check_return_code=False)
                    results[key] = result["stdout"] if result["return_code"] == 0 else "N/A"
                except Exception:
                    results[key] = "N/A"

            return results

        except Exception as e:
            logger.error(f"Failed to get system info: {e}")
            return {"error": str(e)}

    async def cleanup(self) -> None:
        """Clean up resources, especially SSH connections."""
        if self._ssh_client:
            try:
                self._ssh_client.close()
            except Exception as e:
                logger.warning(f"Error closing SSH connection: {e}")
            finally:
                self._ssh_client = None

    # Abstract methods that must be implemented by subclasses

    @abstractmethod
    async def list_tools(self) -> List[Tool]:
        """
        List all tools provided by this tool implementation.

        Returns:
            List of Tool objects
        """
        pass

    @abstractmethod
    async def can_handle(self, tool_name: str) -> bool:
        """
        Check if this tool can handle the given tool name.

        Args:
            tool_name: Name of the tool to check

        Returns:
            True if this tool can handle the request
        """
        pass

    @abstractmethod
    async def execute(self, tool_name: str, arguments: Dict[str, Any]) -> List[Any]:
        """
        Execute a tool with the given arguments.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments

        Returns:
            List of execution results
        """
        pass

    # Optional methods for resource management

    async def list_resources(self) -> List[Resource]:
        """
        List resources provided by this tool.

        Returns:
            List of Resource objects (empty by default)
        """
        return []

    async def can_read_resource(self, uri: str) -> bool:
        """
        Check if this tool can read the given resource URI.

        Args:
            uri: Resource URI to check

        Returns:
            False by default
        """
        return False

    async def read_resource(self, uri: str) -> str:
        """
        Read a resource by URI.

        Args:
            uri: Resource URI to read

        Returns:
            Resource content
        """
        raise NotImplementedError("Resource reading not implemented for this tool")
