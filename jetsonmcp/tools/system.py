"""
System Management Tool for Jetson Nano

Handles basic system administration tasks like package management,
service control, updates, and system information.
"""

import logging
from typing import Any, Dict, List

from mcp.types import Tool

from .base import BaseTool

logger = logging.getLogger(__name__)


class SystemTool(BaseTool):
    """
    Tool for basic system administration tasks on Jetson Nano.
    """

    TOOL_NAME = "manage_system"

    async def list_tools(self) -> List[Tool]:
        """List all system management tools."""
        return [
            Tool(
                name=self.TOOL_NAME,
                description="Manage Jetson Nano system including packages, services, updates, and system information",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": [
                                "get_system_info",
                                "update_packages",
                                "install_package",
                                "remove_package",
                                "list_services",
                                "start_service",
                                "stop_service",
                                "restart_service",
                                "get_service_status",
                                "check_disk_space",
                                "get_network_info",
                                "reboot_system",
                                "shutdown_system",
                            ],
                            "description": "System management action to perform",
                        },
                        "package_name": {
                            "type": "string",
                            "description": "Name of package to install/remove",
                        },
                        "service_name": {
                            "type": "string",
                            "description": "Name of service to manage",
                        },
                        "confirm": {
                            "type": "boolean",
                            "default": False,
                            "description": "Confirm destructive operations",
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
        """Execute system management commands."""
        if not await self.can_handle(tool_name):
            return [{"error": f"Cannot handle tool: {tool_name}"}]

        action = arguments.get("action")
        
        try:
            if action == "get_system_info":
                return await self._get_system_info()
            elif action == "update_packages":
                return await self._update_packages()
            elif action == "install_package":
                package_name = arguments.get("package_name")
                if not package_name:
                    return [{"error": "package_name parameter is required"}]
                return await self._install_package(package_name)
            elif action == "remove_package":
                package_name = arguments.get("package_name")
                if not package_name:
                    return [{"error": "package_name parameter is required"}]
                return await self._remove_package(package_name)
            elif action == "list_services":
                return await self._list_services()
            elif action == "start_service":
                service_name = arguments.get("service_name")
                if not service_name:
                    return [{"error": "service_name parameter is required"}]
                return await self._start_service(service_name)
            elif action == "stop_service":
                service_name = arguments.get("service_name")
                if not service_name:
                    return [{"error": "service_name parameter is required"}]
                return await self._stop_service(service_name)
            elif action == "restart_service":
                service_name = arguments.get("service_name")
                if not service_name:
                    return [{"error": "service_name parameter is required"}]
                return await self._restart_service(service_name)
            elif action == "get_service_status":
                service_name = arguments.get("service_name")
                if not service_name:
                    return [{"error": "service_name parameter is required"}]
                return await self._get_service_status(service_name)
            elif action == "check_disk_space":
                return await self._check_disk_space()
            elif action == "get_network_info":
                return await self._get_network_info()
            elif action == "reboot_system":
                confirm = arguments.get("confirm", False)
                return await self._reboot_system(confirm)
            elif action == "shutdown_system":
                confirm = arguments.get("confirm", False)
                return await self._shutdown_system(confirm)
            else:
                return [{"error": f"Unknown action: {action}"}]

        except Exception as e:
            logger.error(f"System tool execution failed: {e}")
            return [{"error": str(e), "action": action}]

    async def validate_connection(self) -> None:
        """Validate SSH connection to Jetson Nano."""
        try:
            result = await self.execute_command("whoami", timeout=10)
            if result["return_code"] != 0:
                raise Exception("SSH connection test failed")
            logger.info(f"Connected to Jetson as user: {result['stdout']}")
        except Exception as e:
            raise Exception(f"Cannot connect to Jetson Nano: {e}")

    async def _get_system_info(self) -> List[Dict[str, Any]]:
        """Get comprehensive system information."""
        try:
            system_info = await self.get_system_info()
            
            # Add additional system details
            additional_commands = {
                "load_average": "uptime | awk '{print $10, $11, $12}'",
                "users_logged_in": "who | wc -l",
                "processes_running": "ps aux | wc -l",
                "network_interfaces": "ip addr show | grep -E '^[0-9]+:' | awk '{print $2}' | tr -d ':'",
            }

            for key, command in additional_commands.items():
                try:
                    result = await self.execute_command(command, check_return_code=False)
                    if result["return_code"] == 0:
                        system_info[key] = result["stdout"].strip()
                except Exception:
                    system_info[key] = "N/A"

            return [system_info]

        except Exception as e:
            return [{"error": f"Failed to get system info: {e}"}]

    async def _update_packages(self) -> List[Dict[str, Any]]:
        """Update system packages."""
        try:
            # Update package lists
            update_result = await self.execute_command("sudo apt update", sudo=True, timeout=300)
            if update_result["return_code"] != 0:
                return [{"error": "Failed to update package lists", "details": update_result["stderr"]}]

            # Get list of upgradeable packages
            upgradeable_result = await self.execute_command("apt list --upgradeable 2>/dev/null | wc -l", check_return_code=False)
            upgradeable_count = 0
            if upgradeable_result["return_code"] == 0:
                try:
                    upgradeable_count = max(0, int(upgradeable_result["stdout"].strip()) - 1)  # Subtract header line
                except ValueError:
                    pass

            if upgradeable_count == 0:
                return [{
                    "success": True,
                    "message": "System is up to date",
                    "upgradeable_packages": 0,
                    "update_output": update_result["stdout"]
                }]

            # Upgrade packages
            upgrade_result = await self.execute_command("sudo apt upgrade -y", sudo=True, timeout=1800)  # 30 minutes timeout
            
            return [{
                "success": upgrade_result["return_code"] == 0,
                "message": f"Updated {upgradeable_count} packages" if upgrade_result["return_code"] == 0 else "Package upgrade failed",
                "upgradeable_packages": upgradeable_count,
                "update_output": update_result["stdout"],
                "upgrade_output": upgrade_result["stdout"] if upgrade_result["return_code"] == 0 else upgrade_result["stderr"]
            }]

        except Exception as e:
            return [{"error": f"Failed to update packages: {e}"}]

    async def _install_package(self, package_name: str) -> List[Dict[str, Any]]:
        """Install a package using apt."""
        try:
            # Check if package exists
            search_result = await self.execute_command(f"apt-cache show {package_name}", check_return_code=False)
            if search_result["return_code"] != 0:
                return [{"error": f"Package '{package_name}' not found in repositories"}]

            # Install package
            install_result = await self.execute_command(f"sudo apt install -y {package_name}", sudo=True, timeout=600)
            
            if install_result["return_code"] == 0:
                # Verify installation
                verify_result = await self.execute_command(f"dpkg -l | grep {package_name}", check_return_code=False)
                installed = verify_result["return_code"] == 0
                
                return [{
                    "success": True,
                    "message": f"Package '{package_name}' installed successfully",
                    "package_name": package_name,
                    "verified_installed": installed,
                    "install_output": install_result["stdout"]
                }]
            else:
                return [{
                    "success": False,
                    "message": f"Failed to install package '{package_name}'",
                    "package_name": package_name,
                    "error_output": install_result["stderr"]
                }]

        except Exception as e:
            return [{"error": f"Failed to install package: {e}"}]

    async def _remove_package(self, package_name: str) -> List[Dict[str, Any]]:
        """Remove a package using apt."""
        try:
            # Check if package is installed
            check_result = await self.execute_command(f"dpkg -l | grep {package_name}", check_return_code=False)
            if check_result["return_code"] != 0:
                return [{"message": f"Package '{package_name}' is not installed"}]

            # Remove package
            remove_result = await self.execute_command(f"sudo apt remove -y {package_name}", sudo=True, timeout=300)
            
            if remove_result["return_code"] == 0:
                # Verify removal
                verify_result = await self.execute_command(f"dpkg -l | grep {package_name}", check_return_code=False)
                removed = verify_result["return_code"] != 0
                
                return [{
                    "success": True,
                    "message": f"Package '{package_name}' removed successfully",
                    "package_name": package_name,
                    "verified_removed": removed,
                    "remove_output": remove_result["stdout"]
                }]
            else:
                return [{
                    "success": False,
                    "message": f"Failed to remove package '{package_name}'",
                    "package_name": package_name,
                    "error_output": remove_result["stderr"]
                }]

        except Exception as e:
            return [{"error": f"Failed to remove package: {e}"}]

    async def _list_services(self) -> List[Dict[str, Any]]:
        """List system services."""
        try:
            # Get all services
            result = await self.execute_command("systemctl list-units --type=service --all --no-pager")
            
            services = []
            lines = result["stdout"].strip().split('\n')
            
            # Skip header lines and parse service information
            for line in lines[1:]:  # Skip header
                if line.strip() and not line.startswith('●') and not line.startswith('UNIT'):
                    parts = line.split()
                    if len(parts) >= 4:
                        try:
                            service_info = {
                                "name": parts[0],
                                "load": parts[1],
                                "active": parts[2],
                                "sub": parts[3],
                                "description": " ".join(parts[4:]) if len(parts) > 4 else ""
                            }
                            services.append(service_info)
                        except IndexError:
                            continue

            # Get count of services by status
            active_count = len([s for s in services if s.get("active") == "active"])
            inactive_count = len([s for s in services if s.get("active") == "inactive"])
            failed_count = len([s for s in services if s.get("active") == "failed"])

            return [{
                "total_services": len(services),
                "active_services": active_count,
                "inactive_services": inactive_count,
                "failed_services": failed_count,
                "services": services[:50]  # Limit to first 50 for readability
            }]

        except Exception as e:
            return [{"error": f"Failed to list services: {e}"}]

    async def _start_service(self, service_name: str) -> List[Dict[str, Any]]:
        """Start a system service."""
        try:
            result = await self.execute_command(f"sudo systemctl start {service_name}", sudo=True)
            
            if result["return_code"] == 0:
                # Check service status
                status = await self._get_service_status(service_name)
                return [{
                    "success": True,
                    "message": f"Service '{service_name}' started successfully",
                    "service_name": service_name,
                    "status": status[0] if status else {}
                }]
            else:
                return [{
                    "success": False,
                    "message": f"Failed to start service '{service_name}'",
                    "service_name": service_name,
                    "error": result["stderr"]
                }]

        except Exception as e:
            return [{"error": f"Failed to start service: {e}"}]

    async def _stop_service(self, service_name: str) -> List[Dict[str, Any]]:
        """Stop a system service."""
        try:
            result = await self.execute_command(f"sudo systemctl stop {service_name}", sudo=True)
            
            if result["return_code"] == 0:
                # Check service status
                status = await self._get_service_status(service_name)
                return [{
                    "success": True,
                    "message": f"Service '{service_name}' stopped successfully",
                    "service_name": service_name,
                    "status": status[0] if status else {}
                }]
            else:
                return [{
                    "success": False,
                    "message": f"Failed to stop service '{service_name}'",
                    "service_name": service_name,
                    "error": result["stderr"]
                }]

        except Exception as e:
            return [{"error": f"Failed to stop service: {e}"}]

    async def _restart_service(self, service_name: str) -> List[Dict[str, Any]]:
        """Restart a system service."""
        try:
            result = await self.execute_command(f"sudo systemctl restart {service_name}", sudo=True)
            
            if result["return_code"] == 0:
                # Check service status
                status = await self._get_service_status(service_name)
                return [{
                    "success": True,
                    "message": f"Service '{service_name}' restarted successfully",
                    "service_name": service_name,
                    "status": status[0] if status else {}
                }]
            else:
                return [{
                    "success": False,
                    "message": f"Failed to restart service '{service_name}'",
                    "service_name": service_name,
                    "error": result["stderr"]
                }]

        except Exception as e:
            return [{"error": f"Failed to restart service: {e}"}]

    async def _get_service_status(self, service_name: str) -> List[Dict[str, Any]]:
        """Get status of a system service."""
        try:
            result = await self.execute_command(f"systemctl status {service_name} --no-pager", check_return_code=False)
            
            # Parse systemctl status output
            status_info = {
                "service_name": service_name,
                "return_code": result["return_code"],
                "raw_output": result["stdout"]
            }

            # Extract key information from output
            lines = result["stdout"].split('\n') if result["stdout"] else []
            for line in lines:
                line = line.strip()
                if 'Active:' in line:
                    status_info["active_status"] = line.replace('Active:', '').strip()
                elif 'Loaded:' in line:
                    status_info["loaded_status"] = line.replace('Loaded:', '').strip()
                elif 'Main PID:' in line:
                    status_info["main_pid"] = line.replace('Main PID:', '').strip()
                elif 'Memory:' in line:
                    status_info["memory_usage"] = line.replace('Memory:', '').strip()

            return [status_info]

        except Exception as e:
            return [{"error": f"Failed to get service status: {e}"}]

    async def _check_disk_space(self) -> List[Dict[str, Any]]:
        """Check disk space usage."""
        try:
            result = await self.execute_command("df -h")
            
            disk_info = {
                "raw_output": result["stdout"],
                "filesystems": []
            }

            lines = result["stdout"].strip().split('\n')
            # Skip header line
            for line in lines[1:]:
                parts = line.split()
                if len(parts) >= 6:
                    try:
                        filesystem_info = {
                            "filesystem": parts[0],
                            "size": parts[1],
                            "used": parts[2],
                            "available": parts[3],
                            "use_percent": parts[4],
                            "mounted_on": parts[5]
                        }
                        disk_info["filesystems"].append(filesystem_info)
                    except IndexError:
                        continue

            # Check for low disk space warnings
            warnings = []
            for fs in disk_info["filesystems"]:
                try:
                    if fs["use_percent"].endswith('%'):
                        usage_percent = int(fs["use_percent"][:-1])
                        if usage_percent > 90:
                            warnings.append(f"High disk usage on {fs['mounted_on']}: {fs['use_percent']}")
                        elif usage_percent > 80:
                            warnings.append(f"Disk usage warning on {fs['mounted_on']}: {fs['use_percent']}")
                except (ValueError, KeyError):
                    continue

            disk_info["warnings"] = warnings

            return [disk_info]

        except Exception as e:
            return [{"error": f"Failed to check disk space: {e}"}]

    async def _get_network_info(self) -> List[Dict[str, Any]]:
        """Get network interface information."""
        try:
            network_info = {}

            # Get IP addresses
            ip_result = await self.execute_command("ip addr show")
            network_info["ip_addresses"] = ip_result["stdout"]

            # Get routing table
            route_result = await self.execute_command("ip route", check_return_code=False)
            if route_result["return_code"] == 0:
                network_info["routing_table"] = route_result["stdout"]

            # Get network interfaces
            interfaces_result = await self.execute_command("ls /sys/class/net/")
            if interfaces_result["return_code"] == 0:
                interfaces = interfaces_result["stdout"].strip().split()
                network_info["interfaces"] = interfaces

                # Get status for each interface
                interface_status = {}
                for interface in interfaces:
                    try:
                        status_result = await self.execute_command(f"cat /sys/class/net/{interface}/operstate", check_return_code=False)
                        if status_result["return_code"] == 0:
                            interface_status[interface] = status_result["stdout"].strip()
                    except Exception:
                        continue
                
                network_info["interface_status"] = interface_status

            # Get DNS configuration
            dns_result = await self.execute_command("cat /etc/resolv.conf", check_return_code=False)
            if dns_result["return_code"] == 0:
                network_info["dns_config"] = dns_result["stdout"]

            return [network_info]

        except Exception as e:
            return [{"error": f"Failed to get network info: {e}"}]

    async def _reboot_system(self, confirm: bool) -> List[Dict[str, Any]]:
        """Reboot the system."""
        if not confirm:
            return [{
                "error": "Reboot requires confirmation. Set 'confirm': true to proceed.",
                "warning": "This will restart the Jetson Nano system!"
            }]

        try:
            # Schedule reboot with a small delay to allow response to be sent
            result = await self.execute_command("sudo shutdown -r +1 'System reboot requested via JetsonMCP'", sudo=True)
            
            if result["return_code"] == 0:
                return [{
                    "success": True,
                    "message": "System reboot scheduled in 1 minute",
                    "warning": "The Jetson Nano will restart shortly!"
                }]
            else:
                return [{
                    "success": False,
                    "message": "Failed to schedule system reboot",
                    "error": result["stderr"]
                }]

        except Exception as e:
            return [{"error": f"Failed to reboot system: {e}"}]

    async def _shutdown_system(self, confirm: bool) -> List[Dict[str, Any]]:
        """Shutdown the system."""
        if not confirm:
            return [{
                "error": "Shutdown requires confirmation. Set 'confirm': true to proceed.",
                "warning": "This will power off the Jetson Nano system!"
            }]

        try:
            # Schedule shutdown with a small delay to allow response to be sent
            result = await self.execute_command("sudo shutdown -h +1 'System shutdown requested via JetsonMCP'", sudo=True)
            
            if result["return_code"] == 0:
                return [{
                    "success": True,
                    "message": "System shutdown scheduled in 1 minute",
                    "warning": "The Jetson Nano will power off shortly!"
                }]
            else:
                return [{
                    "success": False,
                    "message": "Failed to schedule system shutdown",
                    "error": result["stderr"]
                }]

        except Exception as e:
            return [{"error": f"Failed to shutdown system: {e}"}]
