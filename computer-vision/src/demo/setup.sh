#!/bin/bash

# Streamlit Cloud Setup Script
# This script runs during Streamlit Cloud deployment to handle OpenCV dependencies

set -e

echo "🚀 Setting up Planogram Vision Demo for Streamlit Cloud..."

# Set environment variables for headless OpenCV
export DEBIAN_FRONTEND=noninteractive
export DISPLAY=:99
export OPENCV_VIDEOIO_PRIORITY_MSMF=0
export OPENCV_VIDEOIO_DEBUG=1
export OPENCV_LOG_LEVEL=ERROR

# Set application environment variables
export PLANOGRAM_CONFIG_DIR=/app/config/planograms
export PLANOGRAM_IMAGES_DIR=/app/config/images
export PLANOGRAM_WEIGHTS_DIR=/app/weights
export PLANOGRAM_TEMP_DIR=/tmp
export PLANOGRAM_MODEL_WEIGHTS=pick-instance-seg-v11-1.2.pt

# Create necessary directories
mkdir -p config/planograms config/images weights temp

echo "✅ Setup completed successfully"
