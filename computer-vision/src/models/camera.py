from dataclasses import dataclass
from typing import Dict, List, Tuple
from datetime import time
import cv2

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

class Camera:
    def __init__(self, fixture_id: str, camera_id: str, camera_name: str, stream_url: str, resolution: str, fps: int, status: str):
        self.fixture_id = fixture_id
        self.camera_id = camera_id
        self.camera_name = camera_name
        self.stream_url = stream_url
        self.resolution = resolution
        self.fps = fps
        self.status = status

    def __repr__(self):
        return f"Camera(fixture_id={self.fixture_id}, camera_id={self.camera_id}, camera_name={self.camera_name}, stream_url={self.stream_url}, resolution={self.resolution}, fps={self.fps}, status={self.status})"

