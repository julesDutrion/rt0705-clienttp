import unittest
from datetime import date
from unittest.mock import patch

import requests
from flask import Flask

from app import createApp
from controllers.LoanController import createLoanBlueprint
from exceptions import AlreadyExistsError
from models import LoanDTO
from services.LoanService import LoanService


def loanData(expectedReturnDate="2026-12-27T00:00:00Z"):
    return {
        "idLoan": 3,
        "idUser": 9,
        "idPhysicalSupport": 22,
        "startDate": "2026-11-27T00:00:00Z",
        "expectedReturnDate": expectedReturnDate,
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


class BorrowingServiceTests(unittest.TestCase):
    def test_borrow_posts_only_the_physical_support_id(self):
        apiClient = FakeApiClient(loanData())
        service = LoanService(apiClient, None, None, None)

        loan = service.borrowSupport(22)

        self.assertEqual(apiClient.posts, [("/loans", {"idPhysicalSupport": 22})])
        self.assertEqual(loan.expectedReturnDate, date(2026, 12, 27))


class FakeSupportLookup:
    def __init__(self, filmBySupport):
        self.filmBySupport = filmBySupport
        self.lookups = []

    def getSupportById(self, idSupport):
        self.lookups.append(idSupport)
        return type("Support", (), {"idFilm": self.filmBySupport[idSupport]})()


class FakeFilmLookup:
    def __init__(self, titles):
        self.titles = titles
        self.lookups = []

    def getFilmTitleById(self, idFilm):
        self.lookups.append(idFilm)
        return self.titles[idFilm]


class LoanTitleTests(unittest.TestCase):
    def test_titles_are_resolved_by_support_and_reused_for_repeated_films(self):
        supportService = FakeSupportLookup({22: "film-1", 23: "film-1"})
        filmService = FakeFilmLookup({"film-1": "Film test"})
        service = LoanService(None, supportService, filmService, None)

        loans = []
        for idLoan, idSupport in ((3, 22), (4, 22), (5, 23)):
            data = loanData()
            data.update(idLoan=idLoan, idPhysicalSupport=idSupport)
            loans.append(LoanDTO.fromDict(data))

        titles = service.getFilmTitlesByLoan(loans)

        self.assertEqual(titles, {3: "Film test", 4: "Film test", 5: "Film test"})
        self.assertEqual(supportService.lookups, [22, 23])
        self.assertEqual(filmService.lookups, ["film-1"])


class FakeBorrowService:
    def __init__(self):
        self.supportIds = []
        self.error = None

    def borrowSupport(self, idPhysicalSupport):
        self.supportIds.append(idPhysicalSupport)
        if self.error:
            raise self.error
        return LoanDTO.fromDict(loanData())


class BorrowingRouteTests(unittest.TestCase):
    def setUp(self):
        self.service = FakeBorrowService()
        app = Flask(__name__)
        app.secret_key = "test"
        app.add_url_rule("/login", endpoint="account.login", view_func=lambda: "")
        app.add_url_rule(
            "/films/<string:idFilm>",
            endpoint="films.getFilm",
            view_func=lambda idFilm: "",
        )
        app.register_blueprint(createLoanBlueprint(self.service))
        self.client = app.test_client()

    def test_borrow_requires_login_and_redirects_to_film_after_success(self):
        response = self.client.post("/loans/support/22/borrow/film-1")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "/login")

        with self.client.session_transaction() as session:
            session.pop("_flashes", None)
            session["accessToken"] = "token"
            session["user"] = {
                "idUser": 9,
                "login": "member",
                "role": "consulteur",
            }
        response = self.client.post("/loans/support/22/borrow/film-1")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "/films/film-1")
        self.assertEqual(self.service.supportIds, [22])
        with self.client.session_transaction() as session:
            self.assertEqual(session["_flashes"][0][0], "success")
            self.assertIn("27/12/2026", session["_flashes"][0][1])

    def test_api_conflict_is_reported_without_claiming_success(self):
        with self.client.session_transaction() as session:
            session["accessToken"] = "token"
            session["user"] = {
                "idUser": 9,
                "login": "member",
                "role": "consulteur",
            }
        self.service.error = AlreadyExistsError()

        response = self.client.post("/loans/support/22/borrow/film-1")

        self.assertEqual(response.status_code, 302)
        with self.client.session_transaction() as session:
            self.assertEqual(session["_flashes"][0][0], "error")
            self.assertIn("vient d'être emprunté", session["_flashes"][0][1])


class FakeResponse:
    ok = True
    content = b"response"

    def __init__(self, data):
        self.data = data

    def json(self):
        return self.data


class FilmAvailabilityTests(unittest.TestCase):
    def setUp(self):
        self.app = createApp()
        self.client = self.app.test_client()
        self.film = {
            "idFilm": "film-1",
            "title": "Film test",
            "synopsis": "",
            "releaseDate": "2020-01-01",
            "duration": 100,
            "posterUrl": "",
            "addedDate": "2020-01-02",
        }
        self.supports = [
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
        self.myLoans = [loanData()]
        self.allLoans = [loanData()]

    def fakeRequest(self, _method, url, **_kwargs):
        if url.endswith("/films/film-1"):
            return FakeResponse(self.film)
        if url.endswith("/supports/film/film-1"):
            return FakeResponse(self.supports)
        if url.endswith("/loans/me"):
            return FakeResponse(self.myLoans)
        if url.endswith("/loans"):
            return FakeResponse(self.allLoans)
        self.fail(f"Unexpected API request: {url}")

    def loginAs(self, role):
        with self.client.session_transaction() as session:
            session["accessToken"] = "token"
            session["user"] = {
                "idUser": 9,
                "login": "member",
                "role": role,
            }

    def test_member_sees_availability_and_own_expected_return_date(self):
        self.loginAs("consulteur")

        with patch.object(requests.Session, "request", self.fakeRequest):
            response = self.client.get("/films/film-1")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Disponible", response.data)
        self.assertIn(b"Emprunter ce support", response.data)
        self.assertIn(b"Emprunt\xc3\xa9", response.data)
        self.assertIn(b"27/12/2026", response.data)

    def test_manager_can_see_expected_date_for_another_users_loan(self):
        self.loginAs("manager")

        with patch.object(requests.Session, "request", self.fakeRequest):
            response = self.client.get("/films/film-1")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"27/12/2026", response.data)

    def test_standard_user_does_not_get_another_users_due_date(self):
        self.loginAs("consulteur")
        self.myLoans = []

        with patch.object(requests.Session, "request", self.fakeRequest):
            response = self.client.get("/films/film-1")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Date de retour pr\xc3\xa9vue non disponible.", response.data)
        self.assertNotIn(b"27/12/2026", response.data)
