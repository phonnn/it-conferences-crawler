import logging
from asyncio import Queue
from typing import Callable

from crawler import ICrawler, ACMCrawler, ConferenceIndexCrawler
from datastore import IDatabaseClient
from datastore.model import Conference, Source, Topic, ConferenceTopic

logger = logging.getLogger(__name__)

crawler_names = {
    'ACM': ACMCrawler,
    'CI': ConferenceIndexCrawler
}


class CrawlerFactory:
    crawlers: dict[str, ICrawler] = {}

    def __init__(self, data_client: IDatabaseClient, queue: Queue):
        self.data_client = data_client
        self.detail_queue = queue

    async def add_crawler(self, name):
        # add crawler info to db if not exist
        sources = await self.data_client.finds('Source', name=name)
        if len(sources) == 0:
            source = Source('', '', '', name, '')
            record_id = await self.data_client.insert_source(source)
            source.id = record_id
        else:
            source = sources[0]

        self.crawlers[name] = crawler_names[name](source.id, source.cache)

    async def process_list(self, crawler_name, callback):
        try:
            conferences = await self.crawlers[crawler_name].get_list()
            logger.info(f'Fetched {len(conferences)} conference(s) from {crawler_name}')

            for conference in conferences:
                await self.detail_queue.put({'key': crawler_name, 'data': conference})

        except:
            logger.exception(f'Got exception from crawler: {crawler_name} list')

        if isinstance(callback, Callable):
            await callback(crawler_name)

    async def process_detail(self, crawler_name, data):
        try:
            detail = await self.crawlers[crawler_name].get_details(data)
            await self.save(crawler_name, detail)

            # maybe logic for update here
            await self._save_cache(crawler_name)
        except:
            logger.exception(f'Got exception from crawler: {crawler_name} detail')

    async def save(self, crawler_name, detail):
        conference = detail['conference']
        topics = detail['topics']

        is_duplicate = await self._check_duplicate_conference(conference)
        if not is_duplicate:
            conference_id = await self._save_conference(crawler_name, conference)
            await self._save_topic(conference_id, topics)
            logger.info(f'Add new conference from {crawler_name}: {conference.name}')

    async def _check_duplicate_conference(self, conference: Conference):
        if not isinstance(conference, Conference):
            raise TypeError(f'Expecting a Conference but getting an {type(conference)}')

        if conference.website == '':
            raise ValueError(f"Conference's website is empty")

        duplicates = await self.data_client.finds('Conference', website=conference.website)
        if len(duplicates) > 0:
            return True

        return False

    async def _save_cache(self, crawler_name):
        _id = self.crawlers[crawler_name].get_id()
        cache = self.crawlers[crawler_name].get_cache()
        await self.data_client.update('Source', _id, **{'cache': cache})

    async def _save_conference(self, crawler_name, conference):
        conference_id = await self.data_client.insert_conference(conference)
        return conference_id

    async def _save_topic(self, conference_id: int, topics: list[Topic]):
        conference_topic = []
        for topic in topics:
            if not isinstance(topic, Topic):
                raise TypeError(f'Expecting a Topic but getting an {type(topic)}')

            if topic.name == '':
                raise ValueError(f"Topic's name is empty")

            topic_id = await self.data_client.insert_topic(topic)
            conference_topic.append(ConferenceTopic(conference_id, topic_id))

        for item in conference_topic:
            await self.data_client.insert_conference_topic(item)
