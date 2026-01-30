from observatory.state import StateManager, FilterwheelState
from observatory.devices.filterwheel import ArrieroFilterWheel

def filterwheel_updater(filterwheel: "ArrieroFilterWheel", id, state: "StateManager" = None):
    if not filterwheel.alpaca.Connected:
        raise ConnectionError(f"Filter wheel {id} not connected")
    
    try:
        device = state.get_device(id)
        device.connected = filterwheel.alpaca.Connected
        device.position = filterwheel.alpaca.Position
        
        if hasattr(filterwheel.alpaca, 'Names') and device.names is None:
            device.names = list(filterwheel.alpaca.Names)
    except Exception as e:
        print(f"Error updating filterwheel state: {e}")