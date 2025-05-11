#!/usr/bin/env python3
"""
Main application module for the Computer Vision service.
"""

import time
import cv2
from pathlib import Path
from dependencies.kvs import KVSClient
from service.inference import InferenceEngine
from service.image import draw_detections
from dependencies.setup_cuda import setup_cuda_environment
from service.video_processor import VideoProcessor
from utils import setup_logging

# Setup logging
logger = setup_logging()

class App:
    def __init__(self):
        self.logger = logger
        
        # Set up CUDA environment before initializing inference engine
        if not setup_cuda_environment():
            self.logger.warning("Failed to set up CUDA environment, falling back to CPU")
            
        self.app_config_client = AppConfigClient()

    def initialize_system(self):

        # 1. Fetch KVS Stream Configurations from AppConfig
        cameras = self.app_config_client.get_kvs_streams()

        # 2. Create a KVS - CV Capture for each stream
        for camera in cameras:
            capture = self.kvs_client.create_capture(camera.camera_id, camera.kvs_stream_id)
            if capture:
                camera.capture = capture 

        # 3. Call manager.py to start and manage cameras
        self.manager = CameraManager(cameras)


if __name__ == "__main__":
    app = App()
    # app.run_test_single_image("image3.png")
    app.run_test_video("video-test-1.mp4", output_name="output_video.mp4", show_live=True)