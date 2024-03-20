import logging
from asyncio import Queue
from typing import Callable

from crawler.ICrawler import ICrawler
from crawler.ACMCrawler import ACMCrawler
from datastore.IDatabaseClient import IDatabaseClient
from model.ConferenceSource import ConferenceSource
from model.Source import Source

logger = logging.getLogger(__name__)

crawler_names = {
    'ACM': ACMCrawler
}


class CrawlerFactory:
    crawlers: dict[str, ICrawler] = {}
    callback: Callable = None

    def __init__(self, data_client: IDatabaseClient, queue: Queue):
        self.data_client = data_client
        self.detail_queue = queue

    async def add_crawler(self, name):
        # add crawler info to db if not exist
        sources = await self.data_client.finds('Source', name=name)
        if len(sources) == 0:
            source = Source('', name, '')
            record_id = await self.data_client.insert_source(source)
            source.id = record_id
        else:
            source = sources[0]

        self.crawlers[name] = crawler_names[name](source.id, source.cache)

    async def crawl(self, callback):
        if isinstance(callback, Callable):
            self.callback = callback
            for name in self.crawlers.keys():
                await callback(name)

    async def process_list(self, crawler_name):
        try:
            conferences = await self.crawlers[crawler_name].get_list()
            logger.info(f'Fetched {len(conferences)} conference(s) from {crawler_name}')

            for conference in conferences:
                await self.detail_queue.put({'key': crawler_name, 'data': conference})

        except:
            logger.exception(f'Got exception from crawler: {crawler_name} list')

        if self.callback is not None:
            await self.callback(crawler_name)

    async def process_detail(self, crawler_name, data):
        try:
            conference = await self.crawlers[crawler_name].get_details(data)
            is_duplicate = await self.crawlers[crawler_name].check_duplicate(data, self.data_client)
            if not is_duplicate:
                await self.save(crawler_name, conference)
                logger.info(f'Add new conference from {crawler_name}: {conference.name}')

            # maybe logic for update here
            await self.crawlers[crawler_name].save_cache(self.data_client)
        except:
            logger.exception(f'Got exception from crawler: {crawler_name} detail')

    async def save(self, crawler_name, conference):
        await self.data_client.insert_conference(conference)
        source_id = self.crawlers[crawler_name].get_id()
        conference_source = ConferenceSource(conference.website, source_id, conference.id)
        await self.data_client.insert_conference_source(conference_source)
