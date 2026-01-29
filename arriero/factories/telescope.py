from alpaca import telescope
from time import sleep

from observatory.state import StateManager, TelescopeState

class TelescopeConnectionError(RuntimeError):
    pass


def telescope_factory(
        address: str,
        name: str,
        device_number: int = 0,
        state: "StateManager" = None,
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
                    raise TelescopeConnectionError("Telescope connection timed out")
                sleep(1)
        state.add_device(TelescopeState(id=name, connected=True))
        return t
    except Exception as e:
        print(f"Error connecting to telescope: {e}")
        raise TelescopeConnectionError(f"Error connecting to telescope: {e}")