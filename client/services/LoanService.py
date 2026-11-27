from typing import Dict, List, Optional, Tuple
from urllib.parse import quote

from models import FilmDTO, LoanDTO, SupportDTO, UserDTO

from exceptions import NotFoundError

from .ApiClient import ApiClient
from .FilmService import FilmService
from .SupportService import SupportService
from .UserService import UserService


class LoanService:
    def __init__(
        self,
        apiClient: ApiClient,
        supportService: SupportService,
        filmService: FilmService,
        userService: UserService,
    ) -> None:
        self._apiClient = apiClient
        self._supportService = supportService
        self._filmService = filmService
        self._userService = userService

    def getMyLoans(self) -> List[LoanDTO]:
        return self._loanList("/loans/me")

    def getMyActiveLoansBySupport(self) -> Dict[int, LoanDTO]:
        return self._activeLoansBySupport(self.getMyLoans())

    def getAllActiveLoansBySupport(self) -> Dict[int, LoanDTO]:
        return self._activeLoansBySupport(self.getAllLoans())

    def getMyLoan(self, idLoan: int) -> LoanDTO:
        return LoanDTO.fromDict(self._apiClient.get(f"/loans/me/{idLoan}"))

    def getAllLoans(self) -> List[LoanDTO]:
        return self._loanList("/loans")

    def getLoansByUserLogin(self, login: str) -> List[LoanDTO]:
        encodedLogin = quote(login, safe="")
        return self._loanList(f"/loans/user/{encodedLogin}")

    def getFilmTitlesByLoan(self, loans: List[LoanDTO]) -> Dict[int, str]:
        filmIdBySupport: Dict[int, str] = {}
        for idSupport in dict.fromkeys(
            loan.idPhysicalSupport for loan in loans
        ):
            support = self._supportService.getSupportById(idSupport)
            filmIdBySupport[idSupport] = support.idFilm

        titleByFilm = {
            idFilm: self._filmService.getFilmTitleById(idFilm)
            for idFilm in dict.fromkeys(filmIdBySupport.values())
        }
        return {
            loan.idLoan: titleByFilm[filmIdBySupport[loan.idPhysicalSupport]]
            for loan in loans
        }

    def getUserLogins(
        self, loans: List[LoanDTO], accessToken: str
    ) -> Dict[int, Optional[str]]:
        userLogins: Dict[int, Optional[str]] = {}
        for idUser in dict.fromkeys(loan.idUser for loan in loans):
            try:
                userLogins[idUser] = self._userService.getUser(
                    idUser, accessToken
                ).login
            except NotFoundError:
                userLogins[idUser] = None
        return userLogins

    def getLoan(self, idLoan: int) -> LoanDTO:
        return LoanDTO.fromDict(self._apiClient.get(f"/loans/{idLoan}"))

    def getMyLoanDetails(self, idLoan: int) -> Tuple[LoanDTO, SupportDTO, FilmDTO]:
        loan = self.getMyLoan(idLoan)
        support, film = self._supportAndFilm(loan)
        return loan, support, film

    def getLoanDetails(
        self, idLoan: int, accessToken: str
    ) -> Tuple[LoanDTO, SupportDTO, FilmDTO, UserDTO]:
        loan = self.getLoan(idLoan)
        support, film = self._supportAndFilm(loan)
        user = self._userService.getUser(loan.idUser, accessToken)
        return loan, support, film, user

    def returnLoan(self, idLoan: int) -> LoanDTO:
        data = self._apiClient.patch(f"/loans/{idLoan}/return")
        return LoanDTO.fromDict(data)

    def borrowSupport(self, idPhysicalSupport: int) -> LoanDTO:
        data = self._apiClient.post(
            "/loans", {"idPhysicalSupport": idPhysicalSupport}
        )
        return LoanDTO.fromDict(data)

    def _loanList(self, path: str) -> List[LoanDTO]:
        data = self._apiClient.get(path)
        return [LoanDTO.fromDict(item) for item in data]

    def _supportAndFilm(self, loan: LoanDTO) -> Tuple[SupportDTO, FilmDTO]:
        support = self._supportService.getSupportById(loan.idPhysicalSupport)
        film = self._filmService.getFilmById(support.idFilm)
        return support, film

    @staticmethod
    def _activeLoansBySupport(loans: List[LoanDTO]) -> Dict[int, LoanDTO]:
        return {
            loan.idPhysicalSupport: loan for loan in loans if not loan.isReturned
        }
