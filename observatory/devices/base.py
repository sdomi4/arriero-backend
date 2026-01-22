from abc import ABC
from typing import TypeVar, Generic

TAlpaca = TypeVar("TAlpaca")

class ObservatoryDevice(ABC, Generic[TAlpaca]):
    def __init__(self, observatory, arriero):
        self.observatory = observatory
        self.arriero = arriero

    @property
    def alpaca(self) -> TAlpaca:
        return self.arriero.alpaca
    
    def connect(self):
        return self.arriero.create()
    
    def disconnect(self):
        self.arriero.destroy()