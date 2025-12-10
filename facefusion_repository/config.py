"""
Configuration and execution provider management for FaceFusion Repository System.

Supports both CPU and GPU execution modes.
"""

import os
from typing import List, Literal

ExecutionProvider = Literal['cpu', 'cuda', 'tensorrt', 'coreml']


class Config:
    """System configuration and execution provider management."""
    
    # Execution provider settings
    EXECUTION_PROVIDER: ExecutionProvider = 'cpu'
    EXECUTION_PROVIDERS: List[str] = ['CPUExecutionProvider']
    
    # Repository settings
    REPOSITORY_PATH: str = os.path.expanduser('~/.facefusion_repository')
    
    # Processing settings
    DEFAULT_FRAME_SAMPLE_RATE: int = 1
    DEFAULT_MIN_CONFIDENCE: float = 0.5
    DEFAULT_ORIENTATION_TOLERANCE: int = 22
    
    # GPU settings
    CUDA_DEVICE_ID: int = 0
    USE_GPU_IF_AVAILABLE: bool = True
    
    @classmethod
    def initialize_from_environment(cls) -> None:
        """Initialize configuration from environment variables."""
        # Execution provider
        provider = os.getenv('FACEFUSION_EXECUTION_PROVIDER', 'cpu').lower()
        if provider == 'cuda':
            cls.EXECUTION_PROVIDER = 'cuda'
            cls.EXECUTION_PROVIDERS = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        elif provider == 'tensorrt':
            cls.EXECUTION_PROVIDER = 'tensorrt'
            cls.EXECUTION_PROVIDERS = ['TensorrtExecutionProvider', 'CUDAExecutionProvider', 'CPUExecutionProvider']
        elif provider == 'coreml':
            cls.EXECUTION_PROVIDER = 'coreml'
            cls.EXECUTION_PROVIDERS = ['CoreMLExecutionProvider', 'CPUExecutionProvider']
        else:
            cls.EXECUTION_PROVIDER = 'cpu'
            cls.EXECUTION_PROVIDERS = ['CPUExecutionProvider']
        
        # Override with specific providers list if provided
        providers_env = os.getenv('FACEFUSION_EXECUTION_PROVIDERS')
        if providers_env:
            cls.EXECUTION_PROVIDERS = [p.strip() for p in providers_env.split(',')]
        
        # Repository path
        repo_path = os.getenv('FACEFUSION_REPOSITORY_PATH')
        if repo_path:
            cls.REPOSITORY_PATH = os.path.expanduser(repo_path)
        
        # CUDA device
        cuda_device = os.getenv('CUDA_VISIBLE_DEVICES')
        if cuda_device:
            try:
                cls.CUDA_DEVICE_ID = int(cuda_device)
            except ValueError:
                pass
    
    @classmethod
    def is_gpu_available(cls) -> bool:
        """Check if GPU execution is available."""
        try:
            if cls.EXECUTION_PROVIDER in ['cuda', 'tensorrt']:
                import torch
                return torch.cuda.is_available()
            elif cls.EXECUTION_PROVIDER == 'coreml':
                # CoreML is available on macOS
                import platform
                return platform.system() == 'Darwin'
        except ImportError:
            pass
        return False
    
    @classmethod
    def get_execution_info(cls) -> dict:
        """Get current execution configuration information."""
        return {
            'provider': cls.EXECUTION_PROVIDER,
            'providers_list': cls.EXECUTION_PROVIDERS,
            'gpu_available': cls.is_gpu_available() if cls.USE_GPU_IF_AVAILABLE else False,
            'repository_path': cls.REPOSITORY_PATH,
            'cuda_device': cls.CUDA_DEVICE_ID if cls.EXECUTION_PROVIDER in ['cuda', 'tensorrt'] else None
        }
    
    @classmethod
    def print_execution_info(cls) -> None:
        """Print execution configuration information."""
        info = cls.get_execution_info()
        print('Execution Configuration:')
        print(f'  Provider: {info["provider"]}')
        print(f'  Providers: {", ".join(info["providers_list"])}')
        print(f'  GPU Available: {"Yes" if info["gpu_available"] else "No"}')
        print(f'  Repository: {info["repository_path"]}')
        if info.get('cuda_device') is not None:
            print(f'  CUDA Device: {info["cuda_device"]}')


# Initialize configuration on module import
Config.initialize_from_environment()
