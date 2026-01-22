from observatory.devices.base import ObservatoryDevice
from arriero.arriero import Arriero
from alpaca import switch

class ArrieroSwitch(ObservatoryDevice[switch.Switch]):
    def __init__(self, observatory, factory, updater, poll_time=1, name="switch"):
        arriero = Arriero(
            factory,
            updater,
            poll_time=poll_time,
            name=name,
        )
        super().__init__(observatory, arriero)
