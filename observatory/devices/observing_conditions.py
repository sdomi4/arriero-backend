from observatory.devices.base import ObservatoryDevice
from alpaquero.alpaquero import Alpaquero
from alpaca import observingconditions
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from observatory.observatory import Observatory

class AlpaqueroObservingConditions(ObservatoryDevice[observingconditions.ObservingConditions]):
    def __init__(self, observatory: "Observatory", factory: Callable[[], observingconditions.ObservingConditions], updater: Callable[[], None], id: str, name: str = None, poll_time: float = 1):
        alpaquero = Alpaquero(
            factory,
            updater,
            poll_time=poll_time,
            name=name or id,
        )
        super().__init__(observatory, alpaquero, id=id, name=name)
