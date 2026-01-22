from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from observatory.state import StateManager

def dome_updater(dome, name, state: "StateManager" = None):
    if not dome.alpaca.Connected:
        raise ConnectionError("Dome not connected")
    
    status = dome.alpaca.ShutterStatus
    if status != state._state["dome"]["status"]:
        state.update_key("dome", {name: {"status": status}})
        if status == 4: # Error
            print("Dome reported an error")