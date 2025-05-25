from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict
from ..models.camera import Camera, CameraCreate, CameraUpdate
import json
from pathlib import Path

router = APIRouter()

def load_camera_configs():
    config_path = Path("/Users/khalidll/Desktop/project-eagle/config/camera-config.json")
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading camera configs: {e}")
        return {"cameras": []}

@router.get("/cameras", response_model=List[Camera])
async def list_cameras(client_id: str = Query(..., description="Client ID to filter cameras")) -> List[Camera]:
    """
    List all available cameras for a specific client
    """
    configs = load_camera_configs()
    client_cameras = [
        Camera(
            id=cam['camera_id'],
            name=f"Camera {cam['camera_id']}",
            description=f"Camera in {cam['zone']} zone",
            rtsp_url=cam['rtsp_url'],
            kvs_stream_id=cam.get('kvs_stream_id'),
            status="active" if cam['enabled'] else "inactive"
        )
        for cam in configs['cameras']
        if cam['client_id'] == client_id
    ]
    return client_cameras

@router.get("/cameras/{camera_id}", response_model=Camera)
async def get_camera(camera_id: str) -> Camera:
    """
    Get specific camera details
    """
    # TODO: Implement camera retrieval logic
    raise HTTPException(status_code=404, detail="Camera not found")

@router.post("/cameras", response_model=Camera)
async def create_camera(camera: CameraCreate) -> Camera:
    """
    Add a new camera
    """
    # TODO: Implement camera creation logic
    return Camera(id="dummy_id", **camera.dict())

@router.put("/cameras/{camera_id}", response_model=Camera)
async def update_camera(camera_id: str, camera: CameraUpdate) -> Camera:
    """
    Update camera configuration
    """
    # TODO: Implement camera update logic
    raise HTTPException(status_code=404, detail="Camera not found")

@router.delete("/cameras/{camera_id}")
async def delete_camera(camera_id: str) -> Dict[str, str]:
    """
    Remove a camera
    """
    # TODO: Implement camera deletion logic
    return {"status": "success"} 