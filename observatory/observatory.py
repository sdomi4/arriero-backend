from typing import Dict
from observatory.state import StateManager

class Observatory:
    def __init__(self):
        self.devices: Dict[str, Dict[str, object]] = {
            "cameras": {},
            "conditions": {},
            "safety_monitors": {},
            "filterwheels": {},
            "domes": {},
            "telescopes": {},
            "covers": {},
            "switches": {}
        }
        self.state = StateManager()