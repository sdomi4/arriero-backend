from typing import TYPE_CHECKING
from observatory.state import StateManager, TelescopeState
from observatory.devices.telescope import ArrieroTelescope

if TYPE_CHECKING:
    from observatory.state import StateManager

def telescope_updater(telescope: "ArrieroTelescope", name, state: "StateManager" = None):
    if not telescope.alpaca.Connected:
        raise ConnectionError("Telescope not connected")
    
    try:
        device = state.get_device(name)
        device.connected = telescope.alpaca.Connected
        device.tracking = telescope.alpaca.Tracking
        device.slewing = telescope.alpaca.Slewing
        device.parked = telescope.alpaca.AtPark
        device.position = {"ra": telescope.alpaca.RightAscension, "dec": telescope.alpaca.Declination}
        device.side_of_pier = telescope.alpaca.SideOfPier
        
        if hasattr(telescope.alpaca, 'TargetRightAscension'):
            device.target = {
                "ra": telescope.alpaca.TargetRightAscension,
                "dec": telescope.alpaca.TargetDeclination
            }

        state.update_device(device)
    except Exception as e:
        print(f"Error updating telescope state: {e}")