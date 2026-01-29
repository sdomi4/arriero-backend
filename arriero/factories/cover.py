from alpaca import covercalibrator
from time import sleep

from observatory.state import StateManager, CoverState

class CoverConnectionError(RuntimeError):
    pass


def cover_factory(
        address: str,
        name: str,
        device_number: int = 0,
        state: "StateManager" = None,
    ) -> covercalibrator.CoverCalibrator:
    try:
        print("connecting to cover calibrator", name, address)
        c = covercalibrator.CoverCalibrator(address, device_number)
        timeout = 0
        c.Connect()
        while c.Connecting:
                timeout += 1
                if timeout > 10:
                    print("Cover calibrator connection timed out")
                    raise CoverConnectionError("Cover calibrator connection timed out")
                sleep(1)
        state.add_device(CoverState(id=name, connected=True))
        return c
    except Exception as e:
        print(f"Error connecting to cover calibrator: {e}")
        raise CoverConnectionError(f"Error connecting to cover calibrator: {e}")