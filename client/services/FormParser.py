from datetime import date
from typing import List, Optional

from werkzeug.datastructures import MultiDict

from exceptions import InvalidRequestError


class FormParser:
    """Lecture et validation des champs d'un formulaire HTML (les valeurs arrivent en texte)."""

    @staticmethod
    def text(form: MultiDict, key: str, label: str, required: bool = False) -> str:
        value = (form.get(key) or "").strip()
        if required and not value:
            raise InvalidRequestError(f"Le champ « {label} » est obligatoire.")
        return value

    @staticmethod
    def requiredInteger(form: MultiDict, key: str, label: str) -> int:
        value = FormParser.optionalInteger(form, key, label)
        if value is None:
            raise InvalidRequestError(f"Le champ « {label} » est obligatoire.")
        return value

    @staticmethod
    def optionalInteger(form: MultiDict, key: str, label: str) -> Optional[int]:
        raw = (form.get(key) or "").strip()
        if not raw:
            return None
        try:
            return int(raw)
        except ValueError:
            raise InvalidRequestError(f"Le champ « {label} » doit être un nombre entier.")

    @staticmethod
    def requiredDate(form: MultiDict, key: str, label: str) -> date:
        raw = FormParser.text(form, key, label, required=True)
        try:
            return date.fromisoformat(raw)
        except ValueError:
            raise InvalidRequestError(f"Le champ « {label} » doit être une date valide.")

    @staticmethod
    def integerList(form: MultiDict, key: str, label: str) -> List[int]:
        values: List[int] = []
        for raw in form.getlist(key):
            try:
                values.append(int(raw))
            except ValueError:
                raise InvalidRequestError(f"Le champ « {label} » contient une valeur invalide.")
        return list(dict.fromkeys(values))  # supprime les doublons en gardant l'ordre