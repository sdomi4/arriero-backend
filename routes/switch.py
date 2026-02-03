from fastapi import APIRouter, HTTPException, Depends
from observatory.observatory import Observatory
from routes import get_observatory

router = APIRouter(prefix="/switch", tags=["switch"])

@router.post("/{switch_id}/startup")
async def switch_startup(
    switch_id: str,
    observatory: Observatory = Depends(get_observatory)
):
    try:
        observatory.switches[switch_id].connect()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to switch {switch_id}: {e}")
    
@router.post("/{switch_id}/shutdown")
async def switch_shutdown(
    switch_id: str,
    observatory: Observatory = Depends(get_observatory)
):
    try:
        observatory.switches[switch_id].disconnect()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error disconnecting from switch {switch_id}: {e}")

@router.post("/{switch_id}/{switch_number}/{setting}")
async def set_switch(
    switch_id: str,
    switch_number: int,
    setting: bool,
    observatory: Observatory = Depends(get_observatory)
):
    try:
        observatory.switches[switch_id].set_switch(switch_number, setting)
        return {"message": f"Switch {switch_number} on {switch_id} set to {setting}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting switch {switch_number} on {switch_id}: {e}")
