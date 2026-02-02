from fastapi import Request
from observatory.observatory import Observatory


def get_observatory(request: Request) -> Observatory:
    """Dependency to get the observatory instance from app state."""
    return request.app.state.observatory
