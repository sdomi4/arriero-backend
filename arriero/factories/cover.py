
from time import sleep
from alpaca import covercalibrator

from typing import TYPE_CHECKING

class CoverConnectionError(RuntimeError):
    pass

if TYPE_CHECKING:
    from observatory.state import StateManager

def cover_factory(
        address: str,
        name: str,
        device_number: int = 0,
        state: "StateManager" = None,
    ) -> covercalibrator.CoverCalibrator:
    try:
        print("connecting to cover", name, address)
        cc = covercalibrator.CoverCalibrator(address, device_number)
        
        timeout = 0
        cc.Connected = True
        while cc.Connecting:
            timeout += 1
            if timeout > 10:
                print(f"Cover {name} connection timed out")
                state.update_key("covers", {name: {"connected": False, "status": "unknown"}})
                raise CoverConnectionError(f"Cover {name} connection timed out")
            sleep(1)
        state.update_key("covers", {name: {"connected": True, "status": cc.CoverState}})
        return cc
    except Exception as e:
        print(f"Error connecting to cover {name}: {e}")
        state.update_key("covers", {name: {"connected": False, "status": "unknown"}})
        raise CoverConnectionError(f"Error connecting to cover {name}: {e}")