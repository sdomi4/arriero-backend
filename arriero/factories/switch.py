from time import sleep
from alpaca import switch

from typing import TYPE_CHECKING

class SwitchConnectionError(RuntimeError):
    pass

if TYPE_CHECKING:
    from observatory.state import StateManager

def switch_factory(
        address: str,
        name: str,
        device_number: int = 0,
        state: "StateManager" | None = None,
    ) -> switch.Switch:
    try:
        print("connecting to switch", name, address)
        sw = switch.Switch(address, device_number)

        timeout = 0
        sw.Connected = True
        while sw.Connecting:
            timeout += 1
            if timeout > 10:
                print(f"Switch {name} connection timed out")
                state.update_key("switches", {name: {"status": "disconnected"}})
                raise SwitchConnectionError(f"Switch {name} connection timed out")
            sleep(1)
        state.update_key("switches", {name: {"status": "connected"}})
        return sw
    
    except Exception as e:
        print(f"Error connecting to switch {name}: {e}")
        state.update_key("switches", {name: {"status": "disconnected"}})
        raise SwitchConnectionError(f"Error connecting to switch {name}: {e}")