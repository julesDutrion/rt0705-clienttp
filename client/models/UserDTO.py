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
    """Classe qui représente les données publiques d'un utilisateur."""

    role: str
    login: str
    email: str
    birthDate: str
    age: Optional[int] = None
    idUser: Optional[int] = None

    @classmethod
    def fromDict(cls, data: Dict[str, Any]) -> "UserDTO":
        """
        Méthode qui construit un utilisateur à partir d'un dictionnaire.

        :param data: Données de l'utilisateur.
        :return: Utilisateur correspondant.
        :raises KeyError: Si une donnée obligatoire est absente.
        """
        return cls(
            role=data["role"],
            login=data["login"],
            email=data["email"],
            birthDate=data["birthDate"],
            age=data.get("age"),
            idUser=data.get("idUser"),
        )

    def toPublicDict(self) -> Dict[str, Any]:
        """
        Méthode qui retourne les données publiques de l'utilisateur.

        :return: Dictionnaire des informations publiques.
        """
        return self.toDict()