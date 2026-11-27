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
class DirectorDTO(BaseDTO):
    """Classe qui représente les données d'un réalisateur."""

    idDirector: int
    lastName: str
    firstName: str

    @classmethod
    def fromDict(cls, data: Dict[str, Any]) -> "DirectorDTO":
        """
        Méthode qui construit un réalisateur à partir d'un dictionnaire.

        :param data: Données du réalisateur.
        :return: Réalisateur correspondant.
        :raises KeyError: Si une donnée obligatoire est absente.
        """
        return cls(
            idDirector=data["idDirector"],
            lastName=data["lastName"],
            firstName=data["firstName"],
        )