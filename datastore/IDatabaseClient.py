from abc import ABC, abstractmethod
from .model import Conference, Source, Topic, ConferenceTopic


class IDatabaseClient(ABC):
    @abstractmethod
    async def finds(self, table_name, **criteria):
        """
        Find Items based on provided table and criteria.

        :param table_name: Name of table to find
        :param criteria: Criteria to search for Items
        :return: List of Items matching the criteria
        """
        pass

    @abstractmethod
    async def update(self, table_name, _id, **update_data):
        """
        Update a record in the database.

        :param table_name: Name of table need to update
        :param _id: Record id
        :param update_data: Data of the Item to update
        :return: ID of the update Item
        """
        pass

    @abstractmethod
    async def insert_conference(self, data: Conference):
        """
        Insert a new Conference record into the database.

        :param data: Data of the Conference to insert
        :return: ID of the inserted Conference
        """
        pass

    @abstractmethod
    async def insert_source(self, data: Source):
        """
        Insert a new Source record into the database.

        :param data: Data of the Source to insert
        :return: ID of the inserted Source
        """
        pass

    @abstractmethod
    async def insert_topic(self, data: Topic):
        """
        Insert a new Topic record into the database.

        :param data: Data of the Topic to insert
        :return: ID of the inserted Topic
        """
        pass

    @abstractmethod
    async def insert_conference_topic(self, data: ConferenceTopic):
        """
        Insert a new ConferenceTopic record into the database.

        :param data: Data of the ConferenceTopic to insert
        :return: ID of the inserted ConferenceTopic
        """
        pass