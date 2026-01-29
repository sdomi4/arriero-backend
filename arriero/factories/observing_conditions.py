from alpaca import observingconditions
from time import sleep

from observatory.state import StateManager, ObservingConditionsState

class ObservingConditionsConnectionError(RuntimeError):
    pass


def observing_conditions_factory(
        address: str,
        name: str,
        device_number: int = 0,
        state: "StateManager" = None,
    ) -> observingconditions.ObservingConditions:
    try:
        print("connecting to observing conditions", name, address)
        oc = observingconditions.ObservingConditions(address, device_number)
        timeout = 0
        oc.Connect()
        while oc.Connecting:
                timeout += 1
                if timeout > 10:
                    print("Observing conditions connection timed out")
                    raise ObservingConditionsConnectionError("Observing conditions connection timed out")
                sleep(1)
        state.add_device(ObservingConditionsState(id=name, connected=True))
        return oc
    except Exception as e:
        print(f"Error connecting to observing conditions: {e}")
        raise ObservingConditionsConnectionError(f"Error connecting to observing conditions: {e}")
