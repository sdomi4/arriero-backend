from alpaca import dome
from time import sleep

from observatory.state import StateManager, DomeState

class DomeConnectionError(RuntimeError):
    pass


def dome_factory(
        address: str,
        name: str,
        device_number: int = 0,
        state: "StateManager" = None,
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
                    raise DomeConnectionError("Dome connection timed out")
                sleep(1)
        state.add_device(DomeState(id=name, connected=True, status=d.ShutterStatus))
        return d
    except Exception as e:
        print(f"Error connecting to dome: {e}")
        raise DomeConnectionError(f"Error connecting to dome: {e}")