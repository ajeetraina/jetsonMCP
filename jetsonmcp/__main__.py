"""
JetsonMCP Main Entry Point

Allows running JetsonMCP as a module: python -m jetsonmcp.server
"""

import asyncio
from .server import main

if __name__ == "__main__":
    asyncio.run(main())
