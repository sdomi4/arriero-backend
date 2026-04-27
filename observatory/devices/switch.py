from observatory.devices.base import ObservatoryDevice
from arriero.arriero import Arriero
from alpaca import switch
from observatory.errors import SwitchError
from typing import TYPE_CHECKING, Callable

from observatory.action_registry import ActionRegistry

if TYPE_CHECKING:
    from observatory.observatory import Observatory

class ArrieroSwitch(ObservatoryDevice[switch.Switch]):
    def __init__(self, observatory: "Observatory", factory: Callable[[], switch.Switch], updater: Callable[[], None], id: str, name: str = None, poll_time: float = 1):
        arriero = Arriero(
            factory,
            updater,
            poll_time=poll_time,
            name=name or id,
        )
        super().__init__(observatory, arriero, id=id, name=name)

    @ActionRegistry.register("set_switch", observatory_arg=False, action_type="device")
    def set_switch(self, switch_number: int, switch_status: bool):
        try:
            self.alpaca.SetSwitch(switch_number, switch_status)
        except Exception as e:
            raise SwitchError(code="switch_set_failed", message=f"Error setting switch {switch_number} on {self.arriero.name} to {switch_status}: {e}")
