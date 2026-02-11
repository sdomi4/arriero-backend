from observatory.devices.base import ObservatoryDevice
from arriero.arriero import Arriero
from alpaca import telescope
from observatory.errors import TelescopeError
from time import sleep
from typing import TYPE_CHECKING, Callable
import asyncio
from observatory.safety import require_conditions
from observatory.safety_conditions import *

if TYPE_CHECKING:
    from observatory.observatory import Observatory

class ArrieroTelescope(ObservatoryDevice[telescope.Telescope]):
    def __init__(self, observatory: "Observatory", factory: Callable[[], telescope.Telescope], updater: Callable[[], None], id: str, name: str = None, poll_time: float = 1):
        arriero = Arriero(
            factory,
            updater,
            poll_time=poll_time,
            name=name or id,
        )
        super().__init__(observatory, arriero, id=id, name=name)

    @require_conditions(dome_is_open)
    def park(self, override: bool = False):
        state_device = self.observatory.state.get_device(self.id)
        try:
            if self.alpaca.AtPark:
                return
            
            self.observatory.state.add_action(f"Parking {self.arriero.name}")
            self.alpaca.Park()
            
            for _ in range(60):
                parked = self.alpaca.AtPark
                state_device.parked = parked
                if parked:
                    self.observatory.state.remove_action(f"Parking {self.arriero.name}")
                    return
                sleep(1)
            
            self.observatory.state.remove_action(f"Parking {self.arriero.name}")
            raise TelescopeError(code="telescope_park_timeout", message=f"Parking telescope {self.arriero.name} timed out")
        except Exception as e:
            self.observatory.state.remove_action(f"Parking {self.arriero.name}")
            raise TelescopeError(code="telescope_park_failed", message=f"Error parking telescope {self.arriero.name}: {e}")

    @require_conditions(weather_is_safe, dome_is_open)
    def unpark(self, override: bool = False):
        state_device = self.observatory.state.get_device(self.id)
        try:
            if not self.alpaca.AtPark:
                return
            
            self.observatory.state.add_action(f"Unparking {self.arriero.name}")
            self.alpaca.Unpark()
            
            for _ in range(60):
                parked = self.alpaca.AtPark
                state_device.parked = parked
                if not parked:
                    self.observatory.state.remove_action(f"Unparking {self.arriero.name}")
                    return
                sleep(1)
            
            self.observatory.state.remove_action(f"Unparking {self.arriero.name}")
            raise TelescopeError(code="telescope_unpark_timeout", message=f"Unparking telescope {self.arriero.name} timed out")
        except Exception as e:
            self.observatory.state.remove_action(f"Unparking {self.arriero.name}")
            raise TelescopeError(code="telescope_unpark_failed", message=f"Error unparking telescope {self.arriero.name}: {e}")

    @require_conditions(weather_is_safe, dome_is_open)
    def slew(self, ra: float, dec: float, override: bool = False):
        state_device = self.observatory.state.get_device(self.id)
        try:
            if self.alpaca.AtPark:
                self.alpaca.Unpark()
            
            self.alpaca.TargetRightAscension = ra
            self.alpaca.TargetDeclination = dec
            self.alpaca.Tracking = True
            self.alpaca.SlewToTargetAsync()
            
            self.observatory.state.add_action(f"Slewing {self.arriero.name} to target")
            
            for _ in range(60):
                slewing = self.alpaca.Slewing
                state_device.slewing = slewing
                if not slewing:
                    self.observatory.state.remove_action(f"Slewing {self.arriero.name} to target")
                    return
                sleep(1)
            
            self.observatory.state.remove_action(f"Slewing {self.arriero.name} to target")
            raise TelescopeError(code="telescope_slew_timeout", message=f"Slewing telescope {self.arriero.name} timed out")
        except Exception as e:
            self.observatory.state.remove_action(f"Slewing {self.arriero.name} to target")
            raise TelescopeError(code="telescope_slew_failed", message=f"Error slewing telescope {self.arriero.name}: {e}")

    async def trigger_park(self, override: bool = False):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: self.park(override=override))
    
    async def trigger_unpark(self, override: bool = False):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: self.unpark(override=override))

    async def trigger_slew(self, ra: float, dec: float, override: bool = False):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: self.slew(ra, dec, override=override))
