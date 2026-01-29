from observatory.state import StateManager, DomeState
from observatory.devices.dome import ArrieroDome

def dome_updater(dome: "ArrieroDome", name, state: "StateManager" = None):
    if not dome.alpaca.Connected:
        raise ConnectionError("Dome not connected")
    
    try:
        device = state.get_device(name)
        device.connected = dome.alpaca.Connected
        device.shutter_status = dome.alpaca.ShutterStatus

        if device.shutter_status == 4:
            print("Dome reported an error")

        state.update_device(device)
    except Exception as e:
        print(f"Error updating dome state: {e}")