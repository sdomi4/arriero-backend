from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from observatory.state import StateManager

def cover_updater(cover, name, state: "StateManager" = None):
    if not cover.alpaca.Connected:
        raise ConnectionError(f"Cover {name} not connected")
    
    status = cover.alpaca.CoverState
    if status != state._state["covers"][name]["status"]:
        state.update_key("covers", {name: {"status": status}})
        if status == 4 or status == 5:  # 4 = Unknown, 5 = Error
            print("Cover reported an error")