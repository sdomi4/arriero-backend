from __future__ import annotations
from time import sleep
import time
import threading
from observatory.errors import StateError

from typing import Callable, Generic, TypeVar
import traceback

TAlpaca = TypeVar("TAlpaca")

class Arriero(Generic[TAlpaca]):
    def __init__(
            self,
            factory: Callable[[], TAlpaca],
            updater,
            poll_time: float = 1,
            name: str = "alpaca"
        ):
        self._alpaca: TAlpaca | None = None
        self._factory = factory
        self._updater = updater
        self._backoff = 1
        self._max_backoff = 60
        self._poll_time = poll_time
        self.name = name

        self._stop = threading.Event()
        self._thread = None

    @property
    def alpaca(self) -> TAlpaca:
        if self._alpaca is None:
            raise RuntimeError("Alpaca device is not connected")
        return self._alpaca

    def create(self):
        if self._thread and self._thread.is_alive():
            return self._alpaca
        
        try:
            self._alpaca = self._factory()
        except Exception as e:
            print("Error creating Alpaca device:", e)
            self._alpaca = None
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name=f"Arriero-{self.name}", daemon=True)
        self._thread.start()
        return self._alpaca
    
    def destroy(self, join_timeout: float = 2):
        self._stop.set()
        t = self._thread
        if t and t.is_alive():
            t.join(timeout=join_timeout)
        self._thread = None
        self._alpaca = None

    def _run(self):
        healthy = False
        while not self._stop.is_set():
            try:
                if self._alpaca is None:
                    self.reconnect()
                    if self._alpaca is None:
                        backoff = min(self._backoff * 2, self._max_backoff)
                        self._sleep_coop(backoff)
                        continue
                    backoff = 1
                
                self._updater()
                if not healthy:
                    healthy = True
                    self._backoff = 1

                self._sleep_coop(self._poll_time)
            
            except StateError as e:
                print("Error state reported in updater:", e)
                self._sleep_coop(self._poll_time)
            except Exception as e:
                print(f"Error in Alpaca updater: {e}")
                traceback.print_exc()
                self._alpaca = None
                healthy = False
                self._sleep_coop(self._backoff)
                self._backoff = min(self._backoff * 2, self._max_backoff)

    def is_running(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    def reconnect(self):
        try:
            self._alpaca = self._factory()
            if self._alpaca:
                print(f"Reconnected to {self.name} Alpaca device")
        except Exception as e:
            print(f"Error reconnecting to {self.name} Alpaca device:", e)
            self._alpaca = None

    def _sleep_coop(self, duration: float):
        end = time.monotonic() + duration
        while not self._stop.is_set():
            remaining = end - time.monotonic()
            if remaining <= 0:
                return
            sleep(min(0.2, remaining))
