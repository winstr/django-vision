FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04
ENV DEBIAN_FRONTEND=noninteractive

RUN mkdir /workspace
WORKDIR /workspace

# Install packages
RUN apt-get update -y && apt-get install -y \
    gcc \
    g++ \
    git \
    zip \
    curl \
    wget \
    gnupg \
    libgl1 \
    libglib2.0-0 \
    libpython3-dev \
    libusb-1.0-0 \
    python3-dev \
    python3-pip

# Install Tensor RT (https://docs.nvidia.com/deeplearning/tensorrt/install-guide/index.html)
ENV os="ubuntu2204"
ENV tag="8.6.1-cuda-11.8"
RUN wget https://developer.nvidia.com/downloads/compute/machine-learning/tensorrt/secure/8.6.1/local_repos/nv-tensorrt-local-repo-${os}-${tag}_1.0-1_amd64.deb && \
    dpkg -i nv-tensorrt-local-repo-${os}-${tag}_1.0-1_amd64.deb && \
    cp /var/nv-tensorrt-local-repo-${os}-${tag}/*-keyring.gpg /usr/share/keyrings/ && \
    apt-get update -y && apt-get install -y tensorrt && \
    rm -rf nv-tensorrt-local-repo-${os}-${tag}_1.0-1_amd64.deb

RUN pip3 install --upgrade pip && \
    pip3 install --upgrade tensorrt && \
    pip install lit torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

RUN apt-get install -y openssh-server vim
ENTRYPOINT service ssh restart && bash
