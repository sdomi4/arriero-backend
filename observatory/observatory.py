from typing import Dict

from observatory.devices.camera import ArrieroCamera
from arriero.factories.camera import camera_factory
from arriero.updaters.camera import camera_updater

from observatory.devices.observing_conditions import ArrieroObservingConditions
from arriero.factories.observing_conditions import observing_conditions_factory
from arriero.updaters.observing_conditions import observing_conditions_updater

from observatory.devices.cover import ArrieroCover
from arriero.factories.cover import cover_factory
from arriero.updaters.cover import cover_updater

from observatory.devices.filterwheel import ArrieroFilterWheel
from arriero.factories.filterwheel import filterwheel_factory
from arriero.updaters.filterwheel import filterwheel_updater

from observatory.devices.safety_monitor import ArrieroSafetyMonitor
from arriero.factories.safety_monitor import safety_monitor_factory
from arriero.updaters.safety_monitor import safety_monitor_updater

from observatory.devices.dome import ArrieroDome
from arriero.factories.dome import dome_factory
from arriero.updaters.dome import dome_updater

from observatory.devices.switch import ArrieroSwitch
from arriero.factories.switch import switch_factory
from arriero.updaters.switch import switch_updater

from observatory.devices.telescope import ArrieroTelescope
from arriero.factories.telescope import telescope_factory
from arriero.updaters.telescope import telescope_updater

from observatory.state import StateManager

from observatory.utils.config import load_observatory_config

class Observatory:
    def __init__(self):
        self.domes: Dict[str, 'ArrieroDome'] = {}
        self.telescopes: Dict[str, 'ArrieroTelescope'] = {}
        self.observing_conditions: Dict[str, 'ArrieroObservingConditions'] = {}
        self.safety_monitors: Dict[str, 'ArrieroSafetyMonitor'] = {}
        self.covers: Dict[str, 'ArrieroCover'] = {}
        self.cameras: Dict[str, 'ArrieroCamera'] = {}
        self.filterwheels: Dict[str, 'ArrieroFilterWheel'] = {}
        self.switches: Dict[str, 'ArrieroSwitch'] = {}

        #self.rituals = RitualManager()

        self.status = "initializing"

        # Init state
        self.state = StateManager()


    def startup(self):
        config = load_observatory_config()
        # Create all devices discovered in config
        for device in config.get("devices", []):
            print(device)
            device_type = device.get("type")
            device_id = device.get("id")
            name = device.get("name")
            poll_time = device.get("poll_time", 1)
            auto_connect = device.get("auto_connect", False)

            host = device.get("host")
            port = device.get("port")
            device_number = device.get("device_number")

            if device_type == "dome":
                device_arriero = ArrieroDome(
                    observatory=self,
                    factory=lambda h=host, p=port, did=device_id, dn=device_number: dome_factory(
                        address=f"{h}:{p}",
                        id=did,
                        device_number=dn,
                        state=self.state
                    ),
                    updater=lambda did=device_id: dome_updater(
                        dome=self.domes[did],
                        id=did,
                        state=self.state
                    ),
                    poll_time=poll_time,
                    name=name
                )
                self.domes[device_id] = device_arriero
            elif device_type == "telescope":
                device_arriero = ArrieroTelescope(
                    observatory=self,
                    factory=lambda h=host, p=port, did=device_id, dn=device_number: telescope_factory(
                        address=f"{h}:{p}",
                        id=did,
                        device_number=dn,
                        state=self.state
                    ),
                    updater=lambda did=device_id: telescope_updater(
                        telescope=self.telescopes[did],
                        id=did,
                        state=self.state
                    ),
                    poll_time=poll_time,
                    name=name,
                )
                self.telescopes[device_id] = device_arriero
            elif device_type == "camera":
                device_arriero = ArrieroCamera(
                    observatory=self,
                    factory=lambda h=host, p=port, did=device_id, dn=device_number: camera_factory(
                        address=f"{h}:{p}",
                        id=did,
                        device_number=dn,
                        state=self.state
                    ),
                    updater=lambda did=device_id: camera_updater(
                        camera=self.cameras[did],
                        id=did,
                        state=self.state
                    ),
                    poll_time=poll_time,
                    name=name,
                )
                self.cameras[device_id] = device_arriero
            elif device_type == "observing_conditions":
                device_arriero = ArrieroObservingConditions(
                    observatory=self,
                    factory=lambda h=host, p=port, did=device_id, dn=device_number: observing_conditions_factory(
                        address=f"{h}:{p}",
                        id=did,
                        device_number=dn,
                        state=self.state
                    ),
                    updater=lambda did=device_id: observing_conditions_updater(
                        observing_conditions=self.observing_conditions[did],
                        id=did,
                        state=self.state
                    ),
                    poll_time=poll_time,
                    name=name,
                )
                self.observing_conditions[device_id] = device_arriero
            elif device_type == "safety_monitor":
                device_arriero = ArrieroSafetyMonitor(
                    observatory=self,
                    factory=lambda h=host, p=port, did=device_id, dn=device_number: safety_monitor_factory(
                        address=f"{h}:{p}",
                        id=did,
                        device_number=dn,
                        state=self.state
                    ),
                    updater=lambda did=device_id: safety_monitor_updater(
                        safety_monitor=self.safety_monitors[did],
                        id=did,
                        state=self.state
                    ),
                    poll_time=poll_time,
                    name=name,
                )
                self.safety_monitors[device_id] = device_arriero
            elif device_type == "cover":
                device_arriero = ArrieroCover(
                    observatory=self,
                    factory=lambda h=host, p=port, did=device_id, dn=device_number: cover_factory(
                        address=f"{h}:{p}",
                        id=did,
                        device_number=dn,
                        state=self.state
                    ),
                    updater=lambda did=device_id: cover_updater(
                        cover=self.covers[did],
                        id=did,
                        state=self.state
                    ),
                    poll_time=poll_time,
                    name=name,
                )
                self.covers[device_id] = device_arriero
            elif device_type == "filterwheel":
                device_arriero = ArrieroFilterWheel(
                    observatory=self,
                    factory=lambda h=host, p=port, did=device_id, dn=device_number: filterwheel_factory(
                        address=f"{h}:{p}",
                        id=did,
                        device_number=dn,
                        state=self.state
                    ),
                    updater=lambda did=device_id: filterwheel_updater(
                        filterwheel=self.filterwheels[did],
                        id=did,
                        state=self.state
                    ),
                    poll_time=poll_time,
                    name=name,
                )
                self.filterwheels[device_id] = device_arriero
            elif device_type == "switch":
                device_arriero = ArrieroSwitch(
                    observatory=self,
                    factory=lambda h=host, p=port, did=device_id, dn=device_number: switch_factory(
                        address=f"{h}:{p}",
                        id=did,
                        device_number=dn,
                        state=self.state
                    ),
                    updater=lambda did=device_id: switch_updater(
                        switch_device=self.switches[did],
                        id=did,
                        state=self.state
                    ),
                    poll_time=poll_time,
                    name=name,
                )
                self.switches[device_id] = device_arriero
            else:
                raise ValueError(f"Unknown device type: {device_type}")

            
            if auto_connect:
                print("="*40, "reached auto connect for", device_type, name)
                device_arriero.connect()
        # Start observatory loops
        pass
