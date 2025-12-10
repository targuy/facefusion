FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN useradd -m -s /bin/bash vscode && \
    mkdir -p /home/vscode/.facefusion_repository && \
    chown -R vscode:vscode /home/vscode

USER vscode

# Set environment variables for CPU/GPU mode
ENV FACEFUSION_EXECUTION_PROVIDER=cpu
ENV PYTHONUNBUFFERED=1

CMD ["/bin/bash"]
