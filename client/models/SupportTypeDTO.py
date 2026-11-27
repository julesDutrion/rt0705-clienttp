from dataclasses import dataclass
from typing import Any, Dict

from .BaseDTO import BaseDTO


@dataclass
class SupportTypeDTO(BaseDTO):
    """Classe qui représente les données d'un type de support."""

    idSupportType: int
    name: str
    mode: str

    @classmethod
    def fromDict(cls, data: Dict[str, Any]) -> "SupportTypeDTO":
        """
        Méthode qui construit un type de support à partir d'un dictionnaire.

        :param data: Données du type de support.
        :return: Type de support correspondant.
        :raises KeyError: Si une donnée obligatoire est absente.
        """
        return cls(
            idSupportType=data["idSupportType"],
            name=data["name"],
            mode=data["mode"],
        )
