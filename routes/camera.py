from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from observatory.observatory import Observatory
from routes import get_observatory

router = APIRouter(prefix="/camera", tags=["camera"])

class CameraExposureRequest(BaseModel):
    exposure: float
    base_path: str
    binX: int = 1
    binY: int = 1
    additional_headers: dict = {}

@router.post("/{camera_id}/startup")
async def camera_startup(
    camera_id: str,
    observatory: Observatory = Depends(get_observatory)
):
    try:
        observatory.cameras[camera_id].connect()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to camera {camera_id}: {e}")
    
@router.post("/{camera_id}/shutdown")
async def camera_shutdown(
    camera_id: str,
    observatory: Observatory = Depends(get_observatory)
):
    try:
        observatory.cameras[camera_id].disconnect()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error disconnecting from camera {camera_id}: {e}")

@router.post("/{camera_id}/set_temperature/{target_temp}")
async def set_camera_temperature(
    camera_id: str,
    target_temp: float,
    observatory: Observatory = Depends(get_observatory)
):
    try:
        observatory.cameras[camera_id].cool(target_temp)
        return {"message": f"Camera {camera_id} cooling to {target_temp}C"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting temperature for camera {camera_id}: {e}")
    
@router.post("/{camera_id}/capture")
async def capture_image(
    camera_id: str,
    body: CameraExposureRequest,
    observatory: Observatory = Depends(get_observatory)
):
    try:
        filename = await observatory.cameras[camera_id].trigger_expose_and_save(
            body.exposure,
            body.base_path,
            body.binX,
            body.binY,
            body.additional_headers
        )
        return {"message": f"Image captured and saved to {filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error capturing image for camera {camera_id}: {e}")
