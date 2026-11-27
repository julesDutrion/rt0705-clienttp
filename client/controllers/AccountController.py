from functools import wraps
from typing import Any, Callable, Dict

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

from exceptions import AuthenticationError, InvalidRequestError, USER_INPUT_ERRORS
from services import UserService

ROLES = (
    ("consulteur", "Consulteur"),
    ("manager", "Gestionnaire"),
    ("adminstrateur", "Administrateur"),
)
ADMIN_ROLE = "adminstrateur"


def _loginRequired(function: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any):
        if not session.get("accessToken") or not session.get("user"):
            flash("Connectez-vous pour accéder à cette page.", "error")
            return redirect(url_for("account.login"))
        return function(*args, **kwargs)

    return wrapper


def _adminRequired(function: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(function)
    @_loginRequired
    def wrapper(*args: Any, **kwargs: Any):
        if session["user"].get("role") != ADMIN_ROLE:
            abort(403)
        return function(*args, **kwargs)

    return wrapper


def createAccountBlueprint(userService: UserService) -> Blueprint:
    blueprint = Blueprint("account", __name__, url_prefix="/account")

    @blueprint.route("/register", methods=["GET", "POST"])
    def register():
        values: Dict[str, str] = {}
        if request.method == "POST":
            values = request.form.to_dict()
            try:
                password = request.form.get("password", "")
                confirmPassword = request.form.get("confirmPassword", "")
                if password != confirmPassword:
                    raise InvalidRequestError(
                        "Les deux mots de passe doivent être identiques."
                    )
                userService.register(
                    request.form.get("login", ""),
                    request.form.get("email", ""),
                    password,
                    confirmPassword,
                    request.form.get("birthDate", ""),
                )
                flash("Compte créé. Vous pouvez maintenant vous connecter.", "success")
                return redirect(url_for("account.login"))
            except USER_INPUT_ERRORS as error:
                flash(str(error), "error")
        return render_template("account/register.html", values=values)

    @blueprint.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            try:
                user, accessToken = userService.login(
                    request.form.get("login", ""),
                    request.form.get("password", ""),
                )
                session.clear()
                session["accessToken"] = accessToken
                session["user"] = user.toPublicDict()
                flash(f"Bienvenue, {user.login}.", "success")
                return redirect(url_for("films.getFilms"))
            except AuthenticationError:
                flash("Identifiants incorrects.", "error")
            except USER_INPUT_ERRORS as error:
                flash(str(error), "error")
        return render_template("account/login.html")

    @blueprint.post("/logout")
    def logout():
        session.clear()
        flash("Vous êtes déconnecté.", "success")
        return redirect(url_for("films.getFilms"))

    @blueprint.route("/profile", methods=["GET", "POST"])
    @_loginRequired
    def profile():
        userId = session["user"]["idUser"]
        accessToken = session["accessToken"]
        user = userService.getUser(userId, accessToken)
        if request.method == "POST":
            payload: Dict[str, Any] = {
                "login": request.form.get("login", ""),
                "email": request.form.get("email", ""),
                "birthDate": request.form.get("birthDate", ""),
            }
            password = request.form.get("password", "")
            confirmPassword = request.form.get("confirmPassword", "")
            try:
                if password != confirmPassword:
                    raise InvalidRequestError(
                        "Les deux mots de passe doivent être identiques."
                    )
                if password:
                    payload["password"] = password
                user = userService.updateUser(userId, payload, accessToken)
                session["user"] = user.toPublicDict()
                flash("Votre compte a été modifié.", "success")
                return redirect(url_for("account.profile"))
            except USER_INPUT_ERRORS as error:
                flash(str(error), "error")
                user.login = payload["login"]
                user.email = payload["email"]
                user.birthDate = payload["birthDate"]
        return render_template("account/profile.html", user=user)

    @blueprint.get("/admin/roles")
    @_adminRequired
    def manageRoles():
        searchLogin = request.args.get("login", "").strip()
        users = userService.getAllUsers(session["accessToken"])
        if searchLogin:
            normalizedSearch = searchLogin.casefold()
            users = [
                user for user in users if normalizedSearch in user.login.casefold()
            ]
        return render_template(
            "account/roles.html",
            users=users,
            roles=ROLES,
            currentUserId=session["user"]["idUser"],
            searchLogin=searchLogin,
        )

    @blueprint.post("/admin/users/<int:idUser>/role")
    @_adminRequired
    def updateRole(idUser: int):
        role = request.form.get("role", "")
        if idUser == session["user"]["idUser"]:
            flash("Vous ne pouvez pas modifier votre propre rôle.", "error")
        elif role not in {roleValue for roleValue, _ in ROLES}:
            flash("Le rôle sélectionné est invalide.", "error")
        else:
            try:
                user = userService.updateUserRole(
                    idUser, role, session["accessToken"]
                )
                flash(f"Le rôle de {user.login} a été modifié.", "success")
            except USER_INPUT_ERRORS as error:
                flash(str(error), "error")
        return redirect(url_for("account.manageRoles"))

    @blueprint.post("/admin/users/<int:idUser>/delete")
    @_adminRequired
    def deleteUser(idUser: int):
        if idUser == session["user"]["idUser"]:
            flash("Vous ne pouvez pas supprimer votre propre compte ici.", "error")
        else:
            userService.deleteUser(idUser, session["accessToken"])
            flash("Le compte a été supprimé.", "success")
        return redirect(url_for("account.manageRoles"))

    return blueprint
