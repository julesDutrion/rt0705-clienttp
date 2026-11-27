"""DTOs du package Model (vidéothèque).

Les noms d'attributs suivent le diagramme de classes (camelCase) afin que
les clés JSON de l'API correspondent exactement au modèle.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from datetime import date
from typing import Any, Dict, List, Optional
from .BaseDTO import BaseDTO


@dataclass
class ActorDTO(BaseDTO):
    """Classe qui représente les données d'un acteur."""

    idActor: int
    firstName: str
    lastName: str

    @classmethod
    def fromDict(cls, data: Dict[str, Any]) -> "ActorDTO":
        """
        Méthode qui construit un acteur à partir d'un dictionnaire.

        :param data: Données de l'acteur.
        :return: Acteur correspondant.
        :raises KeyError: Si une donnée obligatoire est absente.
        """
        return cls(
            idActor=data["idActor"],
            firstName=data["firstName"],
            lastName=data["lastName"],
        )