# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Set environment variables for headless OpenCV
ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:99
ENV OPENCV_VIDEOIO_PRIORITY_MSMF=0
ENV OPENCV_VIDEOIO_DEBUG=1
ENV OPENCV_LOG_LEVEL=ERROR

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    # Core OpenCV dependencies
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libgthread-2.0-0 \
    # Additional OpenCV dependencies
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libatlas-base-dev \
    gfortran \
    libhdf5-dev \
    libhdf5-serial-dev \
    libhdf5-103 \
    # GUI libraries (for headless compatibility)
    libgtk2.0-dev \
    libgtk-3-dev \
    libqtgui4 \
    libqtwebkit4 \
    libqt4-test \
    python3-pyqt5 \
    # Additional development libraries
    libboost-all-dev \
    libopencv-dev \
    libopencv-contrib-dev \
    libopencv-python-dev \
    # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
COPY packages.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p config/planograms config/images weights

# Set environment variables for the application
ENV PLANOGRAM_CONFIG_DIR=/app/config/planograms
ENV PLANOGRAM_IMAGES_DIR=/app/config/images
ENV PLANOGRAM_WEIGHTS_DIR=/app/weights
ENV PLANOGRAM_TEMP_DIR=/tmp
ENV PLANOGRAM_MODEL_WEIGHTS=pick-instance-seg-v11-1.2.pt

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
