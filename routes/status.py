from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
import asyncio
from observatory.observatory import Observatory 
from routes import get_observatory_ws

router = APIRouter()

@router.websocket("/ws/state")
async def state_websocket(websocket: WebSocket, observatory: Observatory = Depends(get_observatory_ws)):
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(observatory.state.snapshot_dict())
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.close(code=1011, reason=str(e))