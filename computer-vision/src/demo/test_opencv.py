#!/usr/bin/env python3
"""
OpenCV Test Script
This script tests if OpenCV is working correctly in the deployment environment.
"""

import sys
import os

def test_opencv_import():
    """Test if OpenCV can be imported successfully."""
    try:
        import cv2
        print(f"✅ OpenCV imported successfully")
        print(f"   Version: {cv2.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import OpenCV: {e}")
        return False

def test_opencv_functionality():
    """Test basic OpenCV functionality."""
    try:
        import cv2
        import numpy as np
        
        # Create a simple test image
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        test_image[:] = (255, 0, 0)  # Blue color
        
        # Test basic operations
        gray = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        print("✅ OpenCV basic functionality test passed")
        return True
    except Exception as e:
        print(f"❌ OpenCV functionality test failed: {e}")
        return False

def test_ultralytics_import():
    """Test if ultralytics can be imported (which depends on OpenCV)."""
    try:
        from ultralytics import YOLO
        print("✅ Ultralytics imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import ultralytics: {e}")
        return False

def test_environment_variables():
    """Test if OpenCV-related environment variables are set."""
    env_vars = [
        'DEBIAN_FRONTEND',
        'DISPLAY',
        'OPENCV_VIDEOIO_PRIORITY_MSMF',
        'OPENCV_VIDEOIO_DEBUG',
        'OPENCV_LOG_LEVEL'
    ]
    
    print("🔧 Environment Variables:")
    for var in env_vars:
        value = os.environ.get(var, 'Not set')
        print(f"   {var}: {value}")

def main():
    """Run all tests."""
    print("🔍 OpenCV Deployment Test")
    print("=" * 40)
    
    # Test environment variables
    test_environment_variables()
    print()
    
    # Test OpenCV import
    opencv_import_ok = test_opencv_import()
    print()
    
    # Test OpenCV functionality
    opencv_func_ok = test_opencv_functionality()
    print()
    
    # Test ultralytics import
    ultralytics_ok = test_ultralytics_import()
    print()
    
    # Summary
    print("=" * 40)
    print("📊 Test Summary:")
    print(f"   OpenCV Import: {'✅ PASS' if opencv_import_ok else '❌ FAIL'}")
    print(f"   OpenCV Functionality: {'✅ PASS' if opencv_func_ok else '❌ FAIL'}")
    print(f"   Ultralytics Import: {'✅ PASS' if ultralytics_ok else '❌ FAIL'}")
    
    if all([opencv_import_ok, opencv_func_ok, ultralytics_ok]):
        print("\n🎉 All tests passed! OpenCV is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the deployment configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
