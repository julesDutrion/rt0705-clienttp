from typing import Any, Dict, List, Tuple

from models import UserDTO

from .ApiClient import ApiClient


class UserService:
    def __init__(self, apiClient: ApiClient) -> None:
        self._apiClient = apiClient

    def login(self, login: str, password: str) -> Tuple[UserDTO, str]:
        data = self._apiClient.post(
            "/auth/login", {"login": login, "password": password}
        )
        return UserDTO.fromDict(data["user"]), data["accessToken"]

    def register(
        self,
        login: str,
        email: str,
        password: str,
        confirmPassword: str,
        birthDate: str,
    ) -> UserDTO:
        data = self._apiClient.post(
            "/users",
            {
                "login": login,
                "email": email,
                "password": password,
                "confirmPassword": confirmPassword,
                "birthDate": birthDate,
            },
        )
        return UserDTO.fromDict(data)

    def getAllUsers(self, accessToken: str) -> List[UserDTO]:
        data = self._apiClient.get("/users", accessToken=accessToken)
        return [UserDTO.fromDict(user) for user in data]

    def getUser(self, idUser: int, accessToken: str) -> UserDTO:
        data = self._apiClient.get(f"/users/{idUser}", accessToken=accessToken)
        return UserDTO.fromDict(data)

    def updateUser(
        self, idUser: int, payload: Dict[str, Any], accessToken: str
    ) -> UserDTO:
        data = self._apiClient.put(
            f"/users/{idUser}", payload, accessToken=accessToken
        )
        return UserDTO.fromDict(data)

    def updateUserRole(
        self, idUser: int, role: str, accessToken: str
    ) -> UserDTO:
        data = self._apiClient.put(
            f"/users/{idUser}/role", {"role": role}, accessToken=accessToken
        )
        return UserDTO.fromDict(data)

    def deleteUser(self, idUser: int, accessToken: str) -> None:
        self._apiClient.delete(f"/users/{idUser}", accessToken=accessToken)
