from observatory.devices.base import ObservatoryDevice
from arriero.arriero import Arriero
from alpaca import telescope

class ArrieroTelescope(ObservatoryDevice[telescope.Telescope]):
    def __init__(self, observatory, factory, updater, poll_time=1, name="telescope"):
        arriero = Arriero(
            factory,
            updater,
            poll_time=poll_time,
            name=name,
        )
        super().__init__(observatory, arriero)
