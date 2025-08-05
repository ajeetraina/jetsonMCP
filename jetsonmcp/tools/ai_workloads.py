"""
AI Workloads Management Tool for Jetson Nano

Handles AI model deployment, inference optimization, CUDA management,
and machine learning framework installations.
"""

import json
import logging
from typing import Any, Dict, List

from mcp.types import Resource, Tool

from .base import BaseTool

logger = logging.getLogger(__name__)


class AIWorkloadsTool(BaseTool):
    """
    Tool for managing AI workloads, models, and machine learning frameworks
    on Jetson Nano systems.
    """

    TOOL_NAME = "manage_ai_workloads"

    # Common AI frameworks and their installation commands
    AI_FRAMEWORKS = {
        "tensorflow": {
            "name": "TensorFlow",
            "install_cmd": "pip3 install tensorflow",
            "verify_cmd": "python3 -c 'import tensorflow as tf; print(tf.__version__)'",
            "gpu_support": True,
        },
        "pytorch": {
            "name": "PyTorch",
            "install_cmd": "pip3 install torch torchvision torchaudio",
            "verify_cmd": "python3 -c 'import torch; print(torch.__version__); print(torch.cuda.is_available())'",
            "gpu_support": True,
        },
        "opencv": {
            "name": "OpenCV",
            "install_cmd": "pip3 install opencv-python",
            "verify_cmd": "python3 -c 'import cv2; print(cv2.__version__)'",
            "gpu_support": True,
        },
        "onnxruntime": {
            "name": "ONNX Runtime",
            "install_cmd": "pip3 install onnxruntime-gpu",
            "verify_cmd": "python3 -c 'import onnxruntime; print(onnxruntime.__version__)'",
            "gpu_support": True,
        },
    }

    async def list_tools(self) -> List[Tool]:
        """List all AI workload management tools."""
        return [
            Tool(
                name=self.TOOL_NAME,
                description="Manage AI workloads, deploy models, optimize inference, and manage ML frameworks on Jetson Nano",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": [
                                "check_cuda",
                                "install_framework",
                                "list_frameworks",
                                "deploy_model",
                                "run_inference",
                                "optimize_model",
                                "benchmark_performance",
                                "check_gpu_memory",
                                "install_tensorrt",
                                "convert_to_tensorrt",
                                "list_models",
                                "download_model",
                                "setup_jupyter",
                            ],
                            "description": "AI workload management action to perform",
                        },
                        "framework": {
                            "type": "string",
                            "enum": ["tensorflow", "pytorch", "opencv", "onnxruntime"],
                            "description": "ML framework to work with",
                        },
                        "model_name": {
                            "type": "string",
                            "description": "Name of the model to deploy/run",
                        },
                        "model_url": {
                            "type": "string",
                            "description": "URL to download model from",
                        },
                        "model_path": {
                            "type": "string",
                            "description": "Local path to model file",
                        },
                        "input_data": {
                            "type": "string",
                            "description": "Path to input data for inference",
                        },
                        "optimization_level": {
                            "type": "string",
                            "enum": ["basic", "advanced", "tensorrt"],
                            "default": "basic",
                            "description": "Level of model optimization",
                        },
                        "batch_size": {
                            "type": "integer",
                            "default": 1,
                            "description": "Batch size for inference",
                        },
                        "precision": {
                            "type": "string",
                            "enum": ["FP32", "FP16", "INT8"],
                            "default": "FP16",
                            "description": "Inference precision mode",
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
        """Execute AI workload management commands."""
        if not await self.can_handle(tool_name):
            return [{"error": f"Cannot handle tool: {tool_name}"}]

        action = arguments.get("action")
        
        try:
            if action == "check_cuda":
                return await self._check_cuda()
            elif action == "install_framework":
                framework = arguments.get("framework")
                if not framework:
                    return [{"error": "framework parameter is required"}]
                return await self._install_framework(framework)
            elif action == "list_frameworks":
                return await self._list_frameworks()
            elif action == "deploy_model":
                model_name = arguments.get("model_name")
                model_path = arguments.get("model_path")
                model_url = arguments.get("model_url")
                if not model_name:
                    return [{"error": "model_name parameter is required"}]
                return await self._deploy_model(model_name, model_path, model_url)
            elif action == "run_inference":
                model_name = arguments.get("model_name")
                input_data = arguments.get("input_data")
                if not model_name:
                    return [{"error": "model_name parameter is required"}]
                return await self._run_inference(model_name, input_data)
            elif action == "optimize_model":
                model_path = arguments.get("model_path")
                optimization_level = arguments.get("optimization_level", "basic")
                if not model_path:
                    return [{"error": "model_path parameter is required"}]
                return await self._optimize_model(model_path, optimization_level)
            elif action == "benchmark_performance":
                model_name = arguments.get("model_name")
                batch_size = arguments.get("batch_size", 1)
                if not model_name:
                    return [{"error": "model_name parameter is required"}]
                return await self._benchmark_performance(model_name, batch_size)
            elif action == "check_gpu_memory":
                return await self._check_gpu_memory()
            elif action == "install_tensorrt":
                return await self._install_tensorrt()
            elif action == "convert_to_tensorrt":
                model_path = arguments.get("model_path")
                precision = arguments.get("precision", "FP16")
                if not model_path:
                    return [{"error": "model_path parameter is required"}]
                return await self._convert_to_tensorrt(model_path, precision)
            elif action == "list_models":
                return await self._list_models()
            elif action == "download_model":
                model_name = arguments.get("model_name")
                model_url = arguments.get("model_url")
                if not model_name or not model_url:
                    return [{"error": "model_name and model_url parameters are required"}]
                return await self._download_model(model_name, model_url)
            elif action == "setup_jupyter":
                return await self._setup_jupyter()
            else:
                return [{"error": f"Unknown action: {action}"}]

        except Exception as e:
            logger.error(f"AI workloads tool execution failed: {e}")
            return [{"error": str(e), "action": action}]

    async def _check_cuda(self) -> List[Dict[str, Any]]:
        """Check CUDA installation and GPU availability."""
        try:
            cuda_info = {}
            
            # Check CUDA version
            nvcc_result = await self.execute_command("nvcc --version", check_return_code=False)
            if nvcc_result["return_code"] == 0:
                cuda_info["nvcc_available"] = True
                cuda_info["nvcc_output"] = nvcc_result["stdout"]
                
                # Extract CUDA version
                for line in nvcc_result["stdout"].split('\n'):
                    if 'release' in line.lower():
                        cuda_info["cuda_version"] = line.strip()
                        break
            else:
                cuda_info["nvcc_available"] = False
                cuda_info["nvcc_error"] = nvcc_result["stderr"]

            # Check nvidia-smi
            nvidia_smi_result = await self.execute_command("nvidia-smi", check_return_code=False)
            if nvidia_smi_result["return_code"] == 0:
                cuda_info["nvidia_smi_available"] = True
                cuda_info["gpu_info"] = nvidia_smi_result["stdout"]
            else:
                cuda_info["nvidia_smi_available"] = False

            # Check CUDA Python support
            python_cuda_result = await self.execute_command(
                "python3 -c 'import torch; print(f\"PyTorch CUDA: {torch.cuda.is_available()}\"); import tensorflow as tf; print(f\"TensorFlow GPU: {len(tf.config.experimental.list_physical_devices(\"GPU\")) > 0}'",
                check_return_code=False
            )
            if python_cuda_result["return_code"] == 0:
                cuda_info["python_gpu_support"] = python_cuda_result["stdout"]
            else:
                cuda_info["python_gpu_support"] = "Frameworks not installed or error occurred"

            # Check CUDA environment variables
            env_result = await self.execute_command("env | grep CUDA", check_return_code=False)
            if env_result["return_code"] == 0:
                cuda_info["cuda_env_vars"] = env_result["stdout"]

            return [cuda_info]

        except Exception as e:
            return [{"error": f"Failed to check CUDA: {e}"}]

    async def _install_framework(self, framework: str) -> List[Dict[str, Any]]:
        """Install an AI/ML framework."""
        try:
            if framework not in self.AI_FRAMEWORKS:
                return [{"error": f"Unknown framework: {framework}. Available: {list(self.AI_FRAMEWORKS.keys())}"}]

            framework_info = self.AI_FRAMEWORKS[framework]
            
            # Check if already installed
            verify_result = await self.execute_command(framework_info["verify_cmd"], check_return_code=False)
            if verify_result["return_code"] == 0:
                return [{
                    "already_installed": True,
                    "framework": framework_info["name"],
                    "version_info": verify_result["stdout"],
                    "message": f"{framework_info['name']} is already installed"
                }]

            # Install framework
            install_result = await self.execute_command(framework_info["install_cmd"], timeout=1800)  # 30 minutes
            
            if install_result["return_code"] != 0:
                return [{
                    "success": False,
                    "framework": framework_info["name"],
                    "error": install_result["stderr"],
                    "message": f"Failed to install {framework_info['name']}"
                }]

            # Verify installation
            verify_result = await self.execute_command(framework_info["verify_cmd"], check_return_code=False)
            
            return [{
                "success": True,
                "framework": framework_info["name"],
                "install_output": install_result["stdout"],
                "verification": verify_result["stdout"] if verify_result["return_code"] == 0 else "Verification failed",
                "gpu_support": framework_info["gpu_support"],
                "message": f"{framework_info['name']} installed successfully"
            }]

        except Exception as e:
            return [{"error": f"Failed to install framework: {e}"}]

    async def _list_frameworks(self) -> List[Dict[str, Any]]:
        """List installed AI/ML frameworks."""
        try:
            frameworks_status = {}
            
            for framework_key, framework_info in self.AI_FRAMEWORKS.items():
                try:
                    verify_result = await self.execute_command(framework_info["verify_cmd"], check_return_code=False)
                    
                    if verify_result["return_code"] == 0:
                        frameworks_status[framework_key] = {
                            "name": framework_info["name"],
                            "installed": True,
                            "version_info": verify_result["stdout"].strip(),
                            "gpu_support": framework_info["gpu_support"]
                        }
                    else:
                        frameworks_status[framework_key] = {
                            "name": framework_info["name"],
                            "installed": False,
                            "gpu_support": framework_info["gpu_support"],
                            "install_command": framework_info["install_cmd"]
                        }
                except Exception as e:
                    frameworks_status[framework_key] = {
                        "name": framework_info["name"],
                        "installed": False,
                        "error": str(e),
                        "gpu_support": framework_info["gpu_support"]
                    }

            # Count installed frameworks
            installed_count = sum(1 for f in frameworks_status.values() if f.get("installed", False))
            
            return [{
                "total_frameworks": len(self.AI_FRAMEWORKS),
                "installed_frameworks": installed_count,
                "frameworks": frameworks_status
            }]

        except Exception as e:
            return [{"error": f"Failed to list frameworks: {e}"}]

    async def _deploy_model(self, model_name: str, model_path: str = None, model_url: str = None) -> List[Dict[str, Any]]:
        """Deploy an AI model for inference."""
        try:
            # Create models directory if it doesn't exist
            models_dir = "/home/jetson/models"
            await self.execute_command(f"mkdir -p {models_dir}", check_return_code=False)
            
            deployed_model_path = f"{models_dir}/{model_name}"
            
            if model_url:
                # Download model from URL
                download_result = await self.execute_command(
                    f"wget -O {deployed_model_path} {model_url}",
                    timeout=1800  # 30 minutes for large models
                )
                if download_result["return_code"] != 0:
                    return [{
                        "success": False,
                        "message": f"Failed to download model from {model_url}",
                        "error": download_result["stderr"]
                    }]
                
                model_source = f"Downloaded from {model_url}"
                
            elif model_path:
                # Copy model from local path
                copy_result = await self.execute_command(f"cp {model_path} {deployed_model_path}")
                if copy_result["return_code"] != 0:
                    return [{
                        "success": False,
                        "message": f"Failed to copy model from {model_path}",
                        "error": copy_result["stderr"]
                    }]
                
                model_source = f"Copied from {model_path}"
                
            else:
                return [{"error": "Either model_path or model_url must be provided"}]

            # Get model file info
            file_info_result = await self.execute_command(f"ls -lh {deployed_model_path}", check_return_code=False)
            file_info = file_info_result["stdout"] if file_info_result["return_code"] == 0 else "N/A"
            
            # Try to identify model type
            model_type = "Unknown"
            if deployed_model_path.endswith('.pb'):
                model_type = "TensorFlow SavedModel/Frozen Graph"
            elif deployed_model_path.endswith('.pth') or deployed_model_path.endswith('.pt'):
                model_type = "PyTorch Model"
            elif deployed_model_path.endswith('.onnx'):
                model_type = "ONNX Model"
            elif deployed_model_path.endswith('.trt') or deployed_model_path.endswith('.engine'):
                model_type = "TensorRT Engine"

            return [{
                "success": True,
                "model_name": model_name,
                "deployed_path": deployed_model_path,
                "model_source": model_source,
                "model_type": model_type,
                "file_info": file_info,
                "message": f"Model '{model_name}' deployed successfully"
            }]

        except Exception as e:
            return [{"error": f"Failed to deploy model: {e}"}]

    async def _check_gpu_memory(self) -> List[Dict[str, Any]]:
        """Check GPU memory usage and availability."""
        try:
            gpu_memory_info = {}
            
            # Use nvidia-smi to get memory info
            nvidia_smi_result = await self.execute_command("nvidia-smi --query-gpu=memory.total,memory.used,memory.free --format=csv,noheader,nounits", check_return_code=False)
            
            if nvidia_smi_result["return_code"] == 0:
                try:
                    memory_data = nvidia_smi_result["stdout"].strip().split(',')
                    gpu_memory_info = {
                        "total_mb": int(memory_data[0].strip()),
                        "used_mb": int(memory_data[1].strip()),
                        "free_mb": int(memory_data[2].strip()),
                        "utilization_percent": round((int(memory_data[1].strip()) / int(memory_data[0].strip())) * 100, 1)
                    }
                except (ValueError, IndexError):
                    gpu_memory_info["error"] = "Failed to parse GPU memory information"
            else:
                gpu_memory_info["error"] = "nvidia-smi not available or failed"

            # Also check system memory (shared with GPU on Jetson)
            system_memory_result = await self.execute_command("free -m")
            if system_memory_result["return_code"] == 0:
                mem_lines = system_memory_result["stdout"].strip().split('\n')
                for line in mem_lines:
                    if line.startswith('Mem:'):
                        mem_values = line.split()
                        gpu_memory_info["system_memory"] = {
                            "total_mb": int(mem_values[1]),
                            "used_mb": int(mem_values[2]),
                            "free_mb": int(mem_values[3]),
                            "available_mb": int(mem_values[6]) if len(mem_values) > 6 else int(mem_values[3])
                        }
                        break

            # Memory recommendations based on usage
            recommendations = []
            if "utilization_percent" in gpu_memory_info:
                if gpu_memory_info["utilization_percent"] > 90:
                    recommendations.append("GPU memory usage is very high. Consider reducing batch size or model complexity.")
                elif gpu_memory_info["utilization_percent"] > 75:
                    recommendations.append("GPU memory usage is high. Monitor for out-of-memory errors.")
                elif gpu_memory_info["utilization_percent"] < 25:
                    recommendations.append("GPU memory usage is low. You may be able to increase batch size for better performance.")

            gpu_memory_info["recommendations"] = recommendations

            return [gpu_memory_info]

        except Exception as e:
            return [{"error": f"Failed to check GPU memory: {e}"}]

    async def _install_tensorrt(self) -> List[Dict[str, Any]]:
        """Install TensorRT for model optimization."""
        try:
            # Check if TensorRT is already installed
            check_result = await self.execute_command("python3 -c 'import tensorrt; print(tensorrt.__version__)'", check_return_code=False)
            
            if check_result["return_code"] == 0:
                return [{
                    "already_installed": True,
                    "version": check_result["stdout"].strip(),
                    "message": "TensorRT is already installed"
                }]

            # TensorRT installation for Jetson (usually comes with JetPack)
            # Check JetPack TensorRT installation
            jetpack_tensorrt = await self.execute_command("dpkg -l | grep tensorrt", check_return_code=False)
            
            if jetpack_tensorrt["return_code"] == 0:
                # TensorRT is installed via JetPack, install Python bindings
                python_install = await self.execute_command("pip3 install pycuda", timeout=600)
                
                if python_install["return_code"] == 0:
                    # Verify installation
                    verify_result = await self.execute_command("python3 -c 'import tensorrt; print(tensorrt.__version__)'", check_return_code=False)
                    
                    return [{
                        "success": True,
                        "installation_method": "JetPack + Python bindings",
                        "jetpack_packages": jetpack_tensorrt["stdout"],
                        "python_bindings": "Installed",
                        "version": verify_result["stdout"].strip() if verify_result["return_code"] == 0 else "Unknown",
                        "message": "TensorRT installed successfully"
                    }]
                else:
                    return [{
                        "success": False,
                        "message": "TensorRT packages found but failed to install Python bindings",
                        "error": python_install["stderr"]
                    }]
            else:
                return [{
                    "success": False,
                    "message": "TensorRT not found. Please install JetPack SDK which includes TensorRT.",
                    "recommendation": "Use the NVIDIA SDK Manager to install JetPack with TensorRT support"
                }]

        except Exception as e:
            return [{"error": f"Failed to install TensorRT: {e}"}]

    async def _setup_jupyter(self) -> List[Dict[str, Any]]:
        """Set up Jupyter Notebook for AI development."""
        try:
            # Check if Jupyter is already installed
            check_result = await self.execute_command("jupyter --version", check_return_code=False)
            
            if check_result["return_code"] == 0:
                jupyter_info = {
                    "already_installed": True,
                    "version_info": check_result["stdout"],
                    "message": "Jupyter is already installed"
                }
            else:
                # Install Jupyter
                install_result = await self.execute_command("pip3 install jupyter jupyterlab", timeout=600)
                
                if install_result["return_code"] != 0:
                    return [{
                        "success": False,
                        "message": "Failed to install Jupyter",
                        "error": install_result["stderr"]
                    }]
                
                jupyter_info = {
                    "installed": True,
                    "install_output": install_result["stdout"],
                    "message": "Jupyter installed successfully"
                }

            # Create Jupyter configuration
            config_result = await self.execute_command("jupyter notebook --generate-config", check_return_code=False)
            
            if config_result["return_code"] == 0:
                # Set up basic configuration for remote access
                config_commands = [
                    "echo \"c.NotebookApp.ip = '0.0.0.0'\" >> ~/.jupyter/jupyter_notebook_config.py",
                    "echo \"c.NotebookApp.port = 8888\" >> ~/.jupyter/jupyter_notebook_config.py",
                    "echo \"c.NotebookApp.open_browser = False\" >> ~/.jupyter/jupyter_notebook_config.py",
                    "echo \"c.NotebookApp.allow_root = True\" >> ~/.jupyter/jupyter_notebook_config.py",
                ]
                
                for cmd in config_commands:
                    await self.execute_command(cmd, check_return_code=False)
                
                jupyter_info["configuration"] = "Remote access configured on port 8888"

            # Create sample AI notebook
            notebook_content = '''
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Jetson Nano AI Development\\n",
    "\\n",
    "This notebook is set up for AI development on your Jetson Nano."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "# Check GPU availability\\n",
    "import torch\\n",
    "print(f\\"PyTorch version: {torch.__version__}\\")\\n",
    "print(f\\"CUDA available: {torch.cuda.is_available()}\\")\\n",
    "if torch.cuda.is_available():\\n",
    "    print(f\\"GPU device: {torch.cuda.get_device_name(0)}\\")\\n",
    "    print(f\\"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB\\")"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
'''
            
            # Create notebooks directory and sample notebook
            await self.execute_command("mkdir -p ~/notebooks", check_return_code=False)
            await self.execute_command(f"cat > ~/notebooks/jetson_ai_starter.ipynb << 'EOF'\n{notebook_content}\nEOF", check_return_code=False)
            
            jupyter_info["sample_notebook"] = "Created ~/notebooks/jetson_ai_starter.ipynb"
            jupyter_info["start_command"] = "jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root"

            return [jupyter_info]

        except Exception as e:
            return [{"error": f"Failed to setup Jupyter: {e}"}]

    async def list_resources(self) -> List[Resource]:
        """List AI workload related resources."""
        return [
            Resource(
                uri="jetson://ai/cuda_status",
                name="CUDA Status",
                description="Current CUDA installation and GPU availability status",
                mimeType="application/json",
            ),
            Resource(
                uri="jetson://ai/frameworks",
                name="AI Frameworks",
                description="Status of installed AI/ML frameworks",
                mimeType="application/json",
            ),
            Resource(
                uri="jetson://ai/models",
                name="Deployed Models",
                description="List of deployed AI models",
                mimeType="application/json",
            ),
        ]

    async def can_read_resource(self, uri: str) -> bool:
        """Check if this tool can read the given resource."""
        return uri.startswith("jetson://ai/")

    async def read_resource(self, uri: str) -> str:
        """Read AI workload resource information."""
        if uri == "jetson://ai/cuda_status":
            cuda_data = await self._check_cuda()
            return json.dumps(cuda_data[0] if cuda_data else {}, indent=2)
        elif uri == "jetson://ai/frameworks":
            frameworks_data = await self._list_frameworks()
            return json.dumps(frameworks_data[0] if frameworks_data else {}, indent=2)
        elif uri == "jetson://ai/models":
            models_data = await self._list_models()
            return json.dumps(models_data[0] if models_data else {}, indent=2)
        else:
            return f"Unknown resource: {uri}"

    async def _list_models(self) -> List[Dict[str, Any]]:
        """List deployed AI models."""
        try:
            models_dir = "/home/jetson/models"
            
            # Check if models directory exists
            dir_exists = await self.directory_exists(models_dir)
            if not dir_exists:
                return [{
                    "models_directory": models_dir,
                    "exists": False,
                    "models": [],
                    "message": "No models directory found. Deploy models first."
                }]

            # List models in directory
            list_result = await self.execute_command(f"ls -la {models_dir}", check_return_code=False)
            
            if list_result["return_code"] != 0:
                return [{"error": f"Failed to list models directory: {list_result['stderr']}"}]

            models = []
            lines = list_result["stdout"].strip().split('\n')
            
            for line in lines[1:]:  # Skip header line
                if line.strip() and not line.startswith('total'):
                    parts = line.split()
                    if len(parts) >= 9 and not parts[-1].startswith('.'):
                        try:
                            model_info = {
                                "name": parts[-1],
                                "size": parts[4],
                                "modified": f"{parts[5]} {parts[6]} {parts[7]}",
                                "permissions": parts[0],
                                "full_path": f"{models_dir}/{parts[-1]}"
                            }
                            
                            # Try to determine model type
                            if parts[-1].endswith('.pb'):
                                model_info["type"] = "TensorFlow"
                            elif parts[-1].endswith(('.pth', '.pt')):
                                model_info["type"] = "PyTorch"
                            elif parts[-1].endswith('.onnx'):
                                model_info["type"] = "ONNX"
                            elif parts[-1].endswith('.trt'):
                                model_info["type"] = "TensorRT"
                            else:
                                model_info["type"] = "Unknown"
                            
                            models.append(model_info)
                        except IndexError:
                            continue

            return [{
                "models_directory": models_dir,
                "total_models": len(models),
                "models": models
            }]

        except Exception as e:
            return [{"error": f"Failed to list models: {e}"}]

    async def _download_model(self, model_name: str, model_url: str) -> List[Dict[str, Any]]:
        """Download a model from URL."""
        try:
            models_dir = "/home/jetson/models"
            await self.execute_command(f"mkdir -p {models_dir}", check_return_code=False)
            
            model_path = f"{models_dir}/{model_name}"
            
            # Download model
            download_result = await self.execute_command(
                f"wget -O {model_path} {model_url}",
                timeout=1800  # 30 minutes
            )
            
            if download_result["return_code"] != 0:
                return [{
                    "success": False,
                    "message": f"Failed to download model {model_name}",
                    "error": download_result["stderr"]
                }]

            # Get file info
            file_info_result = await self.execute_command(f"ls -lh {model_path}")
            file_info = file_info_result["stdout"] if file_info_result["return_code"] == 0 else "N/A"

            return [{
                "success": True,
                "model_name": model_name,
                "model_path": model_path,
                "source_url": model_url,
                "file_info": file_info,
                "message": f"Model {model_name} downloaded successfully"
            }]

        except Exception as e:
            return [{"error": f"Failed to download model: {e}"}]
