from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class CameraStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"

class CameraBase(BaseModel):
    name: str = Field(..., description="Name of the camera")
    description: Optional[str] = Field(None, description="Description of the camera")
    rtsp_url: str = Field(..., description="RTSP URL of the camera stream")
    kvs_stream_id: Optional[str] = Field(None, description="KVS stream ID if using KVS")
    status: CameraStatus = Field(default=CameraStatus.INACTIVE, description="Current status of the camera")

class CameraCreate(CameraBase):
    pass

class CameraUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    rtsp_url: Optional[str] = None
    kvs_stream_id: Optional[str] = None
    status: Optional[CameraStatus] = None

class Camera(CameraBase):
    id: str = Field(..., description="Unique identifier for the camera")
    
    class Config:
        from_attributes = True 