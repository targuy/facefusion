"""
GPU resource management and configuration.
"""

import json
from pathlib import Path
from typing import List, Optional

from facefusion_repository.gpu.detector import GPUDetector
from facefusion_repository.types import GPUConfig, GPUInfo


class GPUManager:
    """Manages GPU configuration and resources."""

    def __init__(self, config_path: Optional[str] = None) -> None:
        """
        Initialize GPU manager.

        Args:
            config_path: Path to GPU configuration file. If None, uses default.
        """
        if config_path is None:
            repo_path = Path.home() / '.facefusion_repository'
            config_path = str(repo_path / 'gpu_config.json')
        
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> GPUConfig:
        """
        Load GPU configuration from file.

        Returns:
            GPUConfig object
        """
        if not self.config_path.exists():
            # Return default config
            return GPUConfig()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return GPUConfig(
                enabled=data.get('enabled', True),
                device_ids=data.get('device_ids', [0]),
                memory_limit=data.get('memory_limit'),
                providers=data.get('providers', ['CUDAExecutionProvider', 'CPUExecutionProvider'])
            )
        except Exception as e:
            print(f'Warning: Could not load GPU config: {e}')
            return GPUConfig()

    def _save_config(self) -> bool:
        """
        Save GPU configuration to file.

        Returns:
            True if save successful
        """
        try:
            # Create directory if needed
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'enabled': self.config.enabled,
                'device_ids': self.config.device_ids,
                'memory_limit': self.config.memory_limit,
                'providers': self.config.providers
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f'Error saving GPU config: {e}')
            return False

    def get_config(self) -> GPUConfig:
        """
        Get current GPU configuration.

        Returns:
            GPUConfig object
        """
        return self.config

    def set_config(self, config: GPUConfig) -> bool:
        """
        Set GPU configuration.

        Args:
            config: GPUConfig object

        Returns:
            True if successful
        """
        self.config = config
        return self._save_config()

    def enable_gpu(self, device_ids: Optional[List[int]] = None) -> bool:
        """
        Enable GPU acceleration.

        Args:
            device_ids: List of device IDs to use. If None, uses [0].

        Returns:
            True if successful
        """
        if device_ids is None:
            device_ids = [0]
        
        self.config.enabled = True
        self.config.device_ids = device_ids
        
        # Update providers based on available hardware
        self.config.providers = GPUDetector.get_recommended_providers()
        
        return self._save_config()

    def disable_gpu(self) -> bool:
        """
        Disable GPU acceleration (CPU only).

        Returns:
            True if successful
        """
        self.config.enabled = False
        self.config.providers = ['CPUExecutionProvider']
        
        return self._save_config()

    def set_memory_limit(self, limit_mb: int) -> bool:
        """
        Set GPU memory limit.

        Args:
            limit_mb: Memory limit in MB

        Returns:
            True if successful
        """
        if limit_mb <= 0:
            print('Error: Memory limit must be positive')
            return False
        
        self.config.memory_limit = limit_mb
        return self._save_config()

    def get_available_gpus(self) -> List[GPUInfo]:
        """
        Get list of available GPUs.

        Returns:
            List of GPUInfo objects
        """
        return GPUDetector.detect_gpus()

    def get_execution_providers(self) -> List[str]:
        """
        Get execution providers based on current configuration.

        Returns:
            List of provider names in priority order
        """
        if not self.config.enabled:
            return ['CPUExecutionProvider']
        
        return self.config.providers

    def get_provider_options(self) -> List[dict]:
        """
        Get provider options including device IDs and memory limits.

        Returns:
            List of provider option dictionaries
        """
        options = []
        
        for provider in self.config.providers:
            if provider == 'CUDAExecutionProvider':
                cuda_options = {
                    'device_id': self.config.device_ids[0] if self.config.device_ids else 0
                }
                
                if self.config.memory_limit:
                    cuda_options['gpu_mem_limit'] = self.config.memory_limit * 1024 * 1024  # Convert to bytes
                
                options.append(cuda_options)
            else:
                options.append({})
        
        return options

    def print_status(self) -> None:
        """Print GPU status and configuration."""
        print('GPU Configuration:')
        print('-' * 60)
        print(f'Enabled: {self.config.enabled}')
        print(f'Providers: {", ".join(self.config.providers)}')
        
        if self.config.device_ids:
            print(f'Device IDs: {", ".join(map(str, self.config.device_ids))}')
        
        if self.config.memory_limit:
            print(f'Memory Limit: {self.config.memory_limit} MB')
        
        print()
        print('Available GPUs:')
        print('-' * 60)
        
        gpus = self.get_available_gpus()
        
        if not gpus:
            print('No GPUs detected. Using CPU only.')
        else:
            for gpu in gpus:
                print(f'\nDevice {gpu.device_id}:')
                print(f'  Name: {gpu.name}')
                
                if gpu.memory_total > 0:
                    print(f'  Memory: {gpu.memory_available} MB available / {gpu.memory_total} MB total')
                
                if gpu.compute_capability:
                    print(f'  Compute Capability: {gpu.compute_capability}')
                
                if gpu.driver_version:
                    print(f'  Driver Version: {gpu.driver_version}')
