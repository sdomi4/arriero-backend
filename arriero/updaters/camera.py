from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from observatory.state import StateManager

def camera_updater(camera, name, state: "StateManager" = None):
    state.update_key("cameras", {
        name: {
            "connected": camera.alpaca.Connected,
            "status": camera.alpaca.CameraState,
            "cooler": {
                "status": camera.alpaca.CoolerOn,
                "power": camera.alpaca.CoolerPower,
                #"setpoint": camera.alpaca.SetCCDTemperature,
                "temperature": camera.alpaca.CCDTemperature
            }
        }
    })