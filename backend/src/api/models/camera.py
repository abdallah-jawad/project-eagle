from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict
from enum import Enum
from datetime import time

class CameraStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"

class Resolution(BaseModel):
    width: int = Field(..., description="Width of the camera resolution")
    height: int = Field(..., description="Height of the camera resolution")

class NotificationSettings(BaseModel):
    labels_to_notify_on: List[str] = Field(..., description="List of labels to trigger notifications")
    contact_email: EmailStr = Field(..., description="Email to send notifications to")
    contact_phone: str = Field(..., description="Phone number to send notifications to")
    notify_start_time: str = Field(..., description="Start time for notifications (HH:MM)")
    notify_end_time: str = Field(..., description="End time for notifications (HH:MM)")
    enabled: bool = Field(..., description="Whether notifications are enabled")

class CameraBase(BaseModel):
    camera_id: str = Field(..., description="Unique identifier for the camera")
    client_id: str = Field(..., description="ID of the client who owns this camera")
    enabled: bool = Field(..., description="Whether the camera is enabled")
    zone: str = Field(..., description="Zone where the camera is located")
    rtsp_url: str = Field(..., description="RTSP URL of the camera stream")
    notification_settings: NotificationSettings = Field(..., description="Notification settings for the camera")
    fps: int = Field(..., description="Frames per second of the camera stream")
    resolution: Resolution = Field(..., description="Resolution of the camera stream")
    kvs_stream_id: Optional[str] = Field(None, description="KVS stream ID if using KVS")
    labels: List[str] = Field(..., description="List of labels to detect")

class CameraCreate(CameraBase):
    pass

class CameraUpdate(BaseModel):
    enabled: Optional[bool] = None
    zone: Optional[str] = None
    rtsp_url: Optional[str] = None
    notification_settings: Optional[NotificationSettings] = None
    fps: Optional[int] = None
    resolution: Optional[Resolution] = None
    kvs_stream_id: Optional[str] = None
    labels: Optional[List[str]] = None

class Camera(CameraBase):
    status: CameraStatus = Field(
        default=CameraStatus.INACTIVE,
        description="Current status of the camera"
    )
    
    @classmethod
    def from_config(cls, config: Dict) -> 'Camera':
        """Create a Camera instance from AppConfig data"""
        return cls(
            camera_id=config['camera_id'],
            client_id=config['client_id'],
            enabled=config['enabled'],
            zone=config['zone'],
            rtsp_url=config['rtsp_url'],
            notification_settings=NotificationSettings(**config['notification_settings']),
            fps=config['fps'],
            resolution=Resolution(**config['resolution']),
            kvs_stream_id=config.get('kvs_stream_id'),
            labels=config['labels'],
            status=CameraStatus.ACTIVE if config['enabled'] else CameraStatus.INACTIVE
        )
    
    class Config:
        from_attributes = True 