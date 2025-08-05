"""
JetsonMCP - MCP server for NVIDIA Jetson Nano systems

A comprehensive MCP server that enables AI assistants to manage and control
NVIDIA Jetson Nano systems through SSH connections, providing edge AI computing
capabilities, hardware optimization, and system administration.
"""

__version__ = "1.0.0"
__author__ = "Ajeet Singh Raina"
__email__ = "ajeetraina@gmail.com"
__license__ = "MIT"

from .server import create_server

__all__ = ["create_server", "__version__"]
