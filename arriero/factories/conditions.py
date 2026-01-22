from time import sleep
from alpaca import safetymonitor, observingconditions

from typing import TYPE_CHECKING

class ObservingConditionsConnectionError(RuntimeError):
    pass

class SafetyMonitorConnectionError(RuntimeError):
    pass

if TYPE_CHECKING:
    from observatory.state import StateManager

def observing_conditions_factory(
        address: str,
        name: str,
        device_number: int = 0,
        state: "StateManager" | None = None,
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
                state.update_key("conditions", {"connected": False})
                raise ObservingConditionsConnectionError("Observing conditions connection timed out")
            sleep(1)
        state.update_key("conditions", {
            "connected": True,
            "sky-ambient": oc.SkyTemperature,
            "ambient": oc.Temperature,
            "rain": oc.RainRate,
            "wind": oc.WindSpeed,
            "daylight": oc.SkyBrightness,
            "humidity": oc.Humidity,
            "dew_point": oc.DewPoint,
            "pressure": oc.Pressure,
        })
        return oc
    except Exception as e:
        print(f"Error connecting to observing conditions: {e}")
        state.update_key("conditions", {"connected": False})
        raise ObservingConditionsConnectionError(f"Error connecting to observing conditions: {e}")
    
def safety_monitor_factory(
        address: str,
        name: str,
        device_number: int = 0,
        state: "StateManager" | None = None,
    ) -> safetymonitor.SafetyMonitor:
    try:
        print("connecting to", name, "at", address)
        sm = safetymonitor.SafetyMonitor(address, device_number)
        
        timeout = 0
        sm.Connect()
        while True:
            try:
                if not sm.Connecting:
                    break
            except Exception as e:
                print(f"Error connecting to safety monitor: {e}")
                state.update_key("safety", {"connected": False, "status": "unknown"})
                raise SafetyMonitorConnectionError(f"Error connecting to safety monitor: {e}")
            timeout += 1
            if timeout > 10:
                print("Safety monitor connection timed out")
                state.update_key("safety", {"connected": False, "status": "unknown"})
                raise SafetyMonitorConnectionError("Safety monitor connection timed out")
            sleep(1)
        state.update_key("safety", {"connected": True, "safe": sm.IsSafe})
        return sm
    except Exception as e:
        print(f"Error connecting to safety monitor: {e}")
        state.update_key("safety", {"connected": False, "status": "unknown"})
        raise SafetyMonitorConnectionError(f"Error connecting to safety monitor: {e}")