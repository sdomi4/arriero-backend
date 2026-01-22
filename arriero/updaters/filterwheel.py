from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from observatory.state import StateManager

def filterwheel_updater(filterwheel, name, state: "StateManager" = None):
    if not filterwheel.alpaca.Connected:
        raise ConnectionError(f"Filter wheel {name} not connected")
    
    position = filterwheel.alpaca.Position
    if position != state._state["filterwheels"][name]["position"]:
        state.update_key("filterwheels", {name: {"position": position, "connected": True}})