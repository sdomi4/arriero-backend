from fastapi import APIRouter, HTTPException, Depends
from observatory.safety import safety_override
from observatory.observatory import Observatory
from routes import get_observatory

router = APIRouter(prefix="/dome", tags=["dome"])

@router.post("/{dome_id}/startup")
async def dome_startup(
    dome_id: str,
    observatory: Observatory = Depends(get_observatory)
):
    try:
        observatory.domes[dome_id].connect()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to dome {dome_id}: {e}")
    
@router.post("/{dome_id}/shutdown")
async def dome_shutdown(
    dome_id: str,
    observatory: Observatory = Depends(get_observatory)
):
    try:
        observatory.domes[dome_id].disconnect()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error disconnecting from dome {dome_id}: {e}")
    
@router.post("/{dome_id}/open")
async def dome_open(
    dome_id: str,
    override: bool = Depends(safety_override),
    observatory: Observatory = Depends(get_observatory)
):
    try:
        await observatory.domes[dome_id].trigger_open(override=override)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error opening dome {dome_id}: {e}")
    
@router.post("/{dome_id}/close")
async def dome_close(
    dome_id: str,
    override: bool = Depends(safety_override),
    observatory: Observatory = Depends(get_observatory)
):
    try:
        await observatory.domes[dome_id].trigger_close(override=override)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error closing dome {dome_id}: {e}")