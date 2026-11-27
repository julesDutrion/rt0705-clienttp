from functools import wraps
from typing import Any, Callable, List, Tuple

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from exceptions import AlreadyExistsError, InvalidReferenceError, NotFoundError
from models import LoanDTO
from services import LoanService

MANAGER_ROLES = {"manager", "adminstrateur"}


def _loginRequired(function: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any):
        """
        Méthode qui vérifie la présence d'une session utilisateur.

        :param args: Arguments de la route protégée.
        :param kwargs: Arguments nommés de la route protégée.
        :return: Réponse de la route ou redirection vers la connexion.
        """
        if not session.get("accessToken") or not session.get("user"):
            flash("Connectez-vous pour accéder à cette page.", "error")
            return redirect(url_for("account.login"))
        return function(*args, **kwargs)

    return wrapper


def _managerRequired(function: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(function)
    @_loginRequired
    def wrapper(*args: Any, **kwargs: Any):
        """
        Méthode qui vérifie le rôle gestionnaire ou administrateur.

        :param args: Arguments de la route protégée.
        :param kwargs: Arguments nommés de la route protégée.
        :return: Réponse de la route protégée.
        :raises HTTPException: Si le rôle est insuffisant.
        """
        if session["user"].get("role") not in MANAGER_ROLES:
            abort(403)
        return function(*args, **kwargs)

    return wrapper


def _splitLoans(loans: List[LoanDTO]) -> Tuple[List[LoanDTO], List[LoanDTO]]:
    currentLoans = [loan for loan in loans if not loan.isReturned]
    pastLoans = [loan for loan in loans if loan.isReturned]
    return currentLoans, pastLoans


def createLoanBlueprint(loanService: LoanService) -> Blueprint:
    """
    Méthode qui crée les routes des emprunts.

    :param loanService: Service de gestion des emprunts.
    :return: Blueprint Flask des emprunts.
    """
    blueprint = Blueprint("loans", __name__, url_prefix="/loans")

    @blueprint.get("")
    @_loginRequired
    def myLoans():
        """
        Méthode qui affiche les emprunts personnels et leur historique.

        :return: Page HTML des emprunts personnels.
        :raises ClientError: Si un appel API échoue.
        """
        loans = loanService.getMyLoans()
        currentLoans, pastLoans = _splitLoans(loans)
        return render_template(
            "loans/my_loans.html",
            currentLoans=currentLoans,
            pastLoans=pastLoans,
            filmTitles=loanService.getFilmTitlesByLoan(loans),
        )

    @blueprint.get("/<int:idLoan>")
    @_loginRequired
    def myLoanDetail(idLoan: int):
        """
        Méthode qui affiche le détail d'un emprunt personnel.

        :param idLoan: Identifiant de l'emprunt.
        :return: Page HTML du détail de l'emprunt.
        :raises ClientError: Si l'emprunt ou une ressource associée est introuvable.
        """
        loan, support, film = loanService.getMyLoanDetails(idLoan)
        return render_template(
            "loans/detail.html",
            loan=loan,
            support=support,
            film=film,
            userLogin=session["user"]["login"],
            isManagement=False,
            canReturn=False,
        )

    @blueprint.post(
        "/support/<int:idPhysicalSupport>/borrow/<string:idFilm>"
    )
    @_loginRequired
    def borrowSupport(idPhysicalSupport: int, idFilm: str):
        """
        Méthode qui demande l'emprunt d'un support physique.

        :param idPhysicalSupport: Identifiant du support.
        :param idFilm: Identifiant du film de destination.
        :return: Redirection vers le détail du film.
        """
        try:
            loan = loanService.borrowSupport(idPhysicalSupport)
            flash(
                "Emprunt confirmé. Retour prévu le "
                f"{loan.expectedReturnDate.strftime('%d/%m/%Y')}.",
                "success",
            )
        except AlreadyExistsError:
            flash(
                "Ce support vient d'être emprunté. Actualisez la fiche pour "
                "voir son état.",
                "error",
            )
        except NotFoundError:
            flash("Ce support n'est plus disponible dans le catalogue.", "error")
        except InvalidReferenceError:
            flash("Seuls les supports physiques peuvent être empruntés.", "error")
        return redirect(url_for("films.getFilm", idFilm=idFilm))

    @blueprint.get("/manage")
    @_managerRequired
    def manageLoans():
        """
        Méthode qui affiche les emprunts globaux ou ceux d'un login.

        :return: Page HTML de gestion des emprunts.
        :raises ClientError: Si un appel API échoue.
        """
        searchLogin = request.args.get("login", "").strip()
        userNotFound = False
        if searchLogin:
            try:
                loans = loanService.getLoansByUserLogin(searchLogin)
            except NotFoundError:
                loans = []
                userNotFound = True
        else:
            loans = loanService.getAllLoans()

        filmTitles = loanService.getFilmTitlesByLoan(loans)
        userLogins = (
            loanService.getUserLogins(loans, session["accessToken"])
            if not searchLogin
            else {}
        )
        currentLoans, pastLoans = _splitLoans(loans)
        return render_template(
            "loans/manage.html",
            currentLoans=currentLoans,
            pastLoans=pastLoans,
            filmTitles=filmTitles,
            userLogins=userLogins,
            searchLogin=searchLogin,
            searchPerformed=bool(searchLogin),
            userNotFound=userNotFound,
        )

    @blueprint.get("/manage/<int:idLoan>")
    @_managerRequired
    def managedLoanDetail(idLoan: int):
        """
        Méthode qui affiche le détail d'un emprunt géré.

        :param idLoan: Identifiant de l'emprunt.
        :return: Page HTML du détail de l'emprunt.
        :raises ClientError: Si une ressource associée est introuvable.
        """
        loan, support, film, user = loanService.getLoanDetails(
            idLoan, session["accessToken"]
        )
        return render_template(
            "loans/detail.html",
            loan=loan,
            support=support,
            film=film,
            userLogin=user.login,
            isManagement=True,
            canReturn=not loan.isReturned,
        )

    @blueprint.post("/manage/<int:idLoan>/return")
    @_managerRequired
    def returnLoan(idLoan: int):
        """
        Méthode qui demande le retour d'un emprunt.

        :param idLoan: Identifiant de l'emprunt à retourner.
        :return: Redirection vers la gestion des emprunts.
        :raises ClientError: Si l'appel API échoue hors erreurs prises en charge.
        """
        try:
            loanService.returnLoan(idLoan)
            flash("Le retour du support a été enregistré.", "success")
        except AlreadyExistsError:
            flash("Cet emprunt a déjà été retourné.", "error")
        except NotFoundError:
            flash("Cet emprunt est introuvable.", "error")
        return redirect(url_for("loans.manageLoans"))

    return blueprint
