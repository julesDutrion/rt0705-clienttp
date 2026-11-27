from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Dict, Optional

from .BaseDTO import BaseDTO
from .SupportTypeDTO import SupportTypeDTO


@dataclass
class LoanDTO(BaseDTO):
    """Classe qui représente les données d'un emprunt."""

    idLoan: int
    idUser: int
    idPhysicalSupport: int
    startDate: date
    expectedReturnDate: date
    actualReturnDate: Optional[date]
    status: str
    statusLabel: str
    supportType: Optional[SupportTypeDTO] = None

    @classmethod
    def fromDict(cls, data: Dict[str, Any]) -> "LoanDTO":
        """
        Méthode qui construit un emprunt à partir d'un dictionnaire.

        :param data: Données de l'emprunt.
        :return: Emprunt correspondant.
        :raises KeyError: Si une donnée obligatoire est absente.
        :raises ValueError: Si une date ne respecte pas le format ISO.
        """
        def parseDate(value: Any) -> date:
            """
            Méthode qui convertit une valeur en date.

            :param value: Valeur de date reçue de l'API.
            :return: Date correspondante.
            :raises ValueError: Si la valeur n'est pas une date valide.
            """
            if isinstance(value, datetime):
                return value.date()
            if isinstance(value, date):
                return value
            return date.fromisoformat(str(value)[:10])

        supportType = data.get("supportType")
        return cls(
            idLoan=data["idLoan"],
            idUser=data["idUser"],
            idPhysicalSupport=data["idPhysicalSupport"],
            startDate=parseDate(data["startDate"]),
            expectedReturnDate=parseDate(data["expectedReturnDate"]),
            actualReturnDate=(
                parseDate(data["actualReturnDate"])
                if data.get("actualReturnDate") is not None
                else None
            ),
            status=data["status"],
            statusLabel=data["statusLabel"],
            supportType=(
                SupportTypeDTO.fromDict(supportType) if supportType else None
            ),
        )

    @property
    def isReturned(self) -> bool:
        """
        Méthode qui indique si l'emprunt a été retourné.

        :return: `True` si une date de retour effective est définie.
        """
        return self.actualReturnDate is not None

    @property
    def isOverdue(self) -> bool:
        """
        Méthode qui indique si l'emprunt est en retard.

        :return: `True` si l'emprunt actif porte l'état « OVERDUE ».
        """
        return not self.isReturned and self.status == "OVERDUE"
