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
        if not session.get("accessToken") or not session.get("user"):
            flash("Connectez-vous pour accéder à cette page.", "error")
            return redirect(url_for("account.login"))
        return function(*args, **kwargs)

    return wrapper


def _managerRequired(function: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(function)
    @_loginRequired
    def wrapper(*args: Any, **kwargs: Any):
        if session["user"].get("role") not in MANAGER_ROLES:
            abort(403)
        return function(*args, **kwargs)

    return wrapper


def _splitLoans(loans: List[LoanDTO]) -> Tuple[List[LoanDTO], List[LoanDTO]]:
    currentLoans = [loan for loan in loans if not loan.isReturned]
    pastLoans = [loan for loan in loans if loan.isReturned]
    return currentLoans, pastLoans


def createLoanBlueprint(loanService: LoanService) -> Blueprint:
    blueprint = Blueprint("loans", __name__, url_prefix="/loans")

    @blueprint.get("")
    @_loginRequired
    def myLoans():
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
        try:
            loanService.returnLoan(idLoan)
            flash("Le retour du support a été enregistré.", "success")
        except AlreadyExistsError:
            flash("Cet emprunt a déjà été retourné.", "error")
        except NotFoundError:
            flash("Cet emprunt est introuvable.", "error")
        return redirect(url_for("loans.manageLoans"))

    return blueprint
