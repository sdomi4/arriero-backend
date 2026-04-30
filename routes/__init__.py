from collections.abc import AsyncGenerator

from fastapi import Request, WebSocket
from observatory.observatory import Observatory
from observatory.safety import reset_current_observatory, set_current_observatory


async def get_observatory(request: Request) -> AsyncGenerator[Observatory, None]:
    """Dependency to get the observatory instance from app state."""
    observatory = request.app.state.observatory
    token = set_current_observatory(observatory)
    try:
        yield observatory
    finally:
        reset_current_observatory(token)

async def get_observatory_ws(websocket: WebSocket) -> AsyncGenerator[Observatory, None]:
    observatory = websocket.app.state.observatory
    token = set_current_observatory(observatory)
    try:
        yield observatory
    finally:
        reset_current_observatory(token)