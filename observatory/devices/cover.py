from observatory.devices.base import ObservatoryDevice
from alpaquero.alpaquero import Alpaquero
from alpaca import covercalibrator
from observatory.errors import CoverError
from time import sleep
from typing import TYPE_CHECKING, Callable
from observatory.safety import require_conditions
from observatory.safety_conditions import *

from observatory.action_registry import ActionRegistry

if TYPE_CHECKING:
    from observatory.observatory import Observatory

class AlpaqueroCover(ObservatoryDevice[covercalibrator.CoverCalibrator]):
    def __init__(self, observatory: "Observatory", factory: Callable[[], covercalibrator.CoverCalibrator], updater: Callable[[], None], id: str, name: str = None, poll_time: float = 1):
        alpaquero = Alpaquero(
            factory,
            updater,
            poll_time=poll_time,
            name=name or id,
        )
        super().__init__(observatory, alpaquero, id=id, name=name)

    @ActionRegistry.register("open_cover", observatory_arg=False, action_type="device")
    @require_conditions(weather_is_safe, dome_is_open, is_dark)
    def open(self, override: bool = False):
        state_device = self.observatory.state.get_device(self.id)
        try:
            self.observatory.state.add_action(f"Opening {self.alpaquero.name}")
            self.alpaca.OpenCover()
            
            status = self.alpaca.CoverState
            state_device.cover_status = status
            
            if status == 3:  # 3 = Open
                self.observatory.state.remove_action(f"Opening {self.alpaquero.name}")
                return
            elif status == 2:  # 2 = Moving
                for _ in range(60):
                    status = self.alpaca.CoverState
                    state_device.cover_status = status
                    if status == 3:
                        self.observatory.state.remove_action(f"Opening {self.alpaquero.name}")
                        return
                    sleep(1)
                self.observatory.state.remove_action(f"Opening {self.alpaquero.name}")
                raise CoverError(code="cover_open_timeout", message=f"Opening cover {self.alpaquero.name} timed out")
            else:
                self.observatory.state.remove_action(f"Opening {self.alpaquero.name}")
                raise CoverError(code="cover_open_failed", message=f"Error opening cover {self.alpaquero.name}: status {status}")
        except Exception as e:
            self.observatory.state.remove_action(f"Opening {self.alpaquero.name}")
            raise CoverError(code="cover_open_failed", message=f"Error opening cover {self.alpaquero.name}: {e}")

    @ActionRegistry.register("close_cover", observatory_arg=False, action_type="device")
    @require_conditions(dome_is_open)
    def close(self, override: bool = False):
        state_device = self.observatory.state.get_device(self.id)
        try:
            self.observatory.state.add_action(f"Closing {self.alpaquero.name}")
            self.alpaca.CloseCover()
            
            status = self.alpaca.CoverState
            state_device.cover_status = status
            
            if status == 1:  # 1 = Closed
                self.observatory.state.remove_action(f"Closing {self.alpaquero.name}")
                return
            elif status == 2:  # 2 = Moving
                for _ in range(60):
                    status = self.alpaca.CoverState
                    state_device.cover_status = status
                    if status == 1:
                        self.observatory.state.remove_action(f"Closing {self.alpaquero.name}")
                        return
                    sleep(1)
                self.observatory.state.remove_action(f"Closing {self.alpaquero.name}")
                raise CoverError(code="cover_close_timeout", message=f"Closing cover {self.alpaquero.name} timed out")
            else:
                self.observatory.state.remove_action(f"Closing {self.alpaquero.name}")
                raise CoverError(code="cover_close_failed", message=f"Error closing cover {self.alpaquero.name}: status {status}")
        except Exception as e:
            self.observatory.state.remove_action(f"Closing {self.alpaquero.name}")
            raise CoverError(code="cover_close_failed", message=f"Error closing cover {self.alpaquero.name}: {e}")

    async def trigger_open(self, override: bool = False):
        self.dispatch_trigger(self.open, override=override)
    
    async def trigger_close(self, override: bool = False):
        self.dispatch_trigger(self.close, override=override)
    
    @ActionRegistry.register("enable_calibrator", observatory_arg=False, action_type="device")
    def enable_calibrator(self, brightness: int = 255):
        try:
            self.alpaca.CalibratorOn(brightness)
        except Exception as e:
            raise CoverError(code="calibrator_enable_failed", message=f"Error enabling calibrator on {self.alpaquero.name}: {e}")
        
    @ActionRegistry.register("disable_calibrator", observatory_arg=False, action_type="device")
    def disable_calibrator(self):
        try:
            self.alpaca.CalibratorOff()
        except Exception as e:
            raise CoverError(code="calibrator_disable_failed", message=f"Error disabling calibrator on {self.alpaquero.name}: {e}")