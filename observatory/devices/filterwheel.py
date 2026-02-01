from observatory.devices.base import ObservatoryDevice
from arriero.arriero import Arriero
from alpaca import filterwheel

class ArrieroFilterWheel(ObservatoryDevice[filterwheel.FilterWheel]):
    def __init__(self, observatory, factory, updater, id: str, name: str = None, poll_time=1):
        arriero = Arriero(
            factory,
            updater,
            poll_time=poll_time,
            name=name or id,
        )
        super().__init__(observatory, arriero, id=id, name=name)
