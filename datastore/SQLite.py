import sqlite3

from .IDatastore import IDatastore
from .model import tables


class SQLite(IDatastore):
    def __init__(self):
        self.connection = None

    async def connect(self, **kwargs):
        self.connection = sqlite3.connect(kwargs['database'])
        self.connection.row_factory = sqlite3.Row

    async def execute_query(self, query):
        if not self.is_connected():
            raise RuntimeError("Connection to SQLite database is not established.")

        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor

    async def close(self):
        if self.is_connected():
            self.connection.close()

    def is_connected(self):
        return self.connection is not None


class ConferenceDBClient(SQLite):
    def __init__(self):
        super().__init__()
        self.connection = None

    async def connect(self, **kwargs):
        self.connection = sqlite3.connect(kwargs['database'])
        self.connection.row_factory = sqlite3.Row
        if not (await self.__is_init()):
            await self.__create_database()

    async def __is_init(self):
        cursor = await self.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('Conference', 'Topic', 'Source', "
            "'ConferenceTopic', 'ConferenceSource')"
        )

        existing_tables = cursor.fetchall()
        return False if len(existing_tables) < 5 else True

    async def __create_database(self):
        # Create Conference table
        await self.execute_query('''CREATE TABLE Conference (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
                                    updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
                                    name TEXT,
                                    location TEXT,
                                    start_date DATETIME,
                                    end_date DATETIME,
                                    website TEXT,
                                    description TEXT
                                )''')

        # Create Topic table
        await self.execute_query('''CREATE TABLE Topic (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    name TEXT
                                )''')

        # Create Source table
        await self.execute_query('''CREATE TABLE Source (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
                                    updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
                                    name TEXT,
                                    cache TEXT
                                )''')

        # Create ConferenceTopic table
        await self.execute_query('''CREATE TABLE ConferenceTopic (
                                    conference_id INTEGER,
                                    topic_id INTEGER,
                                    FOREIGN KEY (conference_id) REFERENCES Conference(id) ON DELETE CASCADE,
                                    FOREIGN KEY (topic_id) REFERENCES Topic(id) ON DELETE CASCADE,
                                    PRIMARY KEY (conference_id, topic_id)
                                )''')

        # Create ConferenceSource table
        await self.execute_query('''CREATE TABLE ConferenceSource (
                                    source_url TEXT,
                                    source_id INTEGER,
                                    conference_id INTEGER,
                                    FOREIGN KEY (source_id) REFERENCES Source(id) ON DELETE CASCADE,
                                    FOREIGN KEY (conference_id) REFERENCES Conference(id) ON DELETE CASCADE,
                                    PRIMARY KEY (source_url)
                                )''')

        # Commit the changes
        self.connection.commit()

    async def finds(self, table_name, **criteria):
        query = f"SELECT * FROM {table_name} WHERE "

        for key, value in criteria.items():
            query += f'"{key}" = {'"' + value + '"'if isinstance(value, str) else value} AND '
        # Remove the trailing "AND" from the query
        query = query.rstrip("AND ")

        cursor = await self.execute_query(query)
        records = cursor.fetchall()
        items = []
        for record in records:
            item = tables[table_name](*record)
            items.append(item)

        return items

    async def update(self, table_name, _id, **update_data):
        update_statement = f"UPDATE {table_name} SET "
        update_values = []
        for key, value in update_data.items():
            update_statement += f'{key} = {'"' + value + '"' if isinstance(value, str) else value}, '
            update_values.append(value)

        update_statement = update_statement.rstrip(", ")
        update_statement += f" WHERE id = {_id}"

        cursor = await self.execute_query(update_statement)
        self.connection.commit()
        return cursor.lastrowid

    async def insert_conference(self, data):
        name = data.name
        location = data.location
        start_date = data.start_date
        end_date = data.end_date
        website = data.website
        description = data.description

        query = (
            f'INSERT INTO Conference(name, location, start_date, end_date, website, description) '
            f'VALUES ("{name}", "{location}", "{start_date}", "{end_date}", "{website}", "{description}")'
        )

        cursor = await self.execute_query(query)
        self.connection.commit()
        return cursor.lastrowid

    async def insert_source(self, data):
        name = data.name
        cache = data.cache

        query = (
            f'INSERT INTO Source(name, cache) '
            f'VALUES ("{name}", "{cache}")'
        )

        cursor = await self.execute_query(query)
        self.connection.commit()
        return cursor.lastrowid

    async def insert_conference_source(self, data):
        source_url = data.source_url
        source_id = data.source_id
        conference_id = data.conference_id

        query = (
            f'INSERT INTO ConferenceSource(source_url, source_id, conference_id) '
            f'VALUES ("{source_url}", "{source_id}", "{conference_id}")'
        )

        cursor = await self.execute_query(query)
        self.connection.commit()
        return cursor.lastrowid
