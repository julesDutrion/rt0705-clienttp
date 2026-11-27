"""DTOs du package Model (vidéothèque).

Les noms d'attributs suivent le diagramme de classes (camelCase) afin que
les clés JSON de l'API correspondent exactement au modèle.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .BaseDTO import BaseDTO


@dataclass
class UserDTO(BaseDTO):
    role: str
    login: str
    email: str
    birthDate: str
    age: Optional[int] = None
    idUser: Optional[int] = None

    @classmethod
    def fromDict(cls, data: Dict[str, Any]) -> "UserDTO":
        return cls(
            role=data["role"],
            login=data["login"],
            email=data["email"],
            birthDate=data["birthDate"],
            age=data.get("age"),
            idUser=data.get("idUser"),
        )

    def toPublicDict(self) -> Dict[str, Any]:
        return self.toDict()