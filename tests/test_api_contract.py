from datetime import date

from services.LoanService import LoanService
from services.UserService import UserService


def user_data():
    return {
        "idUser": 12,
        "role": "consulteur",
        "login": "member",
        "email": "member@example.test",
        "birthDate": "2000-01-01",
        "age": 26,
    }


def loan_data():
    return {
        "idLoan": 5,
        "idUser": 12,
        "idPhysicalSupport": 22,
        "startDate": "2026-11-27",
        "expectedReturnDate": "2026-12-27",
        "actualReturnDate": None,
        "status": "IN_PROGRESS",
        "statusLabel": "En cours",
        "supportType": None,
    }


class RecordingApiClient:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def post(self, path, body, **kwargs):
        self.calls.append(("POST", path, body, kwargs))
        return self.response

    def get(self, path, **kwargs):
        self.calls.append(("GET", path, kwargs))
        return self.response

    def patch(self, path, body=None, **kwargs):
        self.calls.append(("PATCH", path, body, kwargs))
        return self.response


def test_registration_uses_confirmed_api_payload():
    api_client = RecordingApiClient(user_data())
    service = UserService(api_client)

    user = service.register(
        "member",
        "member@example.test",
        "password",
        "password",
        "2000-01-01",
    )

    assert user.login == "member"
    assert api_client.calls == [
        (
            "POST",
            "/users",
            {
                "login": "member",
                "email": "member@example.test",
                "password": "password",
                "confirmPassword": "password",
                "birthDate": "2000-01-01",
            },
            {},
        )
    ]


def test_admin_user_listing_passes_the_bearer_token():
    api_client = RecordingApiClient([user_data()])
    service = UserService(api_client)

    users = service.getAllUsers("admin-token")

    assert [user.login for user in users] == ["member"]
    assert api_client.calls == [
        ("GET", "/users", {"accessToken": "admin-token"})
    ]


def test_loan_search_encodes_login_and_return_uses_confirmed_patch_route():
    api_client = RecordingApiClient([loan_data()])
    service = LoanService(api_client, None, None, None)

    loans = service.getLoansByUserLogin("john doe/film")

    assert loans[0].expectedReturnDate == date(2026, 12, 27)
    assert api_client.calls == [
        ("GET", "/loans/user/john%20doe%2Ffilm", {})
    ]

    api_client.response = loan_data()
    service.returnLoan(5)

    assert api_client.calls[-1] == ("PATCH", "/loans/5/return", None, {})
