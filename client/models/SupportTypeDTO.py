from dataclasses import dataclass
from typing import Any, Dict

from .BaseDTO import BaseDTO


@dataclass
class SupportTypeDTO(BaseDTO):
    idSupportType: int
    name: str
    mode: str

    @classmethod
    def fromDict(cls, data: Dict[str, Any]) -> "SupportTypeDTO":
        return cls(
            idSupportType=data["idSupportType"],
            name=data["name"],
            mode=data["mode"],
        )
