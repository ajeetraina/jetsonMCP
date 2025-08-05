"""
JetsonMCP Command Line Interface

Provides command-line utilities for JetsonMCP management.
"""

import asyncio
import click

from .config import JetsonConfig
from .server import create_server
from .utils.logger import setup_logger


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.pass_context
def cli(ctx, debug):
    """JetsonMCP - MCP server for NVIDIA Jetson Nano systems."""
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug
    
    # Setup logging
    log_level = "DEBUG" if debug else "INFO"
    setup_logger(log_level=log_level)


@cli.command()
@click.option("--config", "-c", help="Path to configuration file")
@click.pass_context
def start(ctx, config):
    """Start the JetsonMCP server."""
    async def run_server():
        from .server import main
        await main()
    
    asyncio.run(run_server())


@cli.command()
@click.option("--config", "-c", help="Path to configuration file")
@click.pass_context
def test_connection(ctx, config):
    """Test SSH connection to Jetson Nano."""
    async def test():
        try:
            jetson_config = JetsonConfig.load(config)
            server = create_server(config)
            await server.start()
            click.echo("✅ Connection successful!")
            await server.stop()
        except Exception as e:
            click.echo(f"❌ Connection failed: {e}")
    
    asyncio.run(test())


@cli.command()
@click.option("--config", "-c", help="Path to configuration file")
def validate_config(config):
    """Validate JetsonMCP configuration."""
    try:
        jetson_config = JetsonConfig.load(config)
        issues = jetson_config.validate_configuration()
        
        if not issues:
            click.echo("✅ Configuration is valid!")
        else:
            click.echo("❌ Configuration issues found:")
            for issue in issues:
                click.echo(f"  - {issue}")
    except Exception as e:
        click.echo(f"❌ Configuration error: {e}")


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
