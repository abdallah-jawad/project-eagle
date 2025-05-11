import boto3
import cv2
from typing import Optional
from utils import setup_logging

logger = setup_logging()

class KVSClient:
    """Client for interacting with Kinesis Video Streams and creating OpenCV capture objects"""
    
    def __init__(self):
        self.kvs_client = boto3.client('kinesisvideo')
        self.logger = logger

    def get_stream_url(self, stream_name: str) -> Optional[str]:
        """Get the endpoint URL for a KVS stream
        
        Args:
            stream_name: Name/ID of the KVS stream
            
        Returns:
            Optional[str]: URL endpoint for the stream if successful, None if failed
        """
        try:
            # Get data endpoint for the stream
            endpoint = self.kvs_client.get_data_endpoint(
                StreamName=stream_name,
                APIName='GET_MEDIA'
            )['DataEndpoint']
            
            return endpoint
        except Exception as e:
            self.logger.error(f"Failed to get KVS endpoint for stream {stream_name}: {str(e)}")
            return None

    def create_capture(self, camera_id: str, stream_name: str) -> Optional[cv2.VideoCapture]:
        """Create an OpenCV VideoCapture object from a KVS stream
        
        Args:
            camera_id: ID of the camera
            stream_name: Name/ID of the KVS stream
            
        Returns:
            Optional[cv2.VideoCapture]: VideoCapture object if successful, None if failed
        """
        try:
            stream_url = self.get_stream_url(stream_name)
            if not stream_url:
                return None
                
            # Create OpenCV capture object
            capture = cv2.VideoCapture(stream_url)
            if not capture.isOpened():
                self.logger.error(f"Failed to open video capture for camera {camera_id}")
                return None
                
            return capture
            
        except Exception as e:
            self.logger.error(f"Failed to create capture for camera {camera_id}: {str(e)}")
            return None
