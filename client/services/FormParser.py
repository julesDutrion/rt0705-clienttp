from datetime import date
from typing import List, Optional

from werkzeug.datastructures import MultiDict

from exceptions import InvalidRequestError


class FormParser:
    """Classe qui représente le lecteur des champs de formulaire."""

    @staticmethod
    def text(form: MultiDict, key: str, label: str, required: bool = False) -> str:
        """
        Méthode qui lit une valeur textuelle de formulaire.

        :param form: Champs soumis par le formulaire.
        :param key: Nom du champ à lire.
        :param label: Libellé affiché en cas de valeur manquante.
        :param required: Indique si une valeur est obligatoire.
        :return: Valeur nettoyée.
        :raises InvalidRequestError: Si le champ obligatoire est vide.
        """
        value = (form.get(key) or "").strip()
        if required and not value:
            raise InvalidRequestError(f"Le champ « {label} » est obligatoire.")
        return value

    @staticmethod
    def requiredInteger(form: MultiDict, key: str, label: str) -> int:
        """
        Méthode qui lit un entier obligatoire de formulaire.

        :param form: Champs soumis par le formulaire.
        :param key: Nom du champ à lire.
        :param label: Libellé affiché en cas d'erreur.
        :return: Entier saisi.
        :raises InvalidRequestError: Si la valeur est absente ou invalide.
        """
        value = FormParser.optionalInteger(form, key, label)
        if value is None:
            raise InvalidRequestError(f"Le champ « {label} » est obligatoire.")
        return value

    @staticmethod
    def optionalInteger(form: MultiDict, key: str, label: str) -> Optional[int]:
        """
        Méthode qui lit un entier facultatif de formulaire.

        :param form: Champs soumis par le formulaire.
        :param key: Nom du champ à lire.
        :param label: Libellé affiché en cas d'erreur.
        :return: Entier saisi ou `None` si le champ est vide.
        :raises InvalidRequestError: Si la valeur n'est pas un entier.
        """
        raw = (form.get(key) or "").strip()
        if not raw:
            return None
        try:
            return int(raw)
        except ValueError:
            raise InvalidRequestError(f"Le champ « {label} » doit être un nombre entier.")

    @staticmethod
    def requiredDate(form: MultiDict, key: str, label: str) -> date:
        """
        Méthode qui lit une date obligatoire de formulaire.

        :param form: Champs soumis par le formulaire.
        :param key: Nom du champ à lire.
        :param label: Libellé affiché en cas d'erreur.
        :return: Date saisie.
        :raises InvalidRequestError: Si la valeur est absente ou invalide.
        """
        raw = FormParser.text(form, key, label, required=True)
        try:
            return date.fromisoformat(raw)
        except ValueError:
            raise InvalidRequestError(f"Le champ « {label} » doit être une date valide.")

    @staticmethod
    def integerList(form: MultiDict, key: str, label: str) -> List[int]:
        """
        Méthode qui lit une liste d'entiers de formulaire.

        :param form: Champs soumis par le formulaire.
        :param key: Nom des champs répétés à lire.
        :param label: Libellé affiché en cas d'erreur.
        :return: Entiers saisis sans doublons.
        :raises InvalidRequestError: Si une valeur n'est pas un entier.
        """
        values: List[int] = []
        for raw in form.getlist(key):
            try:
                values.append(int(raw))
            except ValueError:
                raise InvalidRequestError(f"Le champ « {label} » contient une valeur invalide.")
        return list(dict.fromkeys(values))  # supprime les doublons en gardant l'ordre