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
class LanguageDTO(BaseDTO):
    """Classe qui représente les données d'une langue."""

    idLanguage: int
    code: str
    name: str

    @classmethod
    def fromDict(cls, data: Dict[str, Any]) -> "LanguageDTO":
        """
        Méthode qui construit une langue à partir d'un dictionnaire.

        :param data: Données de la langue.
        :return: Langue correspondante.
        :raises KeyError: Si une donnée obligatoire est absente.
        """
        return cls(
            idLanguage=data["idLanguage"],
            code=data["code"],
            name=data["name"],
        )