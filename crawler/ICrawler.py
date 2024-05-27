from abc import ABC, abstractmethod

from datastore import IDatabaseClient
from datastore.model import Conference, Topic

ConferenceDetails = {
    'conference': Conference,
    'topics': list[Topic]
}


class ICrawler(ABC):
    @abstractmethod
    def get_id(self):
        pass

    @abstractmethod
    def get_cache(self) -> dict:
        pass

    @abstractmethod
    async def get_list(self) -> list[dict]:
        """Abstract method to get list conferences."""
        pass

    @abstractmethod
    async def get_details(self, data: dict) -> ConferenceDetails:
        """Abstract method to extract conference details."""
        pass
