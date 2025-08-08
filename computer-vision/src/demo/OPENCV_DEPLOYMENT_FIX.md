# 🔧 OpenCV Deployment Fix Guide

## 🚨 The Problem

You're encountering this error:
```
ImportError: libGL.so.1: cannot open shared object file: No such file or directory
```

This happens because OpenCV is trying to use GUI libraries that aren't available in headless environments (like Docker containers or cloud deployments).

## ✅ The Solution

I've created several deployment options that handle this issue automatically:

### Option 1: Docker Deployment (Recommended)

**Using Docker Compose:**
```bash
# Navigate to the demo directory
cd computer-vision/src/demo

# Build and run with docker-compose
docker-compose up --build
```

**Using Docker directly:**
```bash
# Build the image
docker build -t planogram-vision .

# Run the container
docker run -p 8501:8501 planogram-vision
```

### Option 2: Deployment Scripts

**For Linux/macOS:**
```bash
# Make script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

**For Windows:**
```powershell
# Run deployment
.\deploy.ps1
```

### Option 3: Manual Fix

If you prefer to fix it manually:

1. **Install system dependencies (Linux):**
   ```bash
   sudo apt-get update
   sudo apt-get install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender1
   ```

2. **Set environment variables:**
   ```bash
   export DEBIAN_FRONTEND=noninteractive
   export DISPLAY=:99
   export OPENCV_VIDEOIO_PRIORITY_MSMF=0
   ```

3. **Use opencv-python-headless:**
   ```bash
   pip uninstall opencv-python
   pip install opencv-python-headless
   ```

## 🧪 Testing the Fix

Run the test script to verify everything is working:

```bash
python test_opencv.py
```

This will test:
- ✅ OpenCV import
- ✅ OpenCV functionality
- ✅ Ultralytics import (which depends on OpenCV)
- ✅ Environment variables

## 📁 What I've Created

1. **`Dockerfile`** - Complete Docker configuration with all OpenCV dependencies
2. **`docker-compose.yml`** - Easy Docker Compose setup
3. **`deploy.sh`** - Linux/macOS deployment script
4. **`deploy.ps1`** - Windows deployment script
5. **`packages.txt`** - Updated system dependencies
6. **`test_opencv.py`** - OpenCV test script
7. **Updated `DEPLOYMENT.md`** - Comprehensive deployment guide

## 🔍 Why This Happens

- OpenCV tries to use GUI libraries (`libGL.so.1`) for display
- In headless environments (containers, cloud), these libraries aren't available
- The error occurs when ultralytics imports OpenCV during startup
- The fix provides the necessary libraries and environment variables

## 🚀 Quick Start

1. **Choose your deployment method:**
   - Docker (easiest): `docker-compose up --build`
   - Script: `./deploy.sh` (Linux) or `.\deploy.ps1` (Windows)
   - Manual: Follow the manual fix steps above

2. **Test the deployment:**
   ```bash
   python test_opencv.py
   ```

3. **Run your application:**
   ```bash
   streamlit run app.py
   ```

## 🎯 Expected Result

After applying the fix, you should see:
- ✅ No more `libGL.so.1` errors
- ✅ OpenCV imports successfully
- ✅ Ultralytics works without issues
- ✅ Your Streamlit app runs normally

## 🔄 If You Still Have Issues

1. **Check the test script output** for specific error messages
2. **Verify environment variables** are set correctly
3. **Ensure you're using `opencv-python-headless`** instead of `opencv-python`
4. **Try the Docker approach** as it includes all dependencies

## 📞 Support

If you continue to have issues:
1. Run `python test_opencv.py` and share the output
2. Check the full error message
3. Verify your deployment environment (local, Docker, cloud)

---

**The deployment scripts and Dockerfile handle all of this automatically, so you shouldn't need to worry about these details!** 🎉
