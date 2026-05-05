from observatory.devices.base import ObservatoryDevice
from alpaquero.alpaquero import Alpaquero
from alpaca import filterwheel
from observatory.errors import FilterWheelError
from time import sleep
from typing import TYPE_CHECKING, Callable

from observatory.action_registry import ActionRegistry

if TYPE_CHECKING:
    from observatory.observatory import Observatory

class AlpaqueroFilterWheel(ObservatoryDevice[filterwheel.FilterWheel]):
    def __init__(self, observatory: "Observatory", factory: Callable[[], filterwheel.FilterWheel], updater: Callable[[], None], id: str, name: str = None, poll_time: float = 1):
        alpaquero = Alpaquero(
            factory,
            updater,
            poll_time=poll_time,
            name=name or id,
        )
        super().__init__(observatory, alpaquero, id=id, name=name)

    @ActionRegistry.register("move_filterwheel", observatory_arg=False, action_type="device")
    def move(self, target_position: int):
        state_device = self.observatory.state.get_device(self.id)
        try:
            if not self.alpaca.Connected:
                raise FilterWheelError(code="filterwheel_not_connected", message=f"Filter wheel {self.alpaquero.name} not connected")
            
            if self.alpaca.Position == target_position:
                return  # Already in the desired position
            
            self.observatory.state.add_action(f"Moving {self.alpaquero.name} to position {target_position}")
            self.alpaca.Position = target_position
            
            timeout = 10
            while self.alpaca.Position == -1 and timeout > 0:
                sleep(1)
                timeout -= 1
            
            if self.alpaca.Position != target_position:
                self.observatory.state.remove_action(f"Moving {self.alpaquero.name} to position {target_position}")
                raise FilterWheelError(code="filterwheel_move_timeout", message=f"Timeout moving filter wheel {self.alpaquero.name} to position {target_position}")
            
            state_device.position = self.alpaca.Position
            self.observatory.state.remove_action(f"Moving {self.alpaquero.name} to position {target_position}")
        except Exception as e:
            self.observatory.state.remove_action(f"Moving {self.alpaquero.name} to position {target_position}")
            raise FilterWheelError(code="filterwheel_move_failed", message=f"Error moving filter wheel {self.alpaquero.name}: {e}")

    async def trigger_move(self, target_position: int):
        self.dispatch_trigger(self.move, target_position)
