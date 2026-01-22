from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from observatory.state import StateManager

def observing_conditions_updater(oc, state: "StateManager" = None):
    if not oc.alpaca.Connected:
        raise ConnectionError("Observing conditions not connected")
    
    state.update_key(
        "conditions",
        {
            "sky-ambient": oc.alpaca.SkyTemperature,
            "ambient": oc.alpaca.Temperature,
            "rain": oc.alpaca.RainRate,
            "wind": oc.alpaca.WindSpeed,
            "daylight": oc.alpaca.SkyBrightness,
            "humidity": oc.alpaca.Humidity,
            "dew_point": oc.alpaca.DewPoint,
            "pressure": oc.alpaca.Pressure,
            "connected": oc.alpaca.Connected,
        },
    )


def safety_monitor_updater(sm, state: "StateManager" = None):
    if not sm.alpaca.Connected:
        raise ConnectionError("Safety monitor not connected")
    
    state.update_key(
        "safety",
        {"safe": sm.alpaca.IsSafe, "connected": sm.alpaca.Connected},
    )