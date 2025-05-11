from dataclasses import dataclass
from typing import List
from datetime import datetime
from models.detection_result import DetectionResult

@dataclass
class DetectionDBRecord:
    """Data model for storing detection results in DynamoDB
    
    Attributes:
        timestamp: Time when frame was processed
        camera_id: ID of camera that captured the frame
        client_id: ID of client that owns the camera
        zone: Zone/area where camera is located
        detections: List of DetectionResult objects found in frame
        frame_id: Unique identifier for this frame
    """
    timestamp: datetime
    camera_id: str
    client_id: str
    zone: str
    detections: List[DetectionResult]
    frame_id: str

