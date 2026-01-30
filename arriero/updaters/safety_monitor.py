from observatory.state import StateManager, SafetyMonitorState
from observatory.devices.safety_monitor import ArrieroSafetyMonitor

def safety_monitor_updater(safety_monitor: "ArrieroSafetyMonitor", id, state: "StateManager" = None):
    if not safety_monitor.alpaca.Connected:
        raise ConnectionError("Safety monitor not connected")
    
    try:
        device = state.get_device(id)
        device.connected = safety_monitor.alpaca.Connected
        device.safe = safety_monitor.alpaca.IsSafe
    except Exception as e:
        print(f"Error updating safety monitor state: {e}")
