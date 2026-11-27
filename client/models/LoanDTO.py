from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Dict, Optional

from .BaseDTO import BaseDTO
from .SupportTypeDTO import SupportTypeDTO


@dataclass
class LoanDTO(BaseDTO):
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
        def parseDate(value: Any) -> date:
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
        return self.actualReturnDate is not None

    @property
    def isOverdue(self) -> bool:
        return not self.isReturned and self.status == "OVERDUE"
