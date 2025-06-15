from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict
from ..models.camera import Camera, CameraCreate, CameraUpdate
from ..dependencies.appconfig import get_camera_configs

router = APIRouter()

@router.get("/cameras", response_model=List[Camera])
async def list_cameras(client_id: str = Query(..., description="Client ID to filter cameras")) -> List[Camera]:
    """
    List all available cameras for a specific client
    """
    try:
        configs = get_camera_configs()
        client_cameras = [
            Camera.from_config(cam)
            for cam in configs['cameras']
            if cam['client_id'] == client_id
        ]
        return client_cameras
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching camera configurations: {str(e)}")

@router.get("/cameras/{camera_id}", response_model=Camera)
async def get_camera(camera_id: str) -> Camera:
    """
    Get specific camera details
    """
    try:
        configs = get_camera_configs()
        for cam in configs['cameras']:
            if cam['camera_id'] == camera_id:
                return Camera.from_config(cam)
        raise HTTPException(status_code=404, detail="Camera not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching camera configuration: {str(e)}")

@router.post("/cameras", response_model=Camera)
async def create_camera(camera: CameraCreate) -> Camera:
    """
    Add a new camera
    """
    # TODO: Implement camera creation logic
    return Camera.from_config(camera.dict())

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