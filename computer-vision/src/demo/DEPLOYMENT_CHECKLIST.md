# ✅ Streamlit Cloud Deployment Checklist

## 📁 Required Files

- [ ] `app.py` - Main Streamlit application
- [ ] `requirements.txt` - Python dependencies (with `opencv-python-headless`)
- [ ] `packages.txt` - System dependencies for OpenCV
- [ ] `setup.sh` - Setup script for environment variables
- [ ] `.streamlit/config.toml` - Streamlit configuration
- [ ] `.gitignore` - Git ignore file
- [ ] `config/planograms/` - Directory for planogram JSON files
- [ ] `config/images/` - Directory for planogram images
- [ ] `weights/` - Directory for model weights
- [ ] `weights/pick-instance-seg-v11-1.2.pt` - Model weights file

## 🔧 Configuration Check

- [ ] `requirements.txt` contains `opencv-python-headless>=4.8.0`
- [ ] `packages.txt` contains `libgl1-mesa-glx` and other OpenCV dependencies
- [ ] `setup.sh` is executable and sets environment variables
- [ ] `.streamlit/config.toml` has `headless = true`
- [ ] Model weights file is in the correct location
- [ ] Configuration directories exist

## 🚀 Deployment Steps

### 1. Local Testing
- [ ] Test OpenCV import: `python test_opencv.py`
- [ ] Test local Streamlit app: `streamlit run app.py`
- [ ] Verify no `libGL.so.1` errors

### 2. GitHub Preparation
- [ ] All files committed to repository
- [ ] Repository is public (for free Streamlit Cloud)
- [ ] Branch name is correct (usually `main`)

### 3. Streamlit Cloud Setup
- [ ] Go to [share.streamlit.io](https://share.streamlit.io)
- [ ] Sign in with GitHub account
- [ ] Create new app
- [ ] Set repository: `your-username/your-repo-name`
- [ ] Set branch: `main`
- [ ] Set main file path: `computer-vision/src/demo/app.py`
- [ ] Choose app URL

### 4. Environment Variables (Optional)
- [ ] `DEBIAN_FRONTEND=noninteractive`
- [ ] `DISPLAY=:99`
- [ ] `OPENCV_VIDEOIO_PRIORITY_MSMF=0`
- [ ] `OPENCV_VIDEOIO_DEBUG=1`
- [ ] `OPENCV_LOG_LEVEL=ERROR`
- [ ] `PLANOGRAM_CONFIG_DIR=/app/config/planograms`
- [ ] `PLANOGRAM_IMAGES_DIR=/app/config/images`
- [ ] `PLANOGRAM_WEIGHTS_DIR=/app/weights`
- [ ] `PLANOGRAM_TEMP_DIR=/tmp`
- [ ] `PLANOGRAM_MODEL_WEIGHTS=pick-instance-seg-v11-1.2.pt`

## 🧪 Post-Deployment Testing

- [ ] App loads without errors
- [ ] No `libGL.so.1` error messages
- [ ] OpenCV imports successfully
- [ ] Ultralytics loads without issues
- [ ] Model weights load correctly
- [ ] Image upload works
- [ ] Interactive drawing interface functions
- [ ] Configuration files load properly
- [ ] No memory or timeout issues

## 🔍 Troubleshooting

### If OpenCV Error Persists
- [ ] Check `packages.txt` is in correct location
- [ ] Verify all system dependencies are listed
- [ ] Ensure using `opencv-python-headless`
- [ ] Check deployment logs in Streamlit Cloud

### If Model Weights Not Found
- [ ] Verify file path in `weights/` directory
- [ ] Check `PLANOGRAM_MODEL_WEIGHTS` environment variable
- [ ] Ensure file is committed to repository

### If Configuration Issues
- [ ] Check `config/` directory structure
- [ ] Verify environment variables are set
- [ ] Test file paths in cloud environment

## 📊 Performance Monitoring

- [ ] Monitor memory usage in Streamlit Cloud dashboard
- [ ] Check for timeout issues
- [ ] Optimize image sizes if needed
- [ ] Use caching for expensive operations

## 🔄 Updates

- [ ] Make code changes
- [ ] Test locally first
- [ ] Commit and push to GitHub
- [ ] Verify automatic redeployment
- [ ] Test updated functionality

---

**✅ Complete this checklist before deploying to ensure a smooth deployment!**
