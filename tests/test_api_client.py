import requests
import pytest

from exceptions import (
    AlreadyExistsError,
    ApiError,
    ApiUnavailableError,
    AuthenticationError,
    ForbiddenError,
    InvalidReferenceError,
    InvalidRequestError,
    NotFoundError,
)
from services.ApiClient import ApiClient


class FakeResponse:
    def __init__(self, status_code=200, data=None, content=b"response"):
        self.status_code = status_code
        self.data = data
        self.content = content
        self.ok = 200 <= status_code < 400
        self.reason = "Response reason"

    def json(self):
        return self.data


def test_get_sends_bearer_token_params_and_timeout(monkeypatch):
    calls = []

    def request(_session, method, url, **kwargs):
        calls.append((method, url, kwargs))
        return FakeResponse(data={"films": []})

    monkeypatch.setattr(requests.Session, "request", request)
    client = ApiClient(
        "https://api.example/",
        timeout=2.5,
        accessTokenProvider=lambda: "session-token",
    )

    response = client.get("/films", params={"title": "Dune"})

    assert response == {"films": []}
    assert calls == [
        (
            "GET",
            "https://api.example/films",
            {
                "params": {"title": "Dune"},
                "json": None,
                "headers": {"Authorization": "Bearer session-token"},
                "timeout": 2.5,
            },
        )
    ]


@pytest.mark.parametrize(
    ("status_code", "error_type"),
    [
        (400, InvalidRequestError),
        (401, AuthenticationError),
        (403, ForbiddenError),
        (404, NotFoundError),
        (409, AlreadyExistsError),
        (422, InvalidReferenceError),
        (500, ApiError),
    ],
)
def test_http_errors_are_mapped_to_client_errors(
    monkeypatch, status_code, error_type
):
    monkeypatch.setattr(
        requests.Session,
        "request",
        lambda *_args, **_kwargs: FakeResponse(
            status_code, {"error": "API message"}
        ),
    )

    with pytest.raises(error_type, match="API message"):
        ApiClient("https://api.example").get("/resource")


def test_network_failure_becomes_api_unavailable(monkeypatch):
    def request(*_args, **_kwargs):
        raise requests.exceptions.ConnectionError("offline")

    monkeypatch.setattr(requests.Session, "request", request)

    with pytest.raises(ApiUnavailableError):
        ApiClient("https://api.example").get("/resource")


def test_empty_response_body_returns_none(monkeypatch):
    monkeypatch.setattr(
        requests.Session,
        "request",
        lambda *_args, **_kwargs: FakeResponse(content=b""),
    )

    assert ApiClient("https://api.example").delete("/resource/1") is None
