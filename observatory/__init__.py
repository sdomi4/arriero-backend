from fastapi import Request
from observatory.observatory import Observatory
from observatory.safety import set_current_observatory


def get_observatory(request: Request) -> Observatory:
    """Dependency to get the observatory instance from app state."""
    observatory = request.app.state.observatory
    set_current_observatory(observatory)
    return observatory
