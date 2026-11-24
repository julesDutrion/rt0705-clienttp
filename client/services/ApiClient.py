from typing import Any, Dict, Optional

import requests

from exceptions import (
    AlreadyExistsError,
    ApiError,
    ApiUnavailableError,
    ClientError,
    InvalidReferenceError,
    InvalidRequestError,
    NotFoundError,
)

# Codes HTTP de l'API -> exceptions du client
_STATUS_TO_ERROR: Dict[int, type] = {
    400: InvalidRequestError,
    404: NotFoundError,
    409: AlreadyExistsError,
    422: InvalidReferenceError,
}


class ApiClient:
    """Transport HTTP vers l'API : seul endroit qui connaît `requests` et les codes de retour."""

    def __init__(self, baseUrl: str, timeout: float = 5.0) -> None:
        self._baseUrl = baseUrl.rstrip("/")
        self._timeout = timeout
        self._session = requests.Session()

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request("GET", path, params=params)

    def post(self, path: str, body: Dict[str, Any]) -> Any:
        return self._request("POST", path, body=body)

    def put(self, path: str, body: Dict[str, Any]) -> Any:
        return self._request("PUT", path, body=body)

    def delete(self, path: str) -> Any:
        return self._request("DELETE", path)

    # ------------------------------------------------------------------ #
    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
    ) -> Any:
        try:
            response = self._session.request(
                method,
                f"{self._baseUrl}{path}",
                params=params,
                json=body,
                timeout=self._timeout,
            )
        except requests.exceptions.RequestException as error:
            raise ApiUnavailableError(f"API unreachable at {self._baseUrl}") from error

        if not response.ok:
            raise self._toError(response)
        return response.json() if response.content else None

    @staticmethod
    def _toError(response: requests.Response) -> ClientError:
        try:
            message = response.json().get("error", response.reason)
        except (ValueError, AttributeError):
            message = response.reason or "Unknown error"
        errorClass = _STATUS_TO_ERROR.get(response.status_code)
        if errorClass is None:
            return ApiError(f"API error {response.status_code}: {message}")
        return errorClass(message)