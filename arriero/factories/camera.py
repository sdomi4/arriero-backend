from time import sleep
from alpaca import camera
from typing import TYPE_CHECKING

from observatory.state import StateManager, CameraState

class CameraConnectionError(RuntimeError):
    pass

if TYPE_CHECKING:
    from observatory.state import StateManager

def camera_factory(
        address: str,
        id: str,
        device_number: int = 0,
        state: "StateManager" = None,
    ) -> camera.Camera:
    try:
        print("connecting to camera", id, address)
        cam = camera.Camera(address, device_number)
        
        timeout = 0
        cam.Connected = True
        while cam.Connecting:
            timeout += 1
            if timeout > 10:
                print(f"Camera {id} connection timed out")
                raise CameraConnectionError(f"Camera {id} connection timed out")
            sleep(1)
        state.add_device(CameraState(id=id, connected=True))
        return cam
    except Exception as e:
        print(f"Error connecting to camera {id}: {e}")
        raise CameraConnectionError(f"Error connecting to camera {id}: {e}")