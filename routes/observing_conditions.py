from fastapi import APIRouter, HTTPException, Depends
from observatory.observatory import Observatory
from routes import get_observatory

router = APIRouter(prefix="/conditions", tags=["conditions"])

@router.post("/{conditions_id}/startup")
async def conditions_startup(
    conditions_id: str,
    observatory: Observatory = Depends(get_observatory)
):
    try:
        observatory.observing_conditions[conditions_id].connect()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to observing conditions {conditions_id}: {e}")
    
@router.post("/{conditions_id}/shutdown")
async def conditions_shutdown(
    conditions_id: str,
    observatory: Observatory = Depends(get_observatory)
):
    try:
        observatory.observing_conditions[conditions_id].disconnect()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error disconnecting from observing conditions {conditions_id}: {e}")
