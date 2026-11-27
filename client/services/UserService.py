from typing import Any, Dict, List, Tuple

from models import UserDTO

from .ApiClient import ApiClient


class UserService:
    """Classe qui représente le service de gestion des utilisateurs."""

    def __init__(self, apiClient: ApiClient) -> None:
        self._apiClient = apiClient

    def login(self, login: str, password: str) -> Tuple[UserDTO, str]:
        """
        Méthode qui authentifie un utilisateur.

        :param login: Login de l'utilisateur.
        :param password: Mot de passe de l'utilisateur.
        :return: Utilisateur authentifié et jeton JWT.
        :raises ClientError: Si les identifiants sont rejetés ou l'API échoue.
        """
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
        """
        Méthode qui crée un compte utilisateur.

        :param login: Login du compte.
        :param email: Adresse e-mail du compte.
        :param password: Mot de passe choisi.
        :param confirmPassword: Confirmation du mot de passe.
        :param birthDate: Date de naissance au format ISO.
        :return: Compte créé.
        :raises ClientError: Si les données ou l'appel API sont invalides.
        """
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
        """
        Méthode qui récupère la liste des utilisateurs.

        :param accessToken: Jeton JWT de l'administrateur.
        :return: Liste des utilisateurs.
        :raises ClientError: Si l'appel API échoue.
        """
        data = self._apiClient.get("/users", accessToken=accessToken)
        return [UserDTO.fromDict(user) for user in data]

    def getUser(self, idUser: int, accessToken: str) -> UserDTO:
        """
        Méthode qui récupère un utilisateur par identifiant.

        :param idUser: Identifiant de l'utilisateur.
        :param accessToken: Jeton JWT de l'utilisateur autorisé.
        :return: Utilisateur correspondant.
        :raises ClientError: Si l'appel API échoue.
        """
        data = self._apiClient.get(f"/users/{idUser}", accessToken=accessToken)
        return UserDTO.fromDict(data)

    def updateUser(
        self, idUser: int, payload: Dict[str, Any], accessToken: str
    ) -> UserDTO:
        """
        Méthode qui modifie les informations d'un utilisateur.

        :param idUser: Identifiant de l'utilisateur à modifier.
        :param payload: Informations à transmettre à l'API.
        :param accessToken: Jeton JWT de l'utilisateur autorisé.
        :return: Utilisateur modifié.
        :raises ClientError: Si l'appel API échoue.
        """
        data = self._apiClient.put(
            f"/users/{idUser}", payload, accessToken=accessToken
        )
        return UserDTO.fromDict(data)

    def updateUserRole(
        self, idUser: int, role: str, accessToken: str
    ) -> UserDTO:
        """
        Méthode qui modifie le rôle d'un utilisateur.

        :param idUser: Identifiant de l'utilisateur concerné.
        :param role: Nouveau rôle.
        :param accessToken: Jeton JWT de l'administrateur.
        :return: Utilisateur modifié.
        :raises ClientError: Si l'appel API échoue.
        """
        data = self._apiClient.put(
            f"/users/{idUser}/role", {"role": role}, accessToken=accessToken
        )
        return UserDTO.fromDict(data)

    def deleteUser(self, idUser: int, accessToken: str) -> None:
        """
        Méthode qui supprime un utilisateur.

        :param idUser: Identifiant de l'utilisateur.
        :param accessToken: Jeton JWT de l'administrateur.
        :raises ClientError: Si l'appel API échoue.
        """
        self._apiClient.delete(f"/users/{idUser}", accessToken=accessToken)
