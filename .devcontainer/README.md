# FaceFusion Repository System - Devcontainer Setup

This directory contains the devcontainer configuration for GitHub Codespaces and VS Code.

## Features

- **Python 3.12** environment
- **CPU/GPU Support**: Configurable execution provider
- **Docker-in-Docker**: For building and testing containers
- **NVIDIA CUDA**: GPU acceleration support (if available)
- **Auto-install dependencies**: Runs `pip install -r requirements.txt` on container creation

## Usage

### GitHub Codespaces

1. Open this repository in GitHub
2. Click "Code" → "Create codespace on main"
3. The environment will automatically set up with all dependencies

### VS Code Dev Containers

1. Install the "Dev Containers" extension
2. Open this repository in VS Code
3. Press F1 and select "Dev Containers: Reopen in Container"
4. The environment will build and open

## CPU vs GPU Mode

The container defaults to CPU mode for maximum compatibility.

### Using CPU Mode (Default)

No changes needed - the default configuration works on all systems.

### Using GPU Mode

**Requirements:**
- NVIDIA GPU with CUDA support
- nvidia-docker2 installed on host system
- Docker with GPU support

**Enable GPU:**

1. Edit `.devcontainer/devcontainer.json`
2. Uncomment or add the `runArgs` section:
   ```json
   "runArgs": [
       "--gpus=all"
   ],
   ```
3. Change `containerEnv`:
   ```json
   "containerEnv": {
       "FACEFUSION_EXECUTION_PROVIDER": "cuda",
       "FACEFUSION_EXECUTION_PROVIDERS": "CUDAExecutionProvider,CPUExecutionProvider"
   }
   ```
4. Rebuild the container

**Note**: If your system doesn't have GPU support, the default CPU configuration will work without any changes.

## Quick Start

Once the container is running:

```bash
# Initialize repository
python facefusion_repo_cli.py init

# Run example workflow
python example_workflow.py

# Check system status
python facefusion_repo_cli.py stats
```

## Environment Variables

- `FACEFUSION_EXECUTION_PROVIDER`: Set to `cpu` or `cuda`
- `FACEFUSION_EXECUTION_PROVIDERS`: Execution provider list (e.g., `CPUExecutionProvider` or `CUDAExecutionProvider`)

## Troubleshooting

### GPU Not Available

If CUDA/GPU is not available, the system will automatically fall back to CPU mode.

### Permission Issues

The container runs as non-root user `vscode`. Repository data is stored in `/home/vscode/.facefusion_repository`.

### Dependency Issues

If dependencies fail to install, manually run:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
