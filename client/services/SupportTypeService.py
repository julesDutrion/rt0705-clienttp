from typing import List

from models import SupportTypeDTO

from .ApiClient import ApiClient


class SupportTypeService:
    def __init__(self, apiClient: ApiClient) -> None:
        self._apiClient = apiClient

    def getAllSupportTypes(self) -> List[SupportTypeDTO]:
        data = self._apiClient.get("/support-types")
        return [SupportTypeDTO.fromDict(item) for item in data]
