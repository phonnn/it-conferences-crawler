from abc import ABC, abstractmethod

from datastore import IDatabaseClient
from datastore.model import Conference


class ICrawler(ABC):
    @abstractmethod
    def get_id(self):
        pass

    @abstractmethod
    async def get_list(self) -> list[dict]:
        """Abstract method to get list conferences."""
        pass

    @abstractmethod
    async def get_details(self, data: dict) -> Conference:
        """Abstract method to extract conference details."""
        pass

    @abstractmethod
    async def check_duplicate(self, data: dict, db_client: IDatabaseClient) -> bool:
        """Abstract method to check duplicate conference from database."""
        pass

    @abstractmethod
    async def save_cache(self, db_client: IDatabaseClient):
        """Abstract method to save cache."""
        pass
