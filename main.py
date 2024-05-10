import asyncio
import logging

from CrawlerFactory import CrawlerFactory
from datastore import ConferenceDBClient

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def run_list(factory: CrawlerFactory, queue):
    while True:
        package = await queue.get()
        if not isinstance(package, dict):
            continue

        key = package.get('key', '')
        if key != '':
            await factory.process_list(key, callback=lambda _name: queue.put({'key': _name}))


async def run_details(factory: CrawlerFactory, queue):
    while True:
        package = await queue.get()
        if not isinstance(package, dict):
            continue

        key = package.get('key', '')
        if key != '':
            data = package.get('data', None)
            await factory.process_detail(key, data)


async def main():
    try:
        logger.info("Starting the application")
        crawler_name = [
            'ACM',
        ]

        data_client = ConferenceDBClient()
        await data_client.connect(database='conferencesDB.db')

        list_queue = asyncio.Queue()
        detail_queue = asyncio.Queue()
        factory = CrawlerFactory(data_client, detail_queue)

        # Start detail processing coroutine
        list_task = asyncio.create_task(run_list(factory, list_queue))
        detail_task = asyncio.create_task(run_details(factory, detail_queue))

        for name in crawler_name:
            await factory.add_crawler(name)
            await list_queue.put({'key': name})

        await list_task
        await detail_task
    except KeyboardInterrupt:
        logger.info("Application stopped by user.")


if __name__ == '__main__':
    # Run the main coroutine
    asyncio.run(main())
    # pass
