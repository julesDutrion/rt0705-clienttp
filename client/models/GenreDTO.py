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
class GenreDTO(BaseDTO):
    """Classe qui représente les données d'un genre."""

    idGenre: int
    nameGenre: str

    @classmethod
    def fromDict(cls, data: Dict[str, Any]) -> "GenreDTO":
        """
        Méthode qui construit un genre à partir d'un dictionnaire.

        :param data: Données du genre.
        :return: Genre correspondant.
        :raises KeyError: Si une donnée obligatoire est absente.
        """
        return cls(idGenre=data["idGenre"], nameGenre=data["nameGenre"])
