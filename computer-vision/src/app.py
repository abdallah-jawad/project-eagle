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
from utils import setup_logging

# Setup logging
logger = setup_logging()

class App:
    def __init__(self):
        self.logger = logger
        self.kvs_client = KVSClient()
        self.inference_engine = InferenceEngine()

    def run_sanity_test(self, image_name: str):
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
            
            # Create a copy of the image for visualization
            vis_image = image.copy()
            
            # Colors for different classes
            colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255)]
            
            # Draw each detection
            for i, detection in enumerate(results, 1):
                self.logger.info(f"Detection {i}:")
                self.logger.info(f"  Class: {detection.class_name} (ID: {detection.class_id})")
                self.logger.info(f"  Confidence: {detection.confidence:.2f}")
                self.logger.info(f"  Bounding Box: {detection.bbox}")
                
                # Get normalized bounding box coordinates
                x1, y1, x2, y2 = detection.bbox
                
                # Convert normalized coordinates to pixel coordinates
                x1 = int(x1 * orig_width)
                y1 = int(y1 * orig_height)
                x2 = int(x2 * orig_width)
                y2 = int(y2 * orig_height)
                
                # Get color for this class
                color = colors[detection.class_id % len(colors)]
                
                # Draw rectangle
                cv2.rectangle(vis_image, (x1, y1), (x2, y2), color, 2)
                
                # Add label with class name and confidence
                label = f"{detection.class_name} ({detection.confidence:.2f})"
                label_size, baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                y1_label = max(y1, label_size[1])
                
                # Draw label background
                cv2.rectangle(vis_image, 
                            (x1, y1_label - label_size[1] - baseline),
                            (x1 + label_size[0], y1_label + baseline),
                            color, cv2.FILLED)
                            
                # Draw label text
                cv2.putText(vis_image, label, (x1, y1_label),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            
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

def process_stream(stream_name: str):
    """
    Process a Kinesis Video Stream by iterating through chunks and processing frames.
    
    Args:
        stream_name: Name of the Kinesis Video stream to process
    """
    logger.info(f"Starting to process KVS stream: {stream_name}")
    
    # Initialize the KVS client
    kvs_client = KVSClient()
    
    try:
        # Get the media stream generator
        media_stream = kvs_client.get_media_stream(stream_name)
        
        # Process each chunk in the stream
        for chunk in media_stream:
            # Extract the data from the chunk
            data = chunk['data']
            timestamp = chunk['timestamp']
            stream_name = chunk['stream_name']
            
            logger.info(f"Received chunk from stream {stream_name} at {timestamp}")
            
            try:
                logger.info(f"Chunk size: {len(data)} bytes")
                
            except Exception as e:
                logger.error(f"Error processing chunk: {str(e)}")
                
    except Exception as e:
        logger.error(f"Error processing KVS stream {stream_name}: {str(e)}")
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
    # Example usage with a specific image name
    app.run_sanity_test("image3.png")