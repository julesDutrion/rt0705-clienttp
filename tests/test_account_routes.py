import requests

from app import createApp


class FakeResponse:
    def __init__(self, status_code, data):
        self.status_code = status_code
        self.data = data
        self.ok = 200 <= status_code < 400
        self.content = b"response"
        self.reason = "Unauthorized"

    def json(self):
        return self.data


def make_app_client():
    app = createApp()
    app.config.update(TESTING=True, SECRET_KEY="test")
    return app.test_client()


def test_registration_rejects_mismatched_passwords_without_api_call(monkeypatch):
    client = make_app_client()
    api_calls = []

    def request(*args, **kwargs):
        api_calls.append((args, kwargs))
        raise AssertionError("The API must not be called for invalid passwords.")

    monkeypatch.setattr(requests.Session, "request", request)

    response = client.post(
        "/account/register",
        data={
            "login": "member",
            "email": "member@example.test",
            "password": "first-password",
            "confirmPassword": "different-password",
            "birthDate": "2000-01-01",
        },
    )

    assert response.status_code == 200
    assert "Les deux mots de passe doivent être identiques.".encode() in response.data
    assert api_calls == []


def test_invalid_credentials_show_a_safe_error(monkeypatch):
    client = make_app_client()

    def request(_session, _method, _url, **_kwargs):
        return FakeResponse(401, {"error": "sensitive API detail"})

    monkeypatch.setattr(requests.Session, "request", request)

    response = client.post(
        "/account/login",
        data={"login": "member", "password": "wrong"},
    )

    assert response.status_code == 200
    assert "Identifiants incorrects.".encode() in response.data
    assert b"sensitive API detail" not in response.data


def test_guest_is_redirected_from_personal_loans():
    client = make_app_client()

    response = client.get("/loans")

    assert response.status_code == 302
    assert response.location.endswith("/account/login")


def test_standard_user_cannot_access_admin_or_global_loan_pages():
    client = make_app_client()
    with client.session_transaction() as session:
        session["accessToken"] = "token"
        session["user"] = {
            "idUser": 9,
            "login": "member",
            "role": "consulteur",
        }

    roles_response = client.get("/account/admin/roles")
    loans_response = client.get("/loans/manage")

    assert roles_response.status_code == 403
    assert loans_response.status_code == 403


def test_manager_can_open_global_loan_page(monkeypatch):
    client = make_app_client()
    with client.session_transaction() as session:
        session["accessToken"] = "token"
        session["user"] = {
            "idUser": 3,
            "login": "manager",
            "role": "manager",
        }

    monkeypatch.setattr(
        requests.Session,
        "request",
        lambda *_args, **_kwargs: FakeResponse(200, []),
    )

    response = client.get("/loans/manage")

    assert response.status_code == 200
    assert "Gestion des emprunts".encode() in response.data
