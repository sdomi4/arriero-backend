from typing import TYPE_CHECKING
from observatory.state import StateManager, SwitchState, ToggleControl, RangeControl
from observatory.devices.switch import ArrieroSwitch

if TYPE_CHECKING:
    from observatory.state import StateManager

def switch_updater(switch_device: "ArrieroSwitch", id, state: "StateManager" = None):
    if not switch_device.alpaca.Connected:
        raise ConnectionError("Switch not connected")
    
    try:
        device = state.get_device(id)
        device.connected = switch_device.alpaca.Connected
        
        # Update each control
        for control_name, control in device.controls.items():
            if isinstance(control, ToggleControl):
                control.value = switch_device.alpaca.GetSwitch(control.id)
            elif isinstance(control, RangeControl):
                control.value = switch_device.alpaca.GetSwitchValue(control.id)
    except Exception as e:
        print(f"Error updating switch state: {e}")