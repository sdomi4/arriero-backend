from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from observatory.state import StateManager

def switch_updater(switch, name, state: "StateManager" = None):
    if not switch.alpaca.Connected:
        raise ConnectionError(f"Switch {name} not connected")
    
    switch_dict = {
        "status": "connected",
        "switch": {}
    }
    for i in range(0, switch.alpaca.MaxSwitch):
        switch_dict["switch"][i] = switch.alpaca.GetSwitch(i)

    state.update_key("switches", {name: switch_dict})