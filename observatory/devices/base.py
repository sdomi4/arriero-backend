from abc import ABC
from typing import TypeVar, Generic, TYPE_CHECKING

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

    @property
    def alpaca(self) -> TAlpaca:
        return self.arriero.alpaca
    
    def connect(self):
        return self.arriero.create()
    
    def disconnect(self):
        self.arriero.destroy()