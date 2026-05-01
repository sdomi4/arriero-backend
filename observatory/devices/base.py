from abc import ABC
import asyncio
from typing import Any, TypeVar, Generic, TYPE_CHECKING, Callable

from observatory.action_registry import ActionRegistry

if TYPE_CHECKING:
    from observatory.observatory import Observatory
    from arriero.arriero import Arriero

TAlpaca = TypeVar("TAlpaca")

class ObservatoryDevice(ABC, Generic[TAlpaca]):
    def __init__(self, observatory: "Observatory", arriero: "Arriero[TAlpaca]", id: str, name: str = None):
        self.observatory: "Observatory" = observatory
        self.arriero: "Arriero[TAlpaca]" = arriero
        self.id = id
        self.name = name or id
        self.arriero.set_on_destroy(self._mark_disconnected)

    @property
    def alpaca(self) -> TAlpaca:
        return self.arriero.alpaca
    
    @ActionRegistry.register("connect_device", observatory_arg=False, action_type="device")
    def connect(self):
        return self.arriero.create()
    
    @ActionRegistry.register("disconnect_device", observatory_arg=False, action_type="device")
    def disconnect(self):
        self.arriero.destroy()

    def _mark_disconnected(self) -> None:
        try:
            self.observatory.state.set_device_connected(self.id, False)
        except ValueError:
            return

    def dispatch_trigger(self, action: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        task = asyncio.create_task(asyncio.to_thread(action, *args, **kwargs))
        task.add_done_callback(self._handle_trigger_result)

    def _handle_trigger_result(self, task: "asyncio.Task[Any]") -> None:
        try:
            task.result()
        except Exception as e:
            print("oppla trigger failed:", e)
