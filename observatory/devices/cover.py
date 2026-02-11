from observatory.devices.base import ObservatoryDevice
from arriero.arriero import Arriero
from alpaca import covercalibrator
from observatory.errors import CoverError
from time import sleep
from typing import TYPE_CHECKING, Callable
import asyncio
from observatory.safety import require_conditions
from observatory.safety_conditions import *

if TYPE_CHECKING:
    from observatory.observatory import Observatory

class ArrieroCover(ObservatoryDevice[covercalibrator.CoverCalibrator]):
    def __init__(self, observatory: "Observatory", factory: Callable[[], covercalibrator.CoverCalibrator], updater: Callable[[], None], id: str, name: str = None, poll_time: float = 1):
        arriero = Arriero(
            factory,
            updater,
            poll_time=poll_time,
            name=name or id,
        )
        super().__init__(observatory, arriero, id=id, name=name)

    @require_conditions(weather_is_safe, dome_is_open, is_dark)
    def open(self, override: bool = False):
        state_device = self.observatory.state.get_device(self.id)
        try:
            self.observatory.state.add_action(f"Opening {self.arriero.name}")
            self.alpaca.OpenCover()
            
            status = self.alpaca.CoverState
            state_device.cover_state = status
            
            if status == 3:  # 3 = Open
                self.observatory.state.remove_action(f"Opening {self.arriero.name}")
                return
            elif status == 2:  # 2 = Moving
                for _ in range(60):
                    status = self.alpaca.CoverState
                    state_device.cover_state = status
                    if status == 3:
                        self.observatory.state.remove_action(f"Opening {self.arriero.name}")
                        return
                    sleep(1)
                self.observatory.state.remove_action(f"Opening {self.arriero.name}")
                raise CoverError(code="cover_open_timeout", message=f"Opening cover {self.arriero.name} timed out")
            else:
                self.observatory.state.remove_action(f"Opening {self.arriero.name}")
                raise CoverError(code="cover_open_failed", message=f"Error opening cover {self.arriero.name}: status {status}")
        except Exception as e:
            self.observatory.state.remove_action(f"Opening {self.arriero.name}")
            raise CoverError(code="cover_open_failed", message=f"Error opening cover {self.arriero.name}: {e}")

    @require_conditions(dome_is_open)
    def close(self, override: bool = False):
        state_device = self.observatory.state.get_device(self.id)
        try:
            self.observatory.state.add_action(f"Closing {self.arriero.name}")
            self.alpaca.CloseCover()
            
            status = self.alpaca.CoverState
            state_device.cover_state = status
            
            if status == 1:  # 1 = Closed
                self.observatory.state.remove_action(f"Closing {self.arriero.name}")
                return
            elif status == 2:  # 2 = Moving
                for _ in range(60):
                    status = self.alpaca.CoverState
                    state_device.cover_state = status
                    if status == 1:
                        self.observatory.state.remove_action(f"Closing {self.arriero.name}")
                        return
                    sleep(1)
                self.observatory.state.remove_action(f"Closing {self.arriero.name}")
                raise CoverError(code="cover_close_timeout", message=f"Closing cover {self.arriero.name} timed out")
            else:
                self.observatory.state.remove_action(f"Closing {self.arriero.name}")
                raise CoverError(code="cover_close_failed", message=f"Error closing cover {self.arriero.name}: status {status}")
        except Exception as e:
            self.observatory.state.remove_action(f"Closing {self.arriero.name}")
            raise CoverError(code="cover_close_failed", message=f"Error closing cover {self.arriero.name}: {e}")

    async def trigger_open(self, override: bool = False):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: self.open(override=override))
    
    async def trigger_close(self, override: bool = False):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: self.close(override=override))
