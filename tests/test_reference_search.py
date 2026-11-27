import requests

from app import createApp


class FakeResponse:
    def __init__(self, status_code, data):
        self.status_code = status_code
        self.data = data
        self.ok = 200 <= status_code < 400
        self.content = b"response"
        self.reason = "Response reason"

    def json(self):
        return self.data


def test_empty_actor_search_returns_no_results_without_api_call(monkeypatch):
    app = createApp()
    app.config.update(TESTING=True, SECRET_KEY="test")
    client = app.test_client()
    api_calls = []

    def request(*args, **kwargs):
        api_calls.append((args, kwargs))
        raise AssertionError("An empty query must not call the API.")

    monkeypatch.setattr(requests.Session, "request", request)

    response = client.get("/actors/search")

    assert response.status_code == 200
    assert response.json == []
    assert api_calls == []


def test_actor_search_maps_api_results_for_the_selector(monkeypatch):
    app = createApp()
    app.config.update(TESTING=True, SECRET_KEY="test")
    client = app.test_client()
    calls = []

    def request(_session, method, url, **kwargs):
        calls.append((method, url, kwargs))
        return FakeResponse(
            200,
            [{"idActor": 4, "firstName": "Ava", "lastName": "DuVernay"}],
        )

    monkeypatch.setattr(requests.Session, "request", request)

    response = client.get("/actors/search?q=Ava")

    assert response.status_code == 200
    assert response.json == [{"id": 4, "label": "Ava DuVernay"}]
    assert len(calls) == 1
    method, url, kwargs = calls[0]
    assert method == "GET"
    assert url.endswith("/actors")
    assert kwargs == {
        "params": {"name": "Ava"},
        "json": None,
        "headers": None,
        "timeout": 5.0,
    }


def test_actor_search_api_failure_returns_generic_error_page(monkeypatch):
    app = createApp()
    app.config.update(TESTING=True, SECRET_KEY="test")
    client = app.test_client()

    def request(*_args, **_kwargs):
        raise requests.exceptions.ConnectionError("private connection detail")

    monkeypatch.setattr(requests.Session, "request", request)

    response = client.get("/actors/search?q=Ava")

    assert response.status_code == 503
    assert "momentanément indisponible".encode() in response.data
    assert b"private connection detail" not in response.data
