"""DTOs du package Model (vidéothèque).

Les noms d'attributs suivent le diagramme de classes (camelCase) afin que
les clés JSON de l'API correspondent exactement au modèle.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .BaseDTO import BaseDTO
from .SupportTypeDTO import SupportTypeDTO

@dataclass
class SupportDTO(BaseDTO):
    idFilm: str
    idSupportType: int
    idSupport: Optional[int] = None
    location: Optional[str] = None
    url: Optional[str] = None
    supportType: Optional[SupportTypeDTO] = None

    @classmethod
    def fromDict(cls, data: Dict[str, Any]) -> "SupportDTO":
        return cls(
            idSupport=data.get("idSupport"),
            idFilm=data["idFilm"],
            idSupportType=data["idSupportType"],
            location=data.get("location"),
            url=data.get("url"),
            supportType=(
                SupportTypeDTO.fromDict(data["supportType"])
                if data.get("supportType")
                else None
            ),
        )
