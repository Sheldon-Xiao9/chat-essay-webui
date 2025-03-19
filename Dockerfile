FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

# Install Python and pip
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    python3.11-dev \
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Configure pip to use tuna mirror
RUN python3.11 -m pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    python3.11 -m pip config set install.trusted-host pypi.tuna.tsinghua.edu.cn

# Set CUDA environment variables
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}
ENV TORCH_CUDA_ARCH_LIST="7.0 7.5 8.0 8.6"

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python packages with retries
RUN python3.11 -m pip install --no-cache-dir --retries 3 --timeout 600 -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p database chat_history models

# Set environment variables
ENV HOST=0.0.0.0
ENV PORT=3791

# Expose the port
EXPOSE 3791

# Run the application
CMD ["python3.11", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3791"]
