from abc import ABC, abstractmethod


class IDatastore(ABC):
    @abstractmethod
    async def connect(self, **kwargs):
        """
        Connect to the database.

        :param kwargs: Connection parameters
        """
        pass

    @abstractmethod
    async def execute_query(self, query):
        """
        Execute a query on the database.

        :param query: Query to execute
        :return: Query result
        """
        pass

    @abstractmethod
    async def close(self):
        """
        Close the connection to the database.
        """
        pass

    @abstractmethod
    def is_connected(self):
        """
        Check if the adapter is currently connected to the database.

        :return: True if connected, False otherwise
        """
        pass
