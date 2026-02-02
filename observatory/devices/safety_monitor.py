from observatory.devices.base import ObservatoryDevice
from arriero.arriero import Arriero
from alpaca import safetymonitor
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from observatory.observatory import Observatory

class ArrieroSafetyMonitor(ObservatoryDevice[safetymonitor.SafetyMonitor]):
    def __init__(self, observatory: "Observatory", factory: Callable[[], safetymonitor.SafetyMonitor], updater: Callable[[], None], id: str, name: str = None, poll_time: float = 1):
        arriero = Arriero(
            factory,
            updater,
            poll_time=poll_time,
            name=name or id,
        )
        super().__init__(observatory, arriero, id=id, name=name)
