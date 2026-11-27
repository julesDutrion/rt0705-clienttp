"""DTOs du package Model (vidéothèque).

Les noms d'attributs suivent le diagramme de classes (camelCase) afin que
les clés JSON de l'API correspondent exactement au modèle.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from datetime import date
from typing import Any, Dict, List, Optional
from models import BaseDTO

@dataclass
class RoleDTO(BaseDTO):
    """Classe qui représente les données d'un rôle."""

    idRole: int
    roleName: str

    @classmethod
    def fromDict(cls, data: Dict[str, Any]) -> "RoleDTO":
        """
        Méthode qui construit un rôle à partir d'un dictionnaire.

        :param data: Données du rôle.
        :return: Rôle correspondant.
        :raises KeyError: Si une donnée obligatoire est absente.
        """
        return cls(idRole=data["idRole"], roleName=data["roleName"])