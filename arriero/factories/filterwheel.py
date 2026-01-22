from alpaca import filterwheel
from time import sleep

from typing import TYPE_CHECKING

class FilterWheelConnectionError(RuntimeError):
    pass

if TYPE_CHECKING:
    from observatory.state import StateManager

def filterwheel_factory(
        address: str,
        name: str,
        device_number: int = 0,
        state: "StateManager" | None = None,
    ) -> filterwheel.FilterWheel:
    try:
        print("connecting to filter wheel", name, address)
        fw = filterwheel.FilterWheel(address, device_number)
        
        timeout = 0
        fw.Connected = True
        while fw.Connecting:
            timeout += 1
            if timeout > 10:
                print(f"Filter wheel {name} connection timed out")
                state.update_key("filterwheels", {name: {"connected": False, "position": None}})
                raise FilterWheelConnectionError(f"Filter wheel {name} connection timed out")
            sleep(1)
        state.update_key("filterwheels", {name: {"connected": True, "position": fw.Position}})
        return fw
    except Exception as e:
        print(f"Error connecting to filter wheel {name}: {e}")
        state.update_key("filterwheels", {name: {"connected": False, "position": None}})
        raise FilterWheelConnectionError(f"Error connecting to filter wheel {name}: {e}")