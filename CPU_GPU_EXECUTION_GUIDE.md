# CPU and GPU Execution Guide

## Overview

The FaceFusion Repository System supports both CPU and GPU execution modes for maximum flexibility and performance.

## Execution Modes

### CPU Mode (Default)

CPU mode works on any system without requiring special hardware.

**Advantages:**
- Works everywhere
- No special setup required
- Lower power consumption
- Good for testing and development

**Disadvantages:**
- Slower processing
- Limited parallelization

### GPU Mode (CUDA)

GPU mode uses NVIDIA CUDA for hardware acceleration.

**Advantages:**
- 5-10x faster processing
- Better for batch operations
- Parallel face processing

**Requirements:**
- NVIDIA GPU with CUDA support
- CUDA Toolkit installed
- CUD drivers

### GPU Mode (TensorRT)

TensorRT provides optimized inference on NVIDIA GPUs.

**Advantages:**
- Even faster than standard CUDA
- Optimized for production workloads

**Requirements:**
- NVIDIA GPU
- TensorRT installed
- CUDA Toolkit

### CoreML Mode (macOS)

CoreML provides Apple Silicon optimization.

**Advantages:**
- Optimized for M1/M2/M3 chips
- Power efficient

**Requirements:**
- macOS device
- Apple Silicon chip

## Configuration

### Environment Variables

Set these before running the system:

```bash
# CPU Mode (default)
export FACEFUSION_EXECUTION_PROVIDER=cpu

# GPU Mode (CUDA)
export FACEFUSION_EXECUTION_PROVIDER=cuda
export CUDA_VISIBLE_DEVICES=0  # GPU device ID

# GPU Mode (TensorRT)
export FACEFUSION_EXECUTION_PROVIDER=tensorrt

# CoreML Mode (macOS)
export FACEFUSION_EXECUTION_PROVIDER=coreml

# Custom execution providers list
export FACEFUSION_EXECUTION_PROVIDERS="CUDAExecutionProvider,CPUExecutionProvider"

# Custom repository path
export FACEFUSION_REPOSITORY_PATH="~/my_faces"
```

### Python Configuration

```python
from facefusion_repository.config import Config

# Check current configuration
Config.print_execution_info()

# Manually set provider
Config.EXECUTION_PROVIDER = 'cuda'
Config.EXECUTION_PROVIDERS = ['CUDAExecutionProvider', 'CPUExecutionProvider']

# Check GPU availability
if Config.is_gpu_available():
    print("GPU is available!")
```

### Container Configuration

#### Docker

```bash
# CPU Mode
docker run -it \
  -e FACEFUSION_EXECUTION_PROVIDER=cpu \
  facefusion-repository:latest

# GPU Mode (requires nvidia-docker)
docker run --gpus all -it \
  -e FACEFUSION_EXECUTION_PROVIDER=cuda \
  -e CUDA_VISIBLE_DEVICES=0 \
  facefusion-repository:latest
```

#### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  facefusion-cpu:
    build: .
    environment:
      - FACEFUSION_EXECUTION_PROVIDER=cpu
    volumes:
      - ./data:/data
      - ~/.facefusion_repository:/root/.facefusion_repository

  facefusion-gpu:
    build: .
    runtime: nvidia
    environment:
      - FACEFUSION_EXECUTION_PROVIDER=cuda
      - CUDA_VISIBLE_DEVICES=0
    volumes:
      - ./data:/data
      - ~/.facefusion_repository:/root/.facefusion_repository
```

#### GitHub Codespaces

The devcontainer is configured for CPU mode by default. To enable GPU (if available):

1. Edit `.devcontainer/devcontainer.json`
2. Change environment variables:
   ```json
   "containerEnv": {
       "FACEFUSION_EXECUTION_PROVIDER": "cuda",
       "FACEFUSION_EXECUTION_PROVIDERS": "CUDAExecutionProvider,CPUExecutionProvider"
   }
   ```
3. Rebuild container: `F1` → `Dev Containers: Rebuild Container`

## Performance Comparison

Typical processing times for 1000 face swaps:

| Mode | Time | Relative Speed |
|------|------|---------------|
| CPU | ~30 minutes | 1x (baseline) |
| CUDA GPU | ~3-5 minutes | 6-10x faster |
| TensorRT GPU | ~2-3 minutes | 10-15x faster |
| CoreML (M2) | ~5-8 minutes | 4-6x faster |

*Times vary based on hardware, resolution, and complexity*

## Troubleshooting

### GPU Not Detected

**Problem:** System defaults to CPU even when GPU is available

**Solutions:**
1. Check CUDA installation:
   ```bash
   nvidia-smi
   python -c "import torch; print(torch.cuda.is_available())"
   ```

2. Verify environment variable:
   ```bash
   echo $FACEFUSION_EXECUTION_PROVIDER
   ```

3. Check execution providers:
   ```bash
   python -c "from facefusion_repository.config import Config; Config.print_execution_info()"
   ```

### Out of Memory (OOM) Errors

**Problem:** GPU runs out of memory during processing

**Solutions:**
1. Reduce batch size (process fewer faces at once)
2. Lower frame sample rate for videos
3. Use lower resolution models
4. Free GPU memory:
   ```python
   import torch
   torch.cuda.empty_cache()
   ```

### Slow Performance on GPU

**Problem:** GPU mode is not faster than CPU

**Solutions:**
1. Check GPU utilization:
   ```bash
   nvidia-smi -l 1  # Monitor every second
   ```

2. Ensure data transfer is optimized
3. Use TensorRT for production workloads
4. Check for CPU bottlenecks (I/O, preprocessing)

### Container GPU Access

**Problem:** Container cannot access GPU

**Solutions:**
1. Install nvidia-docker:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install nvidia-docker2
   sudo systemctl restart docker
   ```

2. Use `--gpus all` flag:
   ```bash
   docker run --gpus all ...
   ```

3. Verify GPU access in container:
   ```bash
   docker run --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
   ```

## Best Practices

### Development

- Use CPU mode for quick testing
- Switch to GPU for batch processing
- Use codespaces for cloud development

### Production

- Use GPU mode (CUDA/TensorRT) for best performance
- Set up proper monitoring
- Use containerized deployment
- Configure autoscaling based on GPU availability

### Cost Optimization

- Use CPU for low-volume workloads
- Reserve GPU for high-volume batch operations
- Consider spot instances for GPU workloads
- Implement request queuing

## Examples

### Basic Usage

```bash
# Check execution mode
python facefusion_repo_cli.py --version

# Initialize with CPU
FACEFUSION_EXECUTION_PROVIDER=cpu python facefusion_repo_cli.py init

# Process with GPU
FACEFUSION_EXECUTION_PROVIDER=cuda python facefusion_repo_cli.py batch-run --output ./output
```

### Programmatic Usage

```python
from facefusion_repository.config import Config
from facefusion_repository.repository.manager import RepositoryManager
from facefusion_repository.batch.executor import BatchExecutor

# Set execution mode
Config.EXECUTION_PROVIDER = 'cuda'

# Check configuration
print(f"Using: {Config.EXECUTION_PROVIDER}")
print(f"GPU Available: {Config.is_gpu_available()}")

# Use system normally
repo = RepositoryManager()
# ... rest of code
```

### Batch Script

```bash
#!/bin/bash
# process_batch.sh

# Set execution mode based on availability
if command -v nvidia-smi &> /dev/null; then
    export FACEFUSION_EXECUTION_PROVIDER=cuda
    echo "Using GPU mode"
else
    export FACEFUSION_EXECUTION_PROVIDER=cpu
    echo "Using CPU mode"
fi

# Process all queues
python facefusion_repo_cli.py batch-run --output ./output

echo "Processing complete!"
```

## References

- [ONNX Runtime Execution Providers](https://onnxruntime.ai/docs/execution-providers/)
- [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit)
- [TensorRT Documentation](https://docs.nvidia.com/deeplearning/tensorrt/)
- [CoreML Documentation](https://developer.apple.com/documentation/coreml)
