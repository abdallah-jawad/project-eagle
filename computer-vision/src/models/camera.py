from dataclasses import dataclass
from typing import Dict, List, Tuple
from datetime import time

@dataclass
class NotificationSettings:
    """Data model for camera notification settings
    
    Attributes:
        labels_to_notify_on: List of object labels that should trigger notifications
        contact_email: Email address to send notifications to
        contact_phone: Phone number to send notifications to
        notify_start_time: Time of day to start sending notifications
        notify_end_time: Time of day to stop sending notifications
        enabled: Whether notifications are enabled
    """
    labels_to_notify_on: List[str]
    contact_email: str
    contact_phone: str
    notify_start_time: time
    notify_end_time: time
    enabled: bool

@dataclass
class Camera:
    """Data model for camera configuration and settings
    
    Attributes:
        camera_id: Unique identifier for the camera
        client_id: ID of the client this camera belongs to
        enabled: Whether the camera is currently enabled
        zone: Zone/area identifier where camera is located
        notification_settings: Notification configuration settings
        fps: Frames per second setting for the camera
        resolution: Tuple of (width, height) for camera resolution
        capture: OpenCV VideoCapture object for reading video frames
        kvs_stream_id: ID of the associated Kinesis Video Stream
        labels: List of object labels this camera should detect
    """
    camera_id: str
    client_id: str
    enabled: bool
    zone: str
    notification_settings: NotificationSettings
    fps: int
    resolution: Tuple[int, int]  # (width, height)
    capture: cv2.VideoCapture
    kvs_stream_id: str
    labels: List[str]

