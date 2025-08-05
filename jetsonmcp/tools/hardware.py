"""
Hardware Management Tool for Jetson Nano

Handles power management, temperature monitoring, GPU control, and other
hardware-specific features of the NVIDIA Jetson Nano.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List

from mcp.types import Resource, Tool

from .base import BaseTool

logger = logging.getLogger(__name__)


class HardwareTool(BaseTool):
    """
    Tool for managing Jetson Nano hardware features including power management,
    thermal monitoring, GPIO control, and GPU management.
    """

    TOOL_NAME = "manage_hardware"
    
    # Power modes mapping
    POWER_MODES = {
        0: {"name": "MAXN", "watts": 15, "description": "Maximum performance mode"},
        1: {"name": "5W", "watts": 5, "description": "Power efficient mode"},
        2: {"name": "10W", "watts": 10, "description": "Balanced performance mode"},
    }

    async def list_tools(self) -> List[Tool]:
        """List all hardware management tools."""
        return [
            Tool(
                name=self.TOOL_NAME,
                description="Manage Jetson Nano hardware including power modes, temperature monitoring, GPU control, and fan management",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": [
                                "get_power_mode",
                                "set_power_mode",
                                "get_temperature",
                                "get_gpu_info",
                                "get_gpu_memory",
                                "control_fan",
                                "get_fan_status",
                                "monitor_thermal",
                                "get_hardware_info",
                                "check_power_supply",
                                "get_voltage_readings",
                                "control_gpio",
                                "list_gpio_pins",
                            ],
                            "description": "Hardware management action to perform",
                        },
                        "power_mode": {
                            "type": "integer",
                            "enum": [0, 1, 2],
                            "description": "Power mode: 0=MAXN(15W), 1=5W, 2=10W",
                        },
                        "fan_speed": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 100,
                            "description": "Fan speed percentage (0-100)",
                        },
                        "gpio_pin": {
                            "type": "integer",
                            "description": "GPIO pin number",
                        },
                        "gpio_state": {
                            "type": "string",
                            "enum": ["high", "low", "input", "output"],
                            "description": "GPIO pin state or mode",
                        },
                        "duration": {
                            "type": "integer",
                            "default": 30,
                            "description": "Monitoring duration in seconds",
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
        """Execute hardware management commands."""
        if not await self.can_handle(tool_name):
            return [{"error": f"Cannot handle tool: {tool_name}"}]

        action = arguments.get("action")
        
        try:
            if action == "get_power_mode":
                return await self._get_power_mode()
            elif action == "set_power_mode":
                power_mode = arguments.get("power_mode")
                if power_mode is None:
                    return [{"error": "power_mode parameter is required"}]
                return await self._set_power_mode(power_mode)
            elif action == "get_temperature":
                return await self._get_temperature()
            elif action == "get_gpu_info":
                return await self._get_gpu_info()
            elif action == "get_gpu_memory":
                return await self._get_gpu_memory()
            elif action == "control_fan":
                fan_speed = arguments.get("fan_speed")
                if fan_speed is None:
                    return [{"error": "fan_speed parameter is required"}]
                return await self._control_fan(fan_speed)
            elif action == "get_fan_status":
                return await self._get_fan_status()
            elif action == "monitor_thermal":
                duration = arguments.get("duration", 30)
                return await self._monitor_thermal(duration)
            elif action == "get_hardware_info":
                return await self._get_hardware_info()
            elif action == "check_power_supply":
                return await self._check_power_supply()
            elif action == "get_voltage_readings":
                return await self._get_voltage_readings()
            elif action == "control_gpio":
                gpio_pin = arguments.get("gpio_pin")
                gpio_state = arguments.get("gpio_state")
                if gpio_pin is None or gpio_state is None:
                    return [{"error": "gpio_pin and gpio_state parameters are required"}]
                return await self._control_gpio(gpio_pin, gpio_state)
            elif action == "list_gpio_pins":
                return await self._list_gpio_pins()
            else:
                return [{"error": f"Unknown action: {action}"}]

        except Exception as e:
            logger.error(f"Hardware tool execution failed: {e}")
            return [{"error": str(e), "action": action}]

    async def _get_power_mode(self) -> List[Dict[str, Any]]:
        """Get current power mode."""
        try:
            # Get current power mode using nvpmodel
            result = await self.execute_command("sudo nvpmodel -q", check_return_code=False)
            
            if result["return_code"] != 0:
                return [{"error": "Failed to query power mode", "details": result["stderr"]}]

            output = result["stdout"]
            current_mode = None
            
            # Parse nvpmodel output
            for line in output.split('\n'):
                if 'NV Power Mode' in line and 'ID' in line:
                    try:
                        # Extract mode ID from output like "NV Power Mode: MAXN with ID: 0"
                        current_mode = int(line.split('ID:')[-1].strip())
                        break
                    except (ValueError, IndexError):
                        continue

            if current_mode is not None and current_mode in self.POWER_MODES:
                mode_info = self.POWER_MODES[current_mode]
                return [{
                    "current_power_mode": current_mode,
                    "mode_name": mode_info["name"],
                    "power_watts": mode_info["watts"],
                    "description": mode_info["description"],
                    "available_modes": self.POWER_MODES,
                    "raw_output": output
                }]
            else:
                return [{
                    "error": "Could not parse power mode",
                    "raw_output": output,
                    "available_modes": self.POWER_MODES
                }]

        except Exception as e:
            return [{"error": f"Failed to get power mode: {e}"}]

    async def _set_power_mode(self, power_mode: int) -> List[Dict[str, Any]]:
        """Set power mode."""
        try:
            if power_mode not in self.POWER_MODES:
                return [{
                    "error": f"Invalid power mode: {power_mode}",
                    "available_modes": self.POWER_MODES
                }]

            # Set power mode using nvpmodel
            result = await self.execute_command(f"sudo nvpmodel -m {power_mode}", sudo=True)
            
            if result["return_code"] != 0:
                return [{"error": "Failed to set power mode", "details": result["stderr"]}]

            # Verify the change
            current_mode_result = await self._get_power_mode()
            
            mode_info = self.POWER_MODES[power_mode]
            return [{
                "success": True,
                "message": f"Power mode set to {mode_info['name']} ({power_mode})",
                "new_mode": power_mode,
                "mode_name": mode_info["name"],
                "power_watts": mode_info["watts"],
                "verification": current_mode_result
            }]

        except Exception as e:
            return [{"error": f"Failed to set power mode: {e}"}]

    async def _get_temperature(self) -> List[Dict[str, Any]]:
        """Get temperature readings from various sensors."""
        try:
            temperatures = {}
            
            # Read temperature from thermal zones
            thermal_zones = [
                "/sys/class/thermal/thermal_zone0/temp",  # CPU
                "/sys/class/thermal/thermal_zone1/temp",  # GPU
                "/sys/class/thermal/thermal_zone2/temp",  # AUX
                "/sys/class/thermal/thermal_zone3/temp",  # PLL
            ]
            
            zone_names = ["CPU", "GPU", "AUX", "PLL"]
            
            for i, zone_path in enumerate(thermal_zones):
                try:
                    result = await self.execute_command(f"cat {zone_path} 2>/dev/null", check_return_code=False)
                    if result["return_code"] == 0 and result["stdout"]:
                        # Temperature is in millidegrees Celsius
                        temp_mc = int(result["stdout"].strip())
                        temp_c = temp_mc / 1000.0
                        temperatures[zone_names[i]] = {
                            "celsius": temp_c,
                            "fahrenheit": (temp_c * 9/5) + 32,
                            "zone_path": zone_path
                        }
                except (ValueError, IndexError):
                    continue

            # Check thermal throttling status
            throttle_result = await self.execute_command(
                "cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq 2>/dev/null", 
                check_return_code=False
            )
            
            current_freq = None
            if throttle_result["return_code"] == 0:
                try:
                    current_freq = int(throttle_result["stdout"].strip()) / 1000  # Convert to MHz
                except ValueError:
                    pass

            # Get temperature thresholds from config
            warning_temp = self.config.power.temp_warning
            critical_temp = self.config.power.temp_critical
            
            # Analyze temperature status
            max_temp = max([t["celsius"] for t in temperatures.values()]) if temperatures else 0
            temp_status = "normal"
            if max_temp >= critical_temp:
                temp_status = "critical"
            elif max_temp >= warning_temp:
                temp_status = "warning"

            return [{
                "temperatures": temperatures,
                "max_temperature_celsius": max_temp,
                "temperature_status": temp_status,
                "thresholds": {
                    "warning": warning_temp,
                    "critical": critical_temp
                },
                "current_cpu_frequency_mhz": current_freq,
                "thermal_throttling": current_freq is not None and current_freq < 1000  # Assume throttling if < 1GHz
            }]

        except Exception as e:
            return [{"error": f"Failed to get temperature: {e}"}]

    async def _get_gpu_info(self) -> List[Dict[str, Any]]:
        """Get GPU information and status."""
        try:
            gpu_info = {}
            
            # Try to get GPU info using nvidia-smi (might not be available on Jetson)
            nvidia_smi_result = await self.execute_command("nvidia-smi --query-gpu=name,driver_version,memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu --format=csv,noheader,nounits", check_return_code=False)
            
            if nvidia_smi_result["return_code"] == 0:
                try:
                    gpu_data = nvidia_smi_result["stdout"].strip().split(',')
                    gpu_info = {
                        "name": gpu_data[0].strip(),
                        "driver_version": gpu_data[1].strip(),
                        "memory_total_mb": int(gpu_data[2].strip()),
                        "memory_used_mb": int(gpu_data[3].strip()),
                        "memory_free_mb": int(gpu_data[4].strip()),
                        "utilization_percent": int(gpu_data[5].strip()),
                        "temperature_celsius": int(gpu_data[6].strip()) if gpu_data[6].strip() != 'N/A' else None
                    }
                except (ValueError, IndexError):
                    pass

            # Get Tegra GPU information
            tegra_info = await self.execute_command("cat /proc/device-tree/model 2>/dev/null", check_return_code=False)
            if tegra_info["return_code"] == 0:
                gpu_info["tegra_model"] = tegra_info["stdout"].strip()

            # Get GPU memory info from /proc/meminfo
            meminfo_result = await self.execute_command("cat /proc/meminfo | grep -E '(MemTotal|MemFree|MemAvailable)'")
            if meminfo_result["return_code"] == 0:
                mem_lines = meminfo_result["stdout"].strip().split('\n')
                for line in mem_lines:
                    if 'MemTotal' in line:
                        gpu_info["system_memory_total_kb"] = int(line.split()[1])
                    elif 'MemFree' in line:
                        gpu_info["system_memory_free_kb"] = int(line.split()[1])
                    elif 'MemAvailable' in line:
                        gpu_info["system_memory_available_kb"] = int(line.split()[1])

            # Check CUDA version
            cuda_result = await self.execute_command("nvcc --version 2>/dev/null", check_return_code=False)
            if cuda_result["return_code"] == 0:
                for line in cuda_result["stdout"].split('\n'):
                    if 'release' in line:
                        gpu_info["cuda_version"] = line.strip()
                        break

            return [gpu_info] if gpu_info else [{"error": "No GPU information available"}]

        except Exception as e:
            return [{"error": f"Failed to get GPU info: {e}"}]

    async def _get_gpu_memory(self) -> List[Dict[str, Any]]:
        """Get detailed GPU memory usage."""
        try:
            memory_info = {}
            
            # Try multiple methods to get GPU memory info
            
            # Method 1: nvidia-smi
            nvidia_result = await self.execute_command("nvidia-smi --query-gpu=memory.total,memory.used,memory.free --format=csv,noheader,nounits", check_return_code=False)
            if nvidia_result["return_code"] == 0:
                try:
                    mem_data = nvidia_result["stdout"].strip().split(',')
                    memory_info.update({
                        "gpu_memory_total_mb": int(mem_data[0].strip()),
                        "gpu_memory_used_mb": int(mem_data[1].strip()),
                        "gpu_memory_free_mb": int(mem_data[2].strip()),
                    })
                except (ValueError, IndexError):
                    pass

            # Method 2: Check Tegra memory info
            tegra_result = await self.execute_command("cat /proc/iomem | grep -i gpu", check_return_code=False)
            if tegra_result["return_code"] == 0:
                memory_info["tegra_gpu_memory_regions"] = tegra_result["stdout"].strip()

            # Method 3: System memory (shared with GPU on Jetson)
            meminfo_result = await self.execute_command("free -m")
            if meminfo_result["return_code"] == 0:
                mem_lines = meminfo_result["stdout"].strip().split('\n')
                for line in mem_lines:
                    if line.startswith('Mem:'):
                        mem_values = line.split()
                        memory_info.update({
                            "system_memory_total_mb": int(mem_values[1]),
                            "system_memory_used_mb": int(mem_values[2]),
                            "system_memory_free_mb": int(mem_values[3]),
                            "system_memory_available_mb": int(mem_values[6]) if len(mem_values) > 6 else int(mem_values[3])
                        })
                        break

            # Calculate memory utilization
            if "gpu_memory_total_mb" in memory_info and "gpu_memory_used_mb" in memory_info:
                total = memory_info["gpu_memory_total_mb"]
                used = memory_info["gpu_memory_used_mb"]
                memory_info["gpu_memory_utilization_percent"] = (used / total) * 100 if total > 0 else 0

            return [memory_info] if memory_info else [{"error": "No memory information available"}]

        except Exception as e:
            return [{"error": f"Failed to get GPU memory info: {e}"}]

    async def _control_fan(self, fan_speed: int) -> List[Dict[str, Any]]:
        """Control fan speed."""
        try:
            if not (0 <= fan_speed <= 100):
                return [{"error": "Fan speed must be between 0 and 100"}]

            # Jetson Nano fan control paths
            fan_paths = [
                "/sys/devices/pwm-fan/target_pwm",
                "/sys/class/hwmon/hwmon0/pwm1",
                "/sys/class/hwmon/hwmon1/pwm1",
            ]

            # Convert percentage to PWM value (0-255)
            pwm_value = int((fan_speed / 100.0) * 255)

            success = False
            used_path = None

            for fan_path in fan_paths:
                try:
                    # Check if path exists
                    exists_result = await self.execute_command(f"test -f {fan_path}", check_return_code=False)
                    if exists_result["return_code"] != 0:
                        continue

                    # Set fan speed
                    result = await self.execute_command(f"echo {pwm_value} | sudo tee {fan_path}", sudo=True)
                    if result["return_code"] == 0:
                        success = True
                        used_path = fan_path
                        break

                except Exception:
                    continue

            if success:
                # Verify the setting
                verification = await self.execute_command(f"cat {used_path}", check_return_code=False)
                actual_pwm = verification["stdout"].strip() if verification["return_code"] == 0 else "unknown"
                
                return [{
                    "success": True,
                    "message": f"Fan speed set to {fan_speed}%",
                    "fan_speed_percent": fan_speed,
                    "pwm_value": pwm_value,
                    "actual_pwm": actual_pwm,
                    "control_path": used_path
                }]
            else:
                return [{
                    "error": "Failed to control fan - no compatible fan control interface found",
                    "attempted_paths": fan_paths
                }]

        except Exception as e:
            return [{"error": f"Failed to control fan: {e}"}]

    async def _get_fan_status(self) -> List[Dict[str, Any]]:
        """Get current fan status."""
        try:
            fan_info = {}
            
            # Check various fan control paths
            fan_paths = [
                "/sys/devices/pwm-fan/target_pwm",
                "/sys/devices/pwm-fan/cur_pwm", 
                "/sys/class/hwmon/hwmon0/pwm1",
                "/sys/class/hwmon/hwmon1/pwm1",
                "/sys/class/hwmon/hwmon0/fan1_input",
            ]

            for path in fan_paths:
                try:
                    result = await self.execute_command(f"cat {path} 2>/dev/null", check_return_code=False)
                    if result["return_code"] == 0 and result["stdout"].strip():
                        value = int(result["stdout"].strip())
                        
                        if "pwm" in path:
                            # PWM value (0-255) to percentage
                            percentage = (value / 255.0) * 100
                            fan_info[f"pwm_control_{path.split('/')[-1]}"] = {
                                "pwm_value": value,
                                "percentage": round(percentage, 1),
                                "path": path
                            }
                        elif "fan" in path and "input" in path:
                            # Fan RPM reading
                            fan_info["fan_rpm"] = {
                                "rpm": value,
                                "path": path
                            }
                except (ValueError, IndexError):
                    continue

            # Check if fan is enabled/disabled
            fan_enable_paths = [
                "/sys/devices/pwm-fan/pwm_cap",
                "/sys/class/hwmon/hwmon0/pwm1_enable",
            ]

            for path in fan_enable_paths:
                try:
                    result = await self.execute_command(f"cat {path} 2>/dev/null", check_return_code=False)
                    if result["return_code"] == 0:
                        fan_info[f"fan_enable_{path.split('/')[-1]}"] = result["stdout"].strip()
                except Exception:
                    continue

            return [fan_info] if fan_info else [{"message": "No fan control interface found"}]

        except Exception as e:
            return [{"error": f"Failed to get fan status: {e}"}]

    async def _monitor_thermal(self, duration: int) -> List[Dict[str, Any]]:
        """Monitor thermal conditions over time."""
        try:
            readings = []
            interval = 5  # 5 seconds between readings
            num_readings = max(1, duration // interval)

            for i in range(num_readings):
                timestamp = await self.execute_command("date '+%Y-%m-%d %H:%M:%S'")
                temp_data = await self._get_temperature()
                
                if temp_data and "temperatures" in temp_data[0]:
                    reading = {
                        "timestamp": timestamp["stdout"].strip(),
                        "reading_number": i + 1,
                        "temperatures": temp_data[0]["temperatures"],
                        "max_temperature": temp_data[0].get("max_temperature_celsius", 0),
                        "status": temp_data[0].get("temperature_status", "unknown")
                    }
                    readings.append(reading)

                # Wait for next reading (except for the last one)
                if i < num_readings - 1:
                    await asyncio.sleep(interval)

            # Calculate statistics
            if readings:
                max_temps = [r["max_temperature"] for r in readings]
                avg_temp = sum(max_temps) / len(max_temps)
                max_temp_overall = max(max_temps)
                min_temp_overall = min(max_temps)

                summary = {
                    "monitoring_duration_seconds": duration,
                    "number_of_readings": len(readings),
                    "temperature_statistics": {
                        "average_celsius": round(avg_temp, 1),
                        "maximum_celsius": max_temp_overall,
                        "minimum_celsius": min_temp_overall,
                        "temperature_range": round(max_temp_overall - min_temp_overall, 1)
                    },
                    "readings": readings
                }

                return [summary]
            else:
                return [{"error": "No temperature readings obtained"}]

        except Exception as e:
            return [{"error": f"Failed to monitor thermal: {e}"}]

    async def _get_hardware_info(self) -> List[Dict[str, Any]]:
        """Get comprehensive hardware information."""
        try:
            # Gather various hardware information
            info_commands = {
                "jetson_model": "cat /proc/device-tree/model 2>/dev/null",
                "jetpack_version": "cat /etc/nv_tegra_release 2>/dev/null",
                "kernel_version": "uname -r",
                "architecture": "uname -m",
                "cpu_info": "cat /proc/cpuinfo | grep -E '(processor|model name|cpu MHz|cache size)' | head -20",
                "memory_info": "cat /proc/meminfo | head -10",
                "storage_info": "lsblk -f",
                "usb_devices": "lsusb",
                "pci_devices": "lspci 2>/dev/null",
            }

            hardware_info = {}
            
            for key, command in info_commands.items():
                try:
                    result = await self.execute_command(command, check_return_code=False)
                    if result["return_code"] == 0:
                        hardware_info[key] = result["stdout"].strip()
                    else:
                        hardware_info[key] = "N/A"
                except Exception:
                    hardware_info[key] = "Error"

            # Get additional Jetson-specific info
            try:
                # Get board info
                board_info = await self.execute_command("cat /proc/device-tree/nvidia,dtsfilename 2>/dev/null", check_return_code=False)
                if board_info["return_code"] == 0:
                    hardware_info["device_tree"] = board_info["stdout"].strip()

                # Get Tegra chip info
                chip_id = await self.execute_command("cat /sys/module/tegra_fuse/parameters/tegra_chip_id 2>/dev/null", check_return_code=False)
                if chip_id["return_code"] == 0:
                    hardware_info["tegra_chip_id"] = chip_id["stdout"].strip()

            except Exception:
                pass

            return [hardware_info]

        except Exception as e:
            return [{"error": f"Failed to get hardware info: {e}"}]

    async def _check_power_supply(self) -> List[Dict[str, Any]]:
        """Check power supply status and recommendations."""
        try:
            power_info = {}

            # Check power supply through various methods
            power_paths = [
                "/sys/class/power_supply/",
                "/proc/device-tree/power-supply/",
            ]

            # List power supplies
            ps_result = await self.execute_command("ls /sys/class/power_supply/ 2>/dev/null", check_return_code=False)
            if ps_result["return_code"] == 0:
                power_supplies = ps_result["stdout"].strip().split('\n')
                power_info["available_power_supplies"] = power_supplies

                # Get info for each power supply
                for ps in power_supplies:
                    if ps.strip():
                        try:
                            type_result = await self.execute_command(f"cat /sys/class/power_supply/{ps}/type 2>/dev/null", check_return_code=False)
                            status_result = await self.execute_command(f"cat /sys/class/power_supply/{ps}/status 2>/dev/null", check_return_code=False)
                            
                            ps_info = {}
                            if type_result["return_code"] == 0:
                                ps_info["type"] = type_result["stdout"].strip()
                            if status_result["return_code"] == 0:
                                ps_info["status"] = status_result["stdout"].strip()
                            
                            if ps_info:
                                power_info[f"power_supply_{ps}"] = ps_info
                        except Exception:
                            continue

            # Check for power mode recommendations
            current_mode = await self._get_power_mode()
            if current_mode and not current_mode[0].get("error"):
                mode_id = current_mode[0].get("current_power_mode")
                if mode_id == 0:  # MAXN mode
                    power_info["power_recommendation"] = {
                        "current_mode": "MAXN (15W)",
                        "recommended_supply": "5V/4A minimum (20W recommended)",
                        "warning": "Ensure adequate power supply for stable operation"
                    }
                elif mode_id == 1:  # 5W mode
                    power_info["power_recommendation"] = {
                        "current_mode": "5W",
                        "recommended_supply": "5V/2.5A minimum",
                        "note": "Power efficient mode suitable for battery operation"
                    }
                elif mode_id == 2:  # 10W mode
                    power_info["power_recommendation"] = {
                        "current_mode": "10W",
                        "recommended_supply": "5V/3A minimum",
                        "note": "Balanced mode with good performance/power ratio"
                    }

            return [power_info]

        except Exception as e:
            return [{"error": f"Failed to check power supply: {e}"}]

    async def _get_voltage_readings(self) -> List[Dict[str, Any]]:
        """Get voltage readings from available sensors."""
        try:
            voltage_info = {}

            # Check INA sensors (common on Jetson boards)
            ina_paths = [
                "/sys/class/hwmon/hwmon0/",
                "/sys/class/hwmon/hwmon1/",
                "/sys/class/hwmon/hwmon2/",
            ]

            for hwmon_path in ina_paths:
                try:
                    # Check if path exists
                    exists = await self.execute_command(f"test -d {hwmon_path}", check_return_code=False)
                    if exists["return_code"] != 0:
                        continue

                    # Get sensor name
                    name_result = await self.execute_command(f"cat {hwmon_path}name 2>/dev/null", check_return_code=False)
                    sensor_name = name_result["stdout"].strip() if name_result["return_code"] == 0 else "unknown"

                    # Look for voltage inputs
                    voltage_files = await self.execute_command(f"ls {hwmon_path}in*_input 2>/dev/null", check_return_code=False)
                    if voltage_files["return_code"] == 0:
                        for voltage_file in voltage_files["stdout"].strip().split('\n'):
                            if voltage_file.strip():
                                try:
                                    voltage_result = await self.execute_command(f"cat {voltage_file}", check_return_code=False)
                                    if voltage_result["return_code"] == 0:
                                        # Voltage is typically in millivolts
                                        voltage_mv = int(voltage_result["stdout"].strip())
                                        voltage_v = voltage_mv / 1000.0
                                        
                                        input_num = voltage_file.split('/')[-1].replace('in', '').replace('_input', '')
                                        voltage_info[f"{sensor_name}_in{input_num}"] = {
                                            "voltage_volts": voltage_v,
                                            "voltage_millivolts": voltage_mv,
                                            "sensor_path": voltage_file
                                        }
                                except (ValueError, IndexError):
                                    continue

                except Exception:
                    continue

            # Also check for current readings
            current_info = {}
            for hwmon_path in ina_paths:
                try:
                    current_files = await self.execute_command(f"ls {hwmon_path}curr*_input 2>/dev/null", check_return_code=False)
                    if current_files["return_code"] == 0:
                        for current_file in current_files["stdout"].strip().split('\n'):
                            if current_file.strip():
                                try:
                                    current_result = await self.execute_command(f"cat {current_file}", check_return_code=False)
                                    if current_result["return_code"] == 0:
                                        # Current is typically in milliamps
                                        current_ma = int(current_result["stdout"].strip())
                                        current_a = current_ma / 1000.0
                                        
                                        name_result = await self.execute_command(f"cat {hwmon_path.rstrip('/')}name 2>/dev/null", check_return_code=False)
                                        sensor_name = name_result["stdout"].strip() if name_result["return_code"] == 0 else "unknown"
                                        
                                        input_num = current_file.split('/')[-1].replace('curr', '').replace('_input', '')
                                        current_info[f"{sensor_name}_curr{input_num}"] = {
                                            "current_amps": current_a,
                                            "current_milliamps": current_ma,
                                            "sensor_path": current_file
                                        }
                                except (ValueError, IndexError):
                                    continue
                except Exception:
                    continue

            result = {"voltage_readings": voltage_info}
            if current_info:
                result["current_readings"] = current_info

            return [result] if voltage_info or current_info else [{"message": "No voltage/current sensors found"}]

        except Exception as e:
            return [{"error": f"Failed to get voltage readings: {e}"}]

    async def _control_gpio(self, gpio_pin: int, gpio_state: str) -> List[Dict[str, Any]]:
        """Control GPIO pins."""
        try:
            # Basic GPIO control (this is simplified - real implementation would need proper GPIO library)
            gpio_base_path = "/sys/class/gpio"
            gpio_pin_path = f"{gpio_base_path}/gpio{gpio_pin}"

            if gpio_state == "output":
                # Export GPIO pin
                export_result = await self.execute_command(f"echo {gpio_pin} | sudo tee {gpio_base_path}/export", sudo=True, check_return_code=False)
                if export_result["return_code"] != 0:
                    return [{"error": f"Failed to export GPIO pin {gpio_pin}"}]

                # Set direction to output
                direction_result = await self.execute_command(f"echo out | sudo tee {gpio_pin_path}/direction", sudo=True)
                if direction_result["return_code"] != 0:
                    return [{"error": f"Failed to set GPIO pin {gpio_pin} as output"}]

                return [{
                    "success": True,
                    "message": f"GPIO pin {gpio_pin} configured as output",
                    "pin": gpio_pin,
                    "state": "output"
                }]

            elif gpio_state == "input":
                # Export GPIO pin
                export_result = await self.execute_command(f"echo {gpio_pin} | sudo tee {gpio_base_path}/export", sudo=True, check_return_code=False)
                if export_result["return_code"] != 0:
                    return [{"error": f"Failed to export GPIO pin {gpio_pin}"}]

                # Set direction to input
                direction_result = await self.execute_command(f"echo in | sudo tee {gpio_pin_path}/direction", sudo=True)
                if direction_result["return_code"] != 0:
                    return [{"error": f"Failed to set GPIO pin {gpio_pin} as input"}]

                # Read current value
                value_result = await self.execute_command(f"cat {gpio_pin_path}/value")
                current_value = value_result["stdout"].strip() if value_result["return_code"] == 0 else "unknown"

                return [{
                    "success": True,
                    "message": f"GPIO pin {gpio_pin} configured as input",
                    "pin": gpio_pin,
                    "state": "input",
                    "current_value": current_value
                }]

            elif gpio_state in ["high", "low"]:
                # Set GPIO value
                value = "1" if gpio_state == "high" else "0"
                
                # Check if pin is exported and configured as output
                direction_check = await self.execute_command(f"cat {gpio_pin_path}/direction 2>/dev/null", check_return_code=False)
                if direction_check["return_code"] != 0:
                    return [{"error": f"GPIO pin {gpio_pin} is not exported or accessible"}]

                if direction_check["stdout"].strip() != "out":
                    return [{"error": f"GPIO pin {gpio_pin} is not configured as output"}]

                # Set value
                value_result = await self.execute_command(f"echo {value} | sudo tee {gpio_pin_path}/value", sudo=True)
                if value_result["return_code"] != 0:
                    return [{"error": f"Failed to set GPIO pin {gpio_pin} to {gpio_state}"}]

                return [{
                    "success": True,
                    "message": f"GPIO pin {gpio_pin} set to {gpio_state}",
                    "pin": gpio_pin,
                    "state": gpio_state,
                    "value": value
                }]

            else:
                return [{"error": f"Invalid GPIO state: {gpio_state}. Use 'high', 'low', 'input', or 'output'"}]

        except Exception as e:
            return [{"error": f"Failed to control GPIO: {e}"}]

    async def _list_gpio_pins(self) -> List[Dict[str, Any]]:
        """List available GPIO pins and their current state."""
        try:
            gpio_info = {}
            gpio_base_path = "/sys/class/gpio"

            # List exported GPIO pins
            exported_result = await self.execute_command(f"ls {gpio_base_path}/ | grep gpio", check_return_code=False)
            if exported_result["return_code"] == 0:
                exported_pins = [pin for pin in exported_result["stdout"].strip().split('\n') if pin.startswith('gpio')]
                
                for pin_dir in exported_pins:
                    if pin_dir.strip():
                        try:
                            pin_number = pin_dir.replace('gpio', '')
                            pin_path = f"{gpio_base_path}/{pin_dir}"
                            
                            # Get pin info
                            direction_result = await self.execute_command(f"cat {pin_path}/direction 2>/dev/null", check_return_code=False)
                            value_result = await self.execute_command(f"cat {pin_path}/value 2>/dev/null", check_return_code=False)
                            
                            pin_info = {"pin_number": pin_number, "exported": True}
                            
                            if direction_result["return_code"] == 0:
                                pin_info["direction"] = direction_result["stdout"].strip()
                            
                            if value_result["return_code"] == 0:
                                pin_info["value"] = value_result["stdout"].strip()
                                pin_info["state"] = "high" if pin_info["value"] == "1" else "low"
                            
                            gpio_info[f"gpio_{pin_number}"] = pin_info
                            
                        except Exception:
                            continue

            # Get Jetson Nano GPIO pin mapping information
            jetson_gpio_info = {
                "pin_layout": "Jetson Nano 40-pin GPIO header",
                "available_gpio_pins": [
                    7, 11, 12, 13, 15, 16, 18, 19, 21, 22, 23, 24, 26, 29, 31, 32, 33, 35, 36, 37, 38, 40
                ],
                "power_pins": {
                    "3.3V": [1, 17],
                    "5V": [2, 4],
                    "GND": [6, 9, 14, 20, 25, 30, 34, 39]
                },
                "special_pins": {
                    "I2C": {"SDA": 3, "SCL": 5},
                    "SPI": {"MOSI": 19, "MISO": 21, "SCLK": 23, "CE0": 24, "CE1": 26},
                    "UART": {"TXD": 8, "RXD": 10}
                }
            }

            return [{
                "exported_gpio_pins": gpio_info,
                "jetson_gpio_layout": jetson_gpio_info,
                "note": "Use caution when controlling GPIO pins. Incorrect usage can damage the hardware."
            }]

        except Exception as e:
            return [{"error": f"Failed to list GPIO pins: {e}"}]

    async def list_resources(self) -> List[Resource]:
        """List hardware-related resources."""
        return [
            Resource(
                uri="jetson://hardware/temperature",
                name="Temperature Sensors",
                description="Current temperature readings from all thermal zones",
                mimeType="application/json",
            ),
            Resource(
                uri="jetson://hardware/power_mode",
                name="Power Mode",
                description="Current power mode and available modes",
                mimeType="application/json",
            ),
            Resource(
                uri="jetson://hardware/gpu_status",
                name="GPU Status",
                description="GPU information and memory usage",
                mimeType="application/json",
            ),
        ]

    async def can_read_resource(self, uri: str) -> bool:
        """Check if this tool can read the given resource."""
        return uri.startswith("jetson://hardware/")

    async def read_resource(self, uri: str) -> str:
        """Read hardware resource information."""
        if uri == "jetson://hardware/temperature":
            temp_data = await self._get_temperature()
            return json.dumps(temp_data[0] if temp_data else {}, indent=2)
        elif uri == "jetson://hardware/power_mode":
            power_data = await self._get_power_mode()
            return json.dumps(power_data[0] if power_data else {}, indent=2)
        elif uri == "jetson://hardware/gpu_status":
            gpu_data = await self._get_gpu_info()
            return json.dumps(gpu_data[0] if gpu_data else {}, indent=2)
        else:
            return f"Unknown resource: {uri}"
