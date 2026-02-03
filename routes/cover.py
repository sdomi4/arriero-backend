from fastapi import APIRouter, HTTPException, Depends
from observatory.safety import safety_override
from observatory.observatory import Observatory
from routes import get_observatory

router = APIRouter(prefix="/cover", tags=["cover"])

@router.post("/{cover_id}/startup")
async def cover_startup(
    cover_id: str,
    observatory: Observatory = Depends(get_observatory)
):
    try:
        observatory.covers[cover_id].connect()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to cover {cover_id}: {e}")
    
@router.post("/{cover_id}/shutdown")
async def cover_shutdown(
    cover_id: str,
    observatory: Observatory = Depends(get_observatory)
):
    try:
        observatory.covers[cover_id].disconnect()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error disconnecting from cover {cover_id}: {e}")
    
@router.post("/{cover_id}/open")
async def cover_open(
    cover_id: str,
    override: bool = Depends(safety_override),
    observatory: Observatory = Depends(get_observatory)
):
    try:
        await observatory.covers[cover_id].trigger_open(override=override)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error opening cover {cover_id}: {e}")
    
@router.post("/{cover_id}/close")
async def cover_close(
    cover_id: str,
    override: bool = Depends(safety_override),
    observatory: Observatory = Depends(get_observatory)
):
    try:
        await observatory.covers[cover_id].trigger_close(override=override)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error closing cover {cover_id}: {e}")
