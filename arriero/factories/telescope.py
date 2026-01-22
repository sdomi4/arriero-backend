from time import sleep
from alpaca import telescope

from typing import TYPE_CHECKING

class TelescopeConnectionError(RuntimeError):
    pass

if TYPE_CHECKING:
    from observatory.state import StateManager

def telescope_factory(
        address: str,
        name: str,
        device_number: int = 0,
        state: "StateManager" | None = None,
    ) -> telescope.Telescope:
    try:
        print("connecting to telescope", name, address)
        t = telescope.Telescope(address, device_number)
        
        timeout = 0
        t.Connect()
        while t.Connecting:
            timeout += 1
            if timeout > 10:
                print("Telescope connection timed out")
                state.update_key("mount", {"connected": False, "status": "unknown"})
                raise TelescopeConnectionError("Telescope connection timed out")
            sleep(1)
        state.update_key("mount", {"connected": True, "parked": t.AtPark, "homed": t.AtHome, "tracking": t.Tracking, "slewing": t.Slewing})
        return t
    except Exception as e:
        print(f"Error connecting to telescope: {e}")
        state.update_key("mount", {"connected": False, "status": "unknown"})
        raise TelescopeConnectionError(f"Error connecting to telescope: {e}")