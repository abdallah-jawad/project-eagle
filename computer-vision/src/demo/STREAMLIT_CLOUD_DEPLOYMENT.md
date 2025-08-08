# 🚀 Streamlit Cloud Deployment Guide

## Overview

This guide will help you deploy your Planogram Vision Demo to Streamlit Cloud without the OpenCV `libGL.so.1` error.

## 📁 Required Files for Streamlit Cloud

Your repository should contain these files in the `computer-vision/src/demo/` directory:

```
demo/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies (with opencv-python-headless)
├── packages.txt                    # System dependencies for OpenCV
├── setup.sh                        # Setup script for environment variables
├── .streamlit/
│   └── config.toml                 # Streamlit configuration
├── config/                         # Configuration directories
│   ├── planograms/                 # Planogram JSON files
│   └── images/                     # Planogram images
└── weights/                        # Model weights directory
    └── pick-instance-seg-v11-1.2.pt
```

## 🚀 Deployment Steps

### 1. Prepare Your Repository

1. **Ensure all files are committed to GitHub:**
   ```bash
   git add .
   git commit -m "Add Streamlit Cloud deployment files"
   git push origin main
   ```

2. **Verify your repository structure:**
   - All files should be in the correct locations
   - Model weights should be in the `weights/` directory
   - Configuration files should be in the `config/` directory

### 2. Deploy to Streamlit Cloud

1. **Go to [share.streamlit.io](https://share.streamlit.io)**
2. **Sign in with your GitHub account**
3. **Click "New app"**
4. **Configure your deployment:**
   - **Repository:** `your-username/your-repo-name`
   - **Branch:** `main` (or your default branch)
   - **Main file path:** `computer-vision/src/demo/app.py`
   - **App URL:** Choose your preferred URL

### 3. Advanced Settings (Optional)

In the Streamlit Cloud dashboard, you can set these environment variables:

```
DEBIAN_FRONTEND=noninteractive
DISPLAY=:99
OPENCV_VIDEOIO_PRIORITY_MSMF=0
OPENCV_VIDEOIO_DEBUG=1
OPENCV_LOG_LEVEL=ERROR
PLANOGRAM_CONFIG_DIR=/app/config/planograms
PLANOGRAM_IMAGES_DIR=/app/config/images
PLANOGRAM_WEIGHTS_DIR=/app/weights
PLANOGRAM_TEMP_DIR=/tmp
PLANOGRAM_MODEL_WEIGHTS=pick-instance-seg-v11-1.2.pt
```

## 🔧 How the Fix Works

### 1. **packages.txt**
- Installs system dependencies required by OpenCV
- Includes `libgl1-mesa-glx` and other GUI libraries
- Streamlit Cloud automatically installs these packages

### 2. **requirements.txt**
- Uses `opencv-python-headless` instead of `opencv-python`
- Includes all necessary Python dependencies
- Optimized for cloud deployment

### 3. **setup.sh**
- Sets environment variables for headless operation
- Creates necessary directories
- Runs during deployment initialization

### 4. **.streamlit/config.toml**
- Configures Streamlit for production deployment
- Sets headless mode and other optimizations

## 🧪 Testing Your Deployment

After deployment, test these features:

1. **OpenCV Import:** The app should start without `libGL.so.1` errors
2. **Model Loading:** Ultralytics should import successfully
3. **Image Processing:** Upload and process planogram images
4. **Drawing Interface:** Interactive drawing should work
5. **File Uploads:** Configuration and image uploads should work

## 🔍 Troubleshooting

### Common Issues

1. **"libGL.so.1: cannot open shared object file"**
   - **Solution:** Ensure `packages.txt` is in the correct location
   - **Check:** Verify all system dependencies are listed

2. **Model weights not found**
   - **Solution:** Ensure model file is in `weights/` directory
   - **Check:** Verify `PLANOGRAM_MODEL_WEIGHTS` environment variable

3. **Configuration files not loading**
   - **Solution:** Check `config/` directory structure
   - **Check:** Verify environment variables are set correctly

4. **Memory issues**
   - **Solution:** Optimize image sizes for cloud deployment
   - **Check:** Monitor memory usage in Streamlit Cloud dashboard

### Debug Steps

1. **Check deployment logs** in Streamlit Cloud dashboard
2. **Verify file paths** are correct for cloud environment
3. **Test locally** with the same configuration
4. **Use the test script:** `python test_opencv.py`

## 📊 Performance Optimization

### For Streamlit Cloud

1. **Image Optimization:**
   - Resize large images before processing
   - Use appropriate image formats (JPEG for photos, PNG for graphics)

2. **Memory Management:**
   - Clear variables after processing
   - Use generators for large datasets

3. **Caching:**
   - Use `@st.cache_data` for expensive computations
   - Cache model loading and preprocessing

## 🔄 Updating Your Deployment

1. **Make changes to your code**
2. **Commit and push to GitHub:**
   ```bash
   git add .
   git commit -m "Update deployment"
   git push origin main
   ```
3. **Streamlit Cloud will automatically redeploy**

## 📞 Support

If you encounter issues:

1. **Check Streamlit Cloud logs** for specific error messages
2. **Verify all required files** are present in your repository
3. **Test the OpenCV fix locally** first
4. **Review the deployment configuration** in Streamlit Cloud dashboard

## 🎉 Success Indicators

Your deployment is successful when:

- ✅ App loads without OpenCV errors
- ✅ Model weights load successfully
- ✅ Image upload and processing works
- ✅ Interactive drawing interface functions
- ✅ Configuration files load properly
- ✅ No memory or timeout issues

---

**The `packages.txt` and `opencv-python-headless` combination should resolve your OpenCV issues in Streamlit Cloud!** 🚀
