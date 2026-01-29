from alpaca import safetymonitor
from time import sleep

from observatory.state import StateManager, SafetyMonitorState

class SafetyMonitorConnectionError(RuntimeError):
    pass


def safety_monitor_factory(
        address: str,
        name: str,
        device_number: int = 0,
        state: "StateManager" = None,
    ) -> safetymonitor.SafetyMonitor:
    try:
        print("connecting to safety monitor", name, address)
        sm = safetymonitor.SafetyMonitor(address, device_number)
        timeout = 0
        sm.Connect()
        while sm.Connecting:
                timeout += 1
                if timeout > 10:
                    print("Safety monitor connection timed out")
                    raise SafetyMonitorConnectionError("Safety monitor connection timed out")
                sleep(1)
        state.add_device(SafetyMonitorState(id=name, connected=True))
        return sm
    except Exception as e:
        print(f"Error connecting to safety monitor: {e}")
        raise SafetyMonitorConnectionError(f"Error connecting to safety monitor: {e}")
