#!/usr/bin/env python3
"""
Main application module for the Computer Vision service.
"""

import time
import cv2
import os
from pathlib import Path
from dependencies.kvs import KVSClient
from dependencies.inference import InferenceEngine
from dependencies.image import draw_detections
from utils import setup_logging

# Setup logging
logger = setup_logging()

class App:
    def __init__(self):
        self.logger = logger
        self.kvs_client = KVSClient()
        self.inference_engine = InferenceEngine(use_gpu=True)

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

    def run_test_video(self, video_name: str, output_name: str = None, show_live: bool = True, frame_interval: int = 1):
        """
        Run object detection on a video file and optionally display/save the results.
        
        Args:
            video_name: Name of the video file to process (e.g. 'video-test-1.mp4')
            output_name: Optional name for the output video file. If None, will use 'output_{video_name}'
            show_live: Whether to display the video with detections in real-time
            frame_interval: Process every N-th frame (e.g. 1 = every frame, 2 = every other frame, etc.)
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
        if frame_interval > 1:
            self.logger.info(f"Processing every {frame_interval}-th frame")
        
        try:
            # Open video file
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                self.logger.error(f"Failed to open video file: {video_path}")
                return
                
            # Get video properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Adjust FPS for frame interval
            adjusted_fps = fps / frame_interval
            
            self.logger.info(f"Video properties: {width}x{height} @ {fps} FPS, {total_frames} frames")
            self.logger.info(f"Adjusted output FPS: {adjusted_fps:.2f}")
            
            # Set up video writer if output is requested
            writer = None
            if output_name:
                output_path = test_dir / output_name
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                writer = cv2.VideoWriter(str(output_path), fourcc, adjusted_fps, (width, height))
                self.logger.info(f"Will save output to: {output_path}")
            
            # Process each frame
            frame_count = 0
            processed_frames = 0
            last_log_time = time.time()
            log_interval = 1.0  # Log every 1 second
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                    
                frame_count += 1
                
                # Skip frames based on interval
                if frame_count % frame_interval != 0:
                    continue
                    
                processed_frames += 1
                current_time = time.time()
                
                # Log progress every second
                if current_time - last_log_time >= log_interval:
                    self.logger.info(f"Processing frame {processed_frames}/{total_frames//frame_interval} ({processed_frames/(total_frames//frame_interval)*100:.1f}%)")
                    last_log_time = current_time
                
                # Run inference
                results = self.inference_engine.run_inference(frame)
                
                # Draw detections
                vis_frame = draw_detections(frame, results)
                
                # Write frame to output video if requested
                if writer:
                    writer.write(vis_frame)
                
                # Display frame if requested
                if show_live:
                    cv2.imshow("Video Detection", vis_frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
            
            # Clean up
            cap.release()
            if writer:
                writer.release()
            if show_live:
                cv2.destroyAllWindows()
                
            self.logger.info(f"Video processing completed. Processed {processed_frames} frames out of {total_frames} total frames.")
                
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
    app.run_test_video("video-test-1.mp4", output_name="output_video.mp4", show_live=False, frame_interval=3)