from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from observatory.state import StateManager

def telescope_updater(telescope, name, state: "StateManager" = None):
    if not telescope.alpaca.Connected:
        raise ConnectionError("Telescope not connected")

    # assume connected must mean booted as well
    state.update_key("mount", {
        name: {
            "booted": True,
            "tracking": telescope.alpaca.Tracking,
            "slewing": telescope.alpaca.Slewing,
            "parked": telescope.alpaca.AtPark,
            "homed": telescope.alpaca.AtHome,
            "position": {
                "ra": telescope.alpaca.RightAscension,
                "dec": telescope.alpaca.Declination
            }
        }
    })