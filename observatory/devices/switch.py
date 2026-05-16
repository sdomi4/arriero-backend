from observatory.devices.base import ObservatoryDevice
from alpaquero.alpaquero import Alpaquero
from alpaca import switch
from observatory.errors import SwitchError
from observatory.state import RangeControl, ToggleControl
from typing import TYPE_CHECKING, Callable

from observatory.action_registry import ActionRegistry

if TYPE_CHECKING:
    from observatory.observatory import Observatory

class AlpaqueroSwitch(ObservatoryDevice[switch.Switch]):
    def __init__(self, observatory: "Observatory", factory: Callable[[], switch.Switch], updater: Callable[[], None], id: str, name: str = None, poll_time: float = 1):
        alpaquero = Alpaquero(
            factory,
            updater,
            poll_time=poll_time,
            name=name or id,
        )
        super().__init__(observatory, alpaquero, id=id, name=name)

    @ActionRegistry.register("set_switch", observatory_arg=False, action_type="device")
    def set_switch(self, switch_number: int, value: float):
        try:
            control = self._get_control(switch_number)
            switch_value = float(value)
            if isinstance(control, RangeControl):
                self.alpaca.SetSwitchValue(switch_number, int(switch_value))
                control.value = switch_value
                return

            if isinstance(control, ToggleControl):
                switch_status = bool(switch_value)
                self.alpaca.SetSwitch(switch_number, switch_status)
                control.value = switch_status
                return

            raise ValueError(f"Switch {switch_number} is not available in device state")
        except Exception as e:
            raise SwitchError(code="switch_set_failed", message=f"Error setting switch {switch_number} on {self.alpaquero.name} to {value}: {e}")

    def _get_control(self, switch_number: int):
        device = self.observatory.state.get_device(self.id)
        for control in device.controls.values():
            if control.id == switch_number:
                return control
        raise ValueError(f"Switch {switch_number} is not available in device state")
