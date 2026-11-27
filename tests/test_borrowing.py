from datetime import date

import pytest
import requests
from flask import Flask

from app import createApp
from controllers.LoanController import createLoanBlueprint
from exceptions import AlreadyExistsError
from models import LoanDTO
from services.LoanService import LoanService


def loan_data(
    id_loan=3,
    id_support=22,
    expected_return_date="2026-12-27T00:00:00Z",
):
    return {
        "idLoan": id_loan,
        "idUser": 9,
        "idPhysicalSupport": id_support,
        "startDate": "2026-11-27T00:00:00Z",
        "expectedReturnDate": expected_return_date,
        "actualReturnDate": None,
        "status": "IN_PROGRESS",
        "statusLabel": "En cours",
        "supportType": None,
    }


class FakeApiClient:
    def __init__(self, response):
        self.response = response
        self.posts = []

    def post(self, path, body):
        self.posts.append((path, body))
        return self.response


class FakeSupportLookup:
    def __init__(self, film_by_support):
        self.film_by_support = film_by_support
        self.lookups = []

    def getSupportById(self, id_support):
        self.lookups.append(id_support)
        return type(
            "Support",
            (),
            {"idFilm": self.film_by_support[id_support]},
        )()


class FakeFilmLookup:
    def __init__(self, titles):
        self.titles = titles
        self.lookups = []

    def getFilmTitleById(self, id_film):
        self.lookups.append(id_film)
        return self.titles[id_film]


def test_borrow_posts_only_the_physical_support_id():
    api_client = FakeApiClient(loan_data())
    service = LoanService(api_client, None, None, None)

    loan = service.borrowSupport(22)

    assert api_client.posts == [("/loans", {"idPhysicalSupport": 22})]
    assert loan.expectedReturnDate == date(2026, 12, 27)


def test_loan_titles_are_resolved_once_per_support_and_film():
    support_service = FakeSupportLookup({22: "film-1", 23: "film-1"})
    film_service = FakeFilmLookup({"film-1": "Film test"})
    service = LoanService(None, support_service, film_service, None)
    loans = [
        LoanDTO.fromDict(loan_data(id_loan, id_support))
        for id_loan, id_support in ((3, 22), (4, 22), (5, 23))
    ]

    titles = service.getFilmTitlesByLoan(loans)

    assert titles == {3: "Film test", 4: "Film test", 5: "Film test"}
    assert support_service.lookups == [22, 23]
    assert film_service.lookups == ["film-1"]


class FakeBorrowService:
    def __init__(self):
        self.support_ids = []
        self.error = None

    def borrowSupport(self, id_physical_support):
        self.support_ids.append(id_physical_support)
        if self.error:
            raise self.error
        return LoanDTO.fromDict(loan_data())


class FakeResponse:
    ok = True
    content = b"response"

    def __init__(self, data):
        self.data = data

    def json(self):
        return self.data


@pytest.fixture
def borrowing_client():
    service = FakeBorrowService()
    app = Flask(__name__)
    app.config.update(TESTING=True, SECRET_KEY="test")
    app.add_url_rule("/login", endpoint="account.login", view_func=lambda: "")
    app.add_url_rule(
        "/films/<string:idFilm>",
        endpoint="films.getFilm",
        view_func=lambda idFilm: "",
    )
    app.register_blueprint(createLoanBlueprint(service))
    return app.test_client(), service


def test_borrow_requires_login_and_redirects_after_success(borrowing_client):
    client, service = borrowing_client

    response = client.post("/loans/support/22/borrow/film-1")

    assert response.status_code == 302
    assert response.location == "/login"
    with client.session_transaction() as session:
        session["accessToken"] = "token"
        session["user"] = {
            "idUser": 9,
            "login": "member",
            "role": "consulteur",
        }

    response = client.post("/loans/support/22/borrow/film-1")

    assert response.status_code == 302
    assert response.location == "/films/film-1"
    assert service.support_ids == [22]
    with client.session_transaction() as session:
        assert session["_flashes"][-1][0] == "success"
        assert "27/12/2026" in session["_flashes"][-1][1]


def test_api_conflict_is_reported_without_claiming_success(borrowing_client):
    client, service = borrowing_client
    service.error = AlreadyExistsError()
    with client.session_transaction() as session:
        session["accessToken"] = "token"
        session["user"] = {
            "idUser": 9,
            "login": "member",
            "role": "consulteur",
        }

    response = client.post("/loans/support/22/borrow/film-1")

    assert response.status_code == 302
    with client.session_transaction() as session:
        assert session["_flashes"][0][0] == "error"
        assert "vient d'être emprunté" in session["_flashes"][0][1]


@pytest.fixture
def availability_app():
    app = createApp()
    app.config.update(TESTING=True, SECRET_KEY="test")
    client = app.test_client()
    film = {
        "idFilm": "film-1",
        "title": "Film test",
        "synopsis": "",
        "releaseDate": "2020-01-01",
        "duration": 100,
        "posterUrl": "",
        "addedDate": "2020-01-02",
    }
    supports = [
        {
            "idFilm": "film-1",
            "idSupport": 21,
            "idSupportType": 1,
            "location": "Rayon A",
            "url": None,
            "supportType": {
                "idSupportType": 1,
                "name": "DVD",
                "mode": "physical",
            },
            "isAvailable": True,
        },
        {
            "idFilm": "film-1",
            "idSupport": 22,
            "idSupportType": 1,
            "location": "Rayon B",
            "url": None,
            "supportType": {
                "idSupportType": 1,
                "name": "DVD",
                "mode": "physical",
            },
            "isAvailable": False,
        },
    ]
    loans = [loan_data()]

    def request(_session, _method, url, **_kwargs):
        if url.endswith("/films/film-1"):
            return FakeResponse(film)
        if url.endswith("/supports/film/film-1"):
            return FakeResponse(supports)
        if url.endswith("/loans/me") or url.endswith("/loans"):
            return FakeResponse(loans)
        raise AssertionError(f"Unexpected API request: {url}")

    return app, client, request, loans


def login_as(client, role):
    with client.session_transaction() as session:
        session["accessToken"] = "token"
        session["user"] = {
            "idUser": 9,
            "login": "member",
            "role": role,
        }


def test_member_sees_availability_and_own_expected_return_date(
    availability_app, monkeypatch
):
    _app, client, request, _loans = availability_app
    login_as(client, "consulteur")
    monkeypatch.setattr(requests.Session, "request", request)

    response = client.get("/films/film-1")

    assert response.status_code == 200
    assert b"Disponible" in response.data
    assert b"Emprunter ce support" in response.data
    assert b"Emprunt\xc3\xa9" in response.data
    assert b"27/12/2026" in response.data


def test_manager_can_see_expected_date_for_another_users_loan(
    availability_app, monkeypatch
):
    _app, client, request, _loans = availability_app
    login_as(client, "manager")
    monkeypatch.setattr(requests.Session, "request", request)

    response = client.get("/films/film-1")

    assert response.status_code == 200
    assert b"27/12/2026" in response.data


def test_standard_user_does_not_get_another_users_due_date(
    availability_app, monkeypatch
):
    _app, client, request, loans = availability_app
    login_as(client, "consulteur")
    loans.clear()
    monkeypatch.setattr(requests.Session, "request", request)

    response = client.get("/films/film-1")

    assert response.status_code == 200
    assert b"Date de retour pr\xc3\xa9vue non disponible." in response.data
    assert b"27/12/2026" not in response.data
