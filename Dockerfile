# FaceFusion - Docker Support
# Supports both CPU and GPU (CUDA) modes

# Base stage with common dependencies
FROM python:3.12-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860

# Expose port for Gradio UI
EXPOSE 7860

# CPU-only stage
FROM base as cpu

# No additional CUDA dependencies needed
CMD ["python", "facefusion.py", "run"]

# GPU stage with CUDA support
FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04 as gpu-base

# Install Python 3.12
RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.12 \
    python3.12-venv \
    python3-pip \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.12 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Install GPU-specific dependencies
RUN pip3 install --no-cache-dir onnxruntime-gpu==1.22.1

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860
ENV CUDA_VISIBLE_DEVICES=0

EXPOSE 7860

# GPU stage
FROM gpu-base as gpu
CMD ["python", "facefusion.py", "run"]
