from alpaca import dome
from time import sleep

from typing import TYPE_CHECKING

class DomeConnectionError(RuntimeError):
    pass

if TYPE_CHECKING:
    from observatory.state import StateManager

def dome_factory(
        address: str,
        name: str,
        device_number: int = 0,
        state: "StateManager" | None = None,
    ) -> dome.Dome:
    try:
        print("connecting to dome", name, address)
        d = dome.Dome(address, device_number)
        timeout = 0
        d.Connect()
        while d.Connecting:
                timeout += 1
                if timeout > 10:
                    print("Dome connection timed out")
                    state.update_key("dome", {name: {"connected": False, "status": "unknown"}})
                    raise DomeConnectionError("Dome connection timed out")
                sleep(1)
        state.update_key("dome", {name: {"connected": True, "status": d.ShutterStatus}})
        return d
    except Exception as e:
        print(f"Error connecting to dome: {e}")
        state.update_key("dome", {name: {"connected": False, "status": "unknown"}})
        raise DomeConnectionError(f"Error connecting to dome: {e}")