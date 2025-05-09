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
            
        self.kvs_client = KVSClient()
        self.inference_engine = InferenceEngine(use_gpu=True)
        self.video_processor = VideoProcessor(self.inference_engine)

    def run_test_single_image(self, image_name: str):
        """
        Run a sanity test on a single image using the inference engine.
        
        Args:
            image_name: Name of the PNG image file to process (e.g. 'test.png')
        """
        self.logger.info("Starting sanity test")
        
        # Get test image path
        test_dir = Path("test")
        if not test_dir.exists():
            self.logger.error("Test directory not found")
            return
            
        # Construct image path
        test_image_path = test_dir / image_name
        if not test_image_path.exists():
            self.logger.error(f"Image file not found: {test_image_path}")
            return
            
        self.logger.info(f"Testing with image: {test_image_path}")
        
        try:
            # Read image
            image = cv2.imread(str(test_image_path))
            if image is None:
                self.logger.error(f"Failed to read image: {test_image_path}")
                return
                
            # Get original dimensions
            orig_height, orig_width = image.shape[:2]
            self.logger.info(f"Original image dimensions: {orig_width}x{orig_height}")
                
            # Run inference
            results = self.inference_engine.run_inference(image)
            
            # Print results
            self.logger.info(f"Found {len(results)} detections:")
            for i, detection in enumerate(results, 1):
                self.logger.info(f"Detection {i}:")
                self.logger.info(f"  Class: {detection.class_name} (ID: {detection.class_id})")
                self.logger.info(f"  Confidence: {detection.confidence:.2f}")
                self.logger.info(f"  Bounding Box: {detection.bbox}")
            
            # Draw detections on the image
            vis_image = draw_detections(image, results)
            
            # Save the visualization
            output_path = test_dir / f"output_{image_name}"
            cv2.imwrite(str(output_path), vis_image)
            self.logger.info(f"Visualization saved to: {output_path}")
            
            # Display the image
            cv2.imshow("Detections", vis_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
                
        except Exception as e:
            self.logger.error(f"Error during sanity test: {str(e)}")
            raise

    def run_test_video(self, video_name: str, output_name: str = None, show_live: bool = True):
        """
        Run object detection on a video file and optionally display/save the results.
        
        Args:
            video_name: Name of the video file to process (e.g. 'video-test-1.mp4')
            output_name: Optional name for the output video file. If None, will use 'output_{video_name}'
            show_live: Whether to display the video with detections in real-time
        """
        self.logger.info("Starting video test")
        
        # Get test video path
        test_dir = Path("test")
        if not test_dir.exists():
            self.logger.error("Test directory not found")
            return
            
        # Construct video path
        video_path = test_dir / video_name
        if not video_path.exists():
            self.logger.error(f"Video file not found: {video_path}")
            return
            
        self.logger.info(f"Processing video: {video_path}")
        
        try:
            if show_live:
                success, message = self.video_processor.process_video_file_live(str(video_path))
            else:
                output_path = str(test_dir / output_name) if output_name else None
                success, message = self.video_processor.process_video_file(str(video_path), output_path)
                
            if not success:
                self.logger.error(message)
                
        except Exception as e:
            self.logger.error(f"Error during video test: {str(e)}")
            raise

def hello_world():
    """
    Print 'Hello World' indefinitely with a timestamp.
    
    This function runs in an infinite loop, printing a message every 5 seconds.
    """
    logger.info("Starting Hello World service")
    
    while True:
        logger.info("Hello World!")
        time.sleep(5)

if __name__ == "__main__":
    app = App()
    # app.run_test_single_image("image3.png")
    app.run_test_video("video-test-1.mp4", output_name="output_video.mp4", show_live=True)