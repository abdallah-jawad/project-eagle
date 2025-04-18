import boto3
import logging
from typing import Optional, Generator, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class KVSClient:
    """Client for interacting with Amazon Kinesis Video Streams."""
    
    def __init__(self):
        """Initialize the KVS client."""
        self.kvs_client = boto3.client('kinesisvideo')
        self.kvs_archive = None
        
    def get_frame(self, stream_name: str, timestamp: Optional[datetime] = None) -> bytes:
        """
        Get a single frame from a Kinesis Video stream.
        
        Args:
            stream_name: Name of the Kinesis Video stream
            timestamp: Optional timestamp to get frame from specific time
            
        Returns:
            Frame data as bytes
            
        Raises:
            Exception: If frame cannot be retrieved
        """
        try:
            # Get data endpoint for the stream
            endpoint = self.kvs_client.get_data_endpoint(
                StreamName=stream_name,
                APIName='GET_MEDIA'
            )['DataEndpoint']
            
            # Create archive client if not exists
            if not self.kvs_archive:
                self.kvs_archive = boto3.client(
                    'kinesis-video-archived-media',
                    endpoint_url=endpoint
                )
            
            # Get the frame
            response = self.kvs_archive.get_media(
                StreamName=stream_name,
                StartSelector={
                    'StartSelectorType': 'NOW' if not timestamp else 'TIMESTAMP',
                    **({"StartTimestamp": timestamp} if timestamp else {})
                }
            )
            
            return response['Payload'].read()
            
        except Exception as e:
            logger.error(f"Failed to get frame from stream {stream_name}: {str(e)}")
            raise
            
    def get_media_stream(self, stream_name: str, start_timestamp: Optional[datetime] = None) -> Generator[Dict[str, Any], None, None]:
        """
        Get a media stream from a Kinesis Video stream that can be iterated through.
        
        Args:
            stream_name: Name of the Kinesis Video stream
            start_timestamp: Optional timestamp to start streaming from
            
        Returns:
            Generator that yields chunks of media data with metadata
            
        Raises:
            Exception: If media stream cannot be retrieved
        """
        try:
            # Get data endpoint for the stream
            endpoint = self.kvs_client.get_data_endpoint(
                StreamName=stream_name,
                APIName='GET_MEDIA'
            )['DataEndpoint']
            
            # Create archive client if not exists
            if not self.kvs_archive:
                self.kvs_archive = boto3.client(
                    'kinesis-video-archived-media',
                    endpoint_url=endpoint
                )
            
            # Get the media stream
            response = self.kvs_archive.get_media(
                StreamName=stream_name,
                StartSelector={
                    'StartSelectorType': 'NOW' if not start_timestamp else 'TIMESTAMP',
                    **({"StartTimestamp": start_timestamp} if start_timestamp else {})
                }
            )
            
            # Get the payload stream
            payload = response['Payload']
            
            # Process the stream in chunks
            for chunk in payload:
                # Each chunk contains a fragment of the media stream
                # You can process each chunk as needed
                yield {
                    'data': chunk,
                    'timestamp': datetime.now(),  # You might want to extract actual timestamp from the chunk
                    'stream_name': stream_name
                }
                
        except Exception as e:
            logger.error(f"Failed to get media stream from {stream_name}: {str(e)}")
            raise

