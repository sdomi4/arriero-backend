from observatory.devices.base import ObservatoryDevice
from arriero.arriero import Arriero
from alpaca import dome
from observatory.errors import DomeError
from time import sleep

class ArrieroDome(ObservatoryDevice[dome.Dome]):
    def __init__(self, observatory, factory, updater, poll_time=1, name="dome"):
        arriero = Arriero(
            factory,
            updater,
            poll_time=poll_time,
            name=name,
        )
        super().__init__(observatory, arriero)

    def open(self):
        self.observatory.state.update_key("dome", {self.arriero.name: {"status": "opening"}})
        self.observatory.state.add_action("dome", f"Opening {self.arriero.name}")

        try:
            self.alpaca.OpenShutter()
        except Exception as e:
            self.observatory.state.remove_action("dome")
            raise DomeError(f"Error opening dome {self.arriero.name}: {e}")
        
        while True:
            try:
                status = self.alpaca.ShutterStatus
                self.observatory.state.update_key("dome", {self.arriero.name: {"status": status}})
                if status == 0:
                    self.observatory.state.remove_action("dome")           
                    break
                sleep(1)
            except Exception as e:
                self.observatory.state.remove_action("dome")
                raise DomeError(f"Error monitoring dome {self.arriero.name} while opening: {e}")
