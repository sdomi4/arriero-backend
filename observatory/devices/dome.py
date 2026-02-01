from observatory.devices.base import ObservatoryDevice
from arriero.arriero import Arriero
from alpaca import dome
from observatory.errors import DomeError
from time import sleep
from typing import TYPE_CHECKING
import asyncio

if TYPE_CHECKING:
    from observatory.observatory import Observatory

class ArrieroDome(ObservatoryDevice[dome.Dome]):
    def __init__(self, observatory: "Observatory", factory, updater, id: str, name: str = None, poll_time=1):
        arriero = Arriero(
            factory,
            updater,
            poll_time=poll_time,
            name=name or id,
        )
        super().__init__(observatory, arriero, id=id, name=name)

    def open(self):
        state_device = self.observatory.state.get_device(self.id)
        state_device.shutter_status = self.alpaca.ShutterStatus
        if state_device.shutter_status == 0:
            return  # Already open
        self.observatory.state.add_action("dome", f"Opening {self.arriero.name} dome")

        try:
            self.alpaca.OpenShutter()
        except Exception as e:
            self.observatory.state.remove_action("dome")
            raise DomeError(f"Error opening dome {self.arriero.name}: {e}")
        
        while True:
            try:
                status = self.alpaca.ShutterStatus
                state_device.shutter_status = status
                if status == 0:
                    self.observatory.state.remove_action("dome")           
                    break
                sleep(1)
            except Exception as e:
                self.observatory.state.remove_action("dome")
                raise DomeError(f"Error monitoring dome {self.arriero.name} while opening: {e}")
            
    def close(self):
        state_device = self.observatory.state.get_device(self.id)
        state_device.shutter_status = self.alpaca.ShutterStatus
        if state_device.shutter_status == 1:
            return  # Already closed
        self.observatory.state.add_action("dome", f"Closing {self.arriero.name} dome")

        try:
            self.alpaca.CloseShutter()
        except Exception as e:
            self.observatory.state.remove_action("dome")
            raise DomeError(f"Error closing dome {self.arriero.name}: {e}")
        
        while True:
            try:
                status = self.alpaca.ShutterStatus
                state_device.shutter_status = status
                if status == 1:
                    self.observatory.state.remove_action("dome")           
                    break
                sleep(1)
            except Exception as e:
                self.observatory.state.remove_action("dome")
                raise DomeError(f"Error monitoring dome {self.arriero.name} while closing: {e}")
            
    async def trigger_open(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.open)
    
    async def trigger_close(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.close)
