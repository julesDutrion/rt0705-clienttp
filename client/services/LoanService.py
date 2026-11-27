from typing import Dict, List, Optional, Tuple
from urllib.parse import quote

from models import FilmDTO, LoanDTO, SupportDTO, UserDTO

from exceptions import NotFoundError

from .ApiClient import ApiClient
from .FilmService import FilmService
from .SupportService import SupportService
from .UserService import UserService


class LoanService:
    """Classe qui représente le service de gestion des emprunts."""

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
        """
        Méthode qui récupère les emprunts de l'utilisateur connecté.

        :return: Emprunts personnels.
        :raises ClientError: Si l'appel API échoue.
        """
        return self._loanList("/loans/me")

    def getMyActiveLoansBySupport(self) -> Dict[int, LoanDTO]:
        """
        Méthode qui récupère les emprunts personnels actifs par support.

        :return: Emprunts actifs indexés par support physique.
        :raises ClientError: Si l'appel API échoue.
        """
        return self._activeLoansBySupport(self.getMyLoans())

    def getAllActiveLoansBySupport(self) -> Dict[int, LoanDTO]:
        """
        Méthode qui récupère tous les emprunts actifs par support.

        :return: Emprunts actifs indexés par support physique.
        :raises ClientError: Si l'appel API échoue.
        """
        return self._activeLoansBySupport(self.getAllLoans())

    def getMyLoan(self, idLoan: int) -> LoanDTO:
        """
        Méthode qui récupère un emprunt de l'utilisateur connecté.

        :param idLoan: Identifiant de l'emprunt.
        :return: Emprunt correspondant.
        :raises ClientError: Si l'emprunt est inaccessible ou l'appel API échoue.
        """
        return LoanDTO.fromDict(self._apiClient.get(f"/loans/me/{idLoan}"))

    def getAllLoans(self) -> List[LoanDTO]:
        """
        Méthode qui récupère tous les emprunts.

        :return: Liste des emprunts.
        :raises ClientError: Si l'appel API échoue.
        """
        return self._loanList("/loans")

    def getLoansByUserLogin(self, login: str) -> List[LoanDTO]:
        """
        Méthode qui récupère les emprunts associés à un login.

        :param login: Login de l'utilisateur recherché.
        :return: Emprunts de l'utilisateur.
        :raises ClientError: Si l'utilisateur est introuvable ou l'appel API échoue.
        """
        encodedLogin = quote(login, safe="")
        return self._loanList(f"/loans/user/{encodedLogin}")

    def getFilmTitlesByLoan(self, loans: List[LoanDTO]) -> Dict[int, str]:
        """
        Méthode qui associe chaque emprunt au titre de son film.

        :param loans: Emprunts à associer.
        :return: Titres indexés par identifiant d'emprunt.
        :raises ClientError: Si un support ou un film est introuvable.
        """
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
        """
        Méthode qui associe les emprunts aux logins de leurs utilisateurs.

        :param loans: Emprunts à associer.
        :param accessToken: Jeton JWT autorisé à lire les comptes.
        :return: Logins indexés par identifiant utilisateur, ou `None` si absent.
        :raises ClientError: Si un appel API échoue hors utilisateur introuvable.
        """
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
        """
        Méthode qui récupère un emprunt par identifiant.

        :param idLoan: Identifiant de l'emprunt.
        :return: Emprunt correspondant.
        :raises ClientError: Si l'appel API échoue.
        """
        return LoanDTO.fromDict(self._apiClient.get(f"/loans/{idLoan}"))

    def getMyLoanDetails(self, idLoan: int) -> Tuple[LoanDTO, SupportDTO, FilmDTO]:
        """
        Méthode qui récupère l'emprunt personnel et son support et film.

        :param idLoan: Identifiant de l'emprunt.
        :return: Emprunt, support associé et film concerné.
        :raises ClientError: Si une ressource est introuvable ou l'API échoue.
        """
        loan = self.getMyLoan(idLoan)
        support, film = self._supportAndFilm(loan)
        return loan, support, film

    def getLoanDetails(
        self, idLoan: int, accessToken: str
    ) -> Tuple[LoanDTO, SupportDTO, FilmDTO, UserDTO]:
        """
        Méthode qui récupère un emprunt et les informations associées.

        :param idLoan: Identifiant de l'emprunt.
        :param accessToken: Jeton JWT autorisé à lire le compte.
        :return: Emprunt, support, film et utilisateur concernés.
        :raises ClientError: Si une ressource est introuvable ou l'API échoue.
        """
        loan = self.getLoan(idLoan)
        support, film = self._supportAndFilm(loan)
        user = self._userService.getUser(loan.idUser, accessToken)
        return loan, support, film, user

    def returnLoan(self, idLoan: int) -> LoanDTO:
        """
        Méthode qui enregistre le retour d'un emprunt.

        :param idLoan: Identifiant de l'emprunt à retourner.
        :return: Emprunt retourné selon la réponse API.
        :raises ClientError: Si l'emprunt est déjà retourné ou l'API échoue.
        """
        data = self._apiClient.patch(f"/loans/{idLoan}/return")
        return LoanDTO.fromDict(data)

    def borrowSupport(self, idPhysicalSupport: int) -> LoanDTO:
        """
        Méthode qui emprunte un support physique.

        :param idPhysicalSupport: Identifiant du support à emprunter.
        :return: Emprunt créé.
        :raises ClientError: Si le support est indisponible ou l'API échoue.
        """
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
