#!/usr/bin/env python3
"""
Main application module for the Computer Vision service.
"""

import time
import logging
import sys
import cv2
import numpy as np
from dependencies.kvs import KVSClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def process_kvs_stream(stream_name: str):
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
            
            # Process the chunk data (this is a simplified example)
            # In a real application, you would decode the video data and process frames
            logger.info(f"Received chunk from stream {stream_name} at {timestamp}")
            
            # Example: If the data is H.264 encoded, you might decode it like this:
            # Note: This is a simplified example and would need proper error handling
            # and frame extraction logic in a production environment
            try:
                # Convert bytes to numpy array (this is a simplified example)
                # In a real application, you would use a proper video decoder
                # nparr = np.frombuffer(data, np.uint8)
                # frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                # Process the frame (example: display or save it)
                # cv2.imshow('Frame', frame)
                # cv2.waitKey(1)
                
                # Or save the frame
                # cv2.imwrite(f'frame_{timestamp.timestamp()}.jpg', frame)
                
                # For now, just log the size of the chunk
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
    # Example usage of the KVS stream processing
    # Replace 'your-stream-name' with your actual KVS stream name
    # process_kvs_stream('your-stream-name')
    
    # Or run the hello world example
    hello_world() 