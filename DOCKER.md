# FaceFusion Docker Guide

This guide explains how to run FaceFusion in Docker containers with CPU or GPU support.

## Prerequisites

### For CPU Mode
- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose (usually included with Docker Desktop)

### For GPU Mode
- NVIDIA GPU with CUDA support
- NVIDIA Docker runtime ([Installation Guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html))
- Docker and Docker Compose

## Quick Start

### Option 1: Docker Compose (Recommended)

#### CPU Mode
```bash
# Start FaceFusion with CPU support
docker-compose --profile cpu up -d

# View logs
docker-compose logs -f facefusion-cpu

# Stop
docker-compose --profile cpu down
```

#### GPU Mode
```bash
# Start FaceFusion with GPU support
docker-compose --profile gpu up -d

# View logs
docker-compose logs -f facefusion-gpu

# Stop
docker-compose --profile gpu down
```

### Option 2: Manual Docker Build

#### CPU Mode
```bash
# Build
docker build --target cpu -t facefusion:cpu .

# Run
docker run -d \
  --name facefusion-cpu \
  -p 7860:7860 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/output:/app/output \
  -v ~/.facefusion_repository:/root/.facefusion_repository \
  facefusion:cpu
```

#### GPU Mode
```bash
# Build
docker build --target gpu -t facefusion:gpu .

# Run
docker run -d \
  --name facefusion-gpu \
  --gpus all \
  -p 7860:7860 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/output:/app/output \
  -v ~/.facefusion_repository:/root/.facefusion_repository \
  facefusion:gpu
```

## Accessing the UI

After starting the container, access FaceFusion at:
- **URL**: http://localhost:7860
- **Wait**: Initial startup may take 1-2 minutes for model downloads

## Development with VS Code

### Using Codespaces

1. **Open in Codespaces**
   - Go to your GitHub repository
   - Click "Code" → "Codespaces" → "Create codespace on branch"
   - Codespaces will automatically use the `.devcontainer` configuration

2. **Access the UI**
   - Codespaces will forward port 7860 automatically
   - Click the forwarded port notification to open the UI

3. **Run FaceFusion**
   ```bash
   python facefusion.py run
   ```

### Using Local Dev Container

1. **Open in VS Code**
   ```bash
   code .
   ```

2. **Reopen in Container**
   - Press `F1` or `Ctrl+Shift+P`
   - Select "Dev Containers: Reopen in Container"
   - VS Code will build and connect to the container

3. **Start Development**
   - Terminal opens automatically in the container
   - Extensions and settings are pre-configured

## CLI Commands in Docker

### Repository Management
```bash
# Initialize repository
docker exec facefusion-cpu python facefusion_repo_cli.py init

# Add face
docker exec facefusion-cpu python facefusion_repo_cli.py add --source /app/face.jpg --name "Person"

# List faces
docker exec facefusion-cpu python facefusion_repo_cli.py list

# Add character
docker exec facefusion-cpu python facefusion_repo_cli.py character-add --name "Alice"
```

### Batch Processing
```bash
# Analyze destination
docker exec facefusion-cpu python facefusion_repo_cli.py analyze-destination --source /app/video.mp4

# Run batch processing
docker exec facefusion-cpu python facefusion_repo_cli.py batch-run --output /app/output
```

## Volume Mounts

The Docker configuration mounts three important directories:

1. **`./models`** → `/app/models`
   - AI models are cached here
   - Persists between container restarts

2. **`./output`** → `/app/output`
   - Processed videos and images
   - Your results are saved here

3. **`~/.facefusion_repository`** → `/root/.facefusion_repository`
   - Face repository database
   - Preserves your face library

## Troubleshooting

### GPU Not Detected
```bash
# Check NVIDIA Docker runtime
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi

# If error, install NVIDIA Container Toolkit
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html
```

### Port Already in Use
```bash
# Change port mapping in docker-compose.yml
ports:
  - "8080:7860"  # Use port 8080 instead
```

### Container Won't Start
```bash
# Check logs
docker-compose logs facefusion-cpu

# Rebuild container
docker-compose build --no-cache
docker-compose up -d
```

### Out of Memory
```bash
# Increase Docker memory limit
# Docker Desktop → Settings → Resources → Memory
# Recommended: 8GB minimum, 16GB+ for large videos
```

## Performance Optimization

### CPU Mode
- **Threads**: Set `OMP_NUM_THREADS` environment variable
  ```yaml
  environment:
    - OMP_NUM_THREADS=8
  ```

### GPU Mode
- **Multiple GPUs**: Specify GPU IDs
  ```yaml
  environment:
    - CUDA_VISIBLE_DEVICES=0,1
  ```

- **Memory**: Limit GPU memory if needed
  ```yaml
  environment:
    - CUDA_VISIBLE_DEVICES=0
    - TF_FORCE_GPU_ALLOW_GROWTH=true
  ```

## Production Deployment

### Using Docker Swarm
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml facefusion
```

### Using Kubernetes
```bash
# Convert compose to Kubernetes manifests
kompose convert -f docker-compose.yml

# Apply to cluster
kubectl apply -f .
```

### Reverse Proxy (Nginx)
```nginx
server {
    listen 80;
    server_name facefusion.example.com;
    
    location / {
        proxy_pass http://localhost:7860;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## Security Considerations

1. **Network Exposure**: By default, containers bind to `0.0.0.0`. Use firewall rules for production.

2. **User Permissions**: Containers run as root. Consider creating a non-root user for production.

3. **Data Privacy**: Repository data contains facial embeddings. Secure volume mounts appropriately.

4. **API Authentication**: Add authentication layer (e.g., OAuth) for public deployments.

## Updates

### Update Container Image
```bash
# Pull latest code
git pull

# Rebuild
docker-compose build --no-cache

# Restart
docker-compose up -d
```

### Update Dependencies
```bash
# Edit requirements.txt
# Rebuild container
docker-compose build
```

## Uninstallation

```bash
# Stop containers
docker-compose down

# Remove images
docker rmi facefusion:cpu facefusion:gpu

# Remove volumes (WARNING: deletes data)
docker volume prune
```

## Support

- **Documentation**: See main README.md and USER_GUIDE.md
- **Issues**: GitHub Issues
- **Discord**: [FaceFusion Community](https://facefusion.io)

## License

Same as FaceFusion project (OpenRAIL-AS)
