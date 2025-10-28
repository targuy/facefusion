"""
GPU detection and information gathering.
"""

import platform
from typing import List, Optional

from facefusion_repository.types import GPUInfo


class GPUDetector:
    """Detects and provides information about available GPUs."""

    @staticmethod
    def detect_gpus() -> List[GPUInfo]:
        """
        Detect all available GPUs in the system.

        Returns:
            List of GPUInfo objects
        """
        gpus = []

        # Try CUDA first (NVIDIA)
        cuda_gpus = GPUDetector._detect_cuda_gpus()
        if cuda_gpus:
            gpus.extend(cuda_gpus)

        # Try DirectML (Windows)
        if platform.system() == 'Windows' and not gpus:
            directml_gpus = GPUDetector._detect_directml_gpus()
            if directml_gpus:
                gpus.extend(directml_gpus)

        # Try ROCm (AMD on Linux)
        if platform.system() == 'Linux' and not gpus:
            rocm_gpus = GPUDetector._detect_rocm_gpus()
            if rocm_gpus:
                gpus.extend(rocm_gpus)

        # Try MPS (Apple Silicon)
        if platform.system() == 'Darwin':
            mps_gpu = GPUDetector._detect_mps_gpu()
            if mps_gpu:
                gpus.append(mps_gpu)

        return gpus

    @staticmethod
    def _detect_cuda_gpus() -> List[GPUInfo]:
        """
        Detect CUDA-capable NVIDIA GPUs.

        Returns:
            List of GPUInfo objects for CUDA devices
        """
        gpus = []
        
        try:
            # Try importing pynvml for NVIDIA GPU info
            import pynvml
            
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(handle)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                
                # Try to get compute capability
                try:
                    major, minor = pynvml.nvmlDeviceGetCudaComputeCapability(handle)
                    compute_capability = f"{major}.{minor}"
                except:
                    compute_capability = None
                
                # Try to get driver version
                try:
                    driver_version = pynvml.nvmlSystemGetDriverVersion()
                except:
                    driver_version = None
                
                gpu_info = GPUInfo(
                    device_id=i,
                    name=name if isinstance(name, str) else name.decode('utf-8'),
                    memory_total=memory_info.total // (1024 * 1024),  # Convert to MB
                    memory_available=memory_info.free // (1024 * 1024),
                    compute_capability=compute_capability,
                    driver_version=driver_version if isinstance(driver_version, str) else 
                                 (driver_version.decode('utf-8') if driver_version else None)
                )
                gpus.append(gpu_info)
            
            pynvml.nvmlShutdown()
            
        except ImportError:
            # pynvml not available, try checking onnxruntime providers
            try:
                import onnxruntime as ort
                providers = ort.get_available_providers()
                
                if 'CUDAExecutionProvider' in providers:
                    # CUDA is available but we can't get detailed info
                    gpu_info = GPUInfo(
                        device_id=0,
                        name="CUDA Device (details unavailable)",
                        memory_total=0,
                        memory_available=0,
                        compute_capability=None,
                        driver_version=None
                    )
                    gpus.append(gpu_info)
            except:
                pass
        except Exception as e:
            print(f"Warning: Could not detect CUDA GPUs: {e}")
        
        return gpus

    @staticmethod
    def _detect_directml_gpus() -> List[GPUInfo]:
        """
        Detect DirectML-capable GPUs on Windows.

        Returns:
            List of GPUInfo objects for DirectML devices
        """
        gpus = []
        
        try:
            import onnxruntime as ort
            providers = ort.get_available_providers()
            
            if 'DmlExecutionProvider' in providers:
                # DirectML is available
                gpu_info = GPUInfo(
                    device_id=0,
                    name="DirectML Device",
                    memory_total=0,
                    memory_available=0,
                    compute_capability=None,
                    driver_version=None
                )
                gpus.append(gpu_info)
        except:
            pass
        
        return gpus

    @staticmethod
    def _detect_rocm_gpus() -> List[GPUInfo]:
        """
        Detect ROCm-capable AMD GPUs on Linux.

        Returns:
            List of GPUInfo objects for ROCm devices
        """
        gpus = []
        
        try:
            import onnxruntime as ort
            providers = ort.get_available_providers()
            
            if 'ROCMExecutionProvider' in providers:
                # ROCm is available
                gpu_info = GPUInfo(
                    device_id=0,
                    name="ROCm Device",
                    memory_total=0,
                    memory_available=0,
                    compute_capability=None,
                    driver_version=None
                )
                gpus.append(gpu_info)
        except:
            pass
        
        return gpus

    @staticmethod
    def _detect_mps_gpu() -> Optional[GPUInfo]:
        """
        Detect Metal Performance Shaders (MPS) on Apple Silicon.

        Returns:
            GPUInfo object for MPS device or None
        """
        try:
            import onnxruntime as ort
            providers = ort.get_available_providers()
            
            if 'CoreMLExecutionProvider' in providers:
                # CoreML/MPS is available
                return GPUInfo(
                    device_id=0,
                    name="Apple Neural Engine",
                    memory_total=0,
                    memory_available=0,
                    compute_capability=None,
                    driver_version=None
                )
        except:
            pass
        
        return None

    @staticmethod
    def get_recommended_providers() -> List[str]:
        """
        Get recommended execution providers in priority order.

        Returns:
            List of provider names
        """
        providers = []
        
        # Check for CUDA
        try:
            import onnxruntime as ort
            available = ort.get_available_providers()
            
            # Priority order
            priority_providers = [
                'CUDAExecutionProvider',
                'DmlExecutionProvider',
                'ROCMExecutionProvider',
                'CoreMLExecutionProvider',
                'CPUExecutionProvider'
            ]
            
            for provider in priority_providers:
                if provider in available:
                    providers.append(provider)
        except:
            # Fallback to CPU only
            providers = ['CPUExecutionProvider']
        
        return providers

    @staticmethod
    def is_gpu_available() -> bool:
        """
        Check if any GPU is available.

        Returns:
            True if GPU is available
        """
        gpus = GPUDetector.detect_gpus()
        return len(gpus) > 0
