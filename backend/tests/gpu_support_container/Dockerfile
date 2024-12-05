# Start from the NVIDIA CUDA base image
FROM nvidia/cuda:11.6.1-devel-ubuntu20.04

# Install Python and any required tools
RUN apt-get update && apt-get install -y python3 python3-pip

# Optional: Set python3 as the default python
RUN ln -s /usr/bin/python3 /usr/local/bin/python

# Verify nvidia-smi
CMD ["nvidia-smi"]
