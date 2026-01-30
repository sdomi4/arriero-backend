from alpaca import filterwheel
from time import sleep

from typing import TYPE_CHECKING

from observatory.state import StateManager, FilterwheelState

class FilterWheelConnectionError(RuntimeError):
    pass

if TYPE_CHECKING:
    from observatory.state import StateManager

def filterwheel_factory(
        address: str,
        id: str,
        device_number: int = 0,
        state: "StateManager" = None,
    ) -> filterwheel.FilterWheel:
    try:
        print("connecting to filter wheel", id, address)
        fw = filterwheel.FilterWheel(address, device_number)
        
        timeout = 0
        fw.Connected = True
        while fw.Connecting:
            timeout += 1
            if timeout > 10:
                print(f"Filter wheel {id} connection timed out")
                raise FilterWheelConnectionError(f"Filter wheel {id} connection timed out")
            sleep(1)
        state.add_device(FilterwheelState(
            id=id,
            connected=True,
            position=fw.Position,
            names=list(fw.Names) if hasattr(fw, 'Names') else None
        ))
        return fw
    except Exception as e:
        print(f"Error connecting to filter wheel {id}: {e}")
        raise FilterWheelConnectionError(f"Error connecting to filter wheel {id}: {e}")