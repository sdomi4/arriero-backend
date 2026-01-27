from time import sleep
from alpaca import camera
from typing import TYPE_CHECKING

class CameraConnectionError(RuntimeError):
    pass

if TYPE_CHECKING:
    from observatory.state import StateManager

def camera_factory(
        address: str,
        name: str,
        device_number: int = 0,
        state: "StateManager" = None,
    ) -> camera.Camera:
    try:
        print("connecting to camera", name, address)
        cam = camera.Camera(address, device_number)
        
        timeout = 0
        cam.Connected = True
        while cam.Connecting:
            timeout += 1
            if timeout > 10:
                print(f"Camera {name} connection timed out")
                state.update_key("cameras", {name: {"connected": False}})
                raise CameraConnectionError(f"Camera {name} connection timed out")
            sleep(1)
        state.update_key("cameras", {name: {"connected": True}})
        return cam
    except Exception as e:
        print(f"Error connecting to camera {name}: {e}")
        state.update_key("cameras", {name: {"connected": False}})
        raise CameraConnectionError(f"Error connecting to camera {name}: {e}")