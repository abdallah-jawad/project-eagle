# 🎨 Interactive Drawing Setup Guide

## 🚀 Quick Setup

To enable interactive drawing in the planogram configuration creator, you need to install the `streamlit-drawable-canvas-fix` component (a compatibility-fixed version).

### 1. Install the Component

```bash
pip install streamlit-drawable-canvas-fix
```

**Note:** We use `streamlit-drawable-canvas-fix` instead of the original `streamlit-drawable-canvas` because it's compatible with newer versions of Streamlit and fixes the `AttributeError: module 'streamlit.elements.image' has no attribute 'image_to_url'` error.

### 2. Restart Your Streamlit App

After installation, **restart your Streamlit app**:

```bash
# Stop the current app (Ctrl+C)
# Then restart:
streamlit run app.py
```

## 🎯 How to Use Interactive Drawing

Once installed, you'll have access to powerful interactive drawing features:

### **Drawing Controls (Sidebar)**
- **Drawing Mode**: Select "rect" to draw rectangles for sections
- **Transform Mode**: Select "transform" to move/resize existing rectangles  
- **Stroke Settings**: Customize line width and color
- **Real-time Updates**: See changes instantly

### **Drawing Process**
1. **Upload your planogram image**
2. **Select "rect" mode** in the sidebar
3. **Click and drag** on the image to draw section boundaries
4. **Switch to "transform"** to adjust existing rectangles
5. **Configure each section** with items and expected counts
6. **Generate your configuration**

## ✨ Features You'll Get

### **Interactive Canvas**
- ✅ Click and drag to draw rectangles
- ✅ Visual feedback as you draw
- ✅ Undo/redo functionality
- ✅ Transform existing shapes

### **Automatic Coordinate Calculation**
- ✅ Precise pixel coordinates
- ✅ Automatic scaling between canvas and image
- ✅ Real-time coordinate display

### **Enhanced User Experience**
- ✅ Visual section preview
- ✅ Drag to resize sections
- ✅ No manual coordinate entry needed
- ✅ Professional drawing interface

## 🔧 Troubleshooting

### **"streamlit-drawable-canvas not installed" Error**
```bash
pip install streamlit-drawable-canvas-fix
# Then restart your Streamlit app
```

### **AttributeError: module 'streamlit.elements.image' has no attribute 'image_to_url'**
This error occurs with the original `streamlit-drawable-canvas` package. The solution is to use the fixed version:
```bash
pip uninstall streamlit-drawable-canvas
pip install streamlit-drawable-canvas-fix
# Then restart your Streamlit app
```

### **Canvas Not Appearing**
1. Make sure you restarted the Streamlit app after installation
2. Check that the package installed correctly: `pip list | grep streamlit-drawable-canvas-fix`
3. Try refreshing your browser

### **Drawing Not Working**
1. Make sure you selected "rect" mode in the sidebar
2. Try clicking and dragging (not just clicking)
3. Check that the canvas has focus (click on it first)

## 📦 What Gets Installed

The `streamlit-drawable-canvas-fix` package provides:
- **Fabric.js-based drawing canvas**
- **Multiple drawing modes** (rectangles, circles, lines, freehand)
- **Object manipulation** (move, resize, rotate)
- **Export capabilities** (image data and object coordinates)
- **Undo/redo functionality**
- **Compatibility with modern Streamlit versions**

## 🆚 Before vs After

### **Without Interactive Drawing**
- ❌ Manual coordinate entry
- ❌ No visual feedback
- ❌ Prone to errors
- ❌ Time-consuming

### **With Interactive Drawing**
- ✅ Visual rectangle drawing
- ✅ Real-time preview
- ✅ Precise and intuitive
- ✅ Fast and efficient

## 🎉 Ready to Draw!

Once you have `streamlit-drawable-canvas-fix` installed, you'll see:
- 🎨 **Interactive drawing controls** in the sidebar
- 🖼️ **Visual canvas** overlaid on your planogram image
- 📐 **Automatic coordinate calculation** 
- 🎯 **Professional drawing experience**

### **Installation Summary:**
```bash
# Install the fixed version
pip install streamlit-drawable-canvas-fix

# Restart your app
streamlit run app.py
```

Happy drawing! 🎨 