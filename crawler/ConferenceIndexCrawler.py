import logging
import re
from asyncio import sleep
from datetime import datetime
from bs4 import BeautifulSoup

from .ICrawler import ICrawler
from datastore.model import Conference, Topic
from .utils import fetch, safe_int

logger = logging.getLogger(__name__)


class ConferenceIndexCrawler(ICrawler):
    _url = 'https://conferenceindex.org/conferences/information-technology'

    def __init__(self, _id, cache):
        self._id = int(_id)
        self._current_page = safe_int(cache, 1)

    def get_id(self):
        return self._id

    def get_cache(self):
        return self._current_page

    async def get_list(self):
        await sleep(5)  # show some mercy
        params = {
            'page': self._current_page
        }

        logger.info(f'Try to get list data from {self._url}, page: {self._current_page} ')
        html_content = await fetch(self._url, params=params)
        parsed_data = self.__extract_list(html_content)
        self._current_page = parsed_data['next-page']

        return parsed_data['conferences']

    async def get_details(self, data):
        if not isinstance(data, dict):
            raise TypeError(f'Expecting a dict but getting an {type(data)}')

        await sleep(2)  # show some mercy
        html_content = await fetch(data['website'])
        detail = self.__extract_details(html_content)
        conference = Conference(
            '',
            '',
            '',
            data.get('name', ''),
            data.get('location', ''),
            detail['conference'].get('start_date', ''),
            detail['conference'].get('end_date', ''),
            detail['conference'].get('website', ''),
            detail['conference'].get('description', '')
        )

        topics = []
        for topic in detail['topics']:
            topics.append(Topic('', topic))

        return {'conference': conference, 'topics': topics}

    @staticmethod
    def __parse_dates(date_string):
        if not isinstance(date_string, str):
            raise TypeError(f'Expecting a string but getting an {type(date_string)}')

        parts = [part.strip() for part in date_string.split(',')]
        year = int(parts[-1])

        start_date_str, end_date_str = [part.strip() for part in parts[0].split('-')]
        # parse start date
        start_month, start_day = start_date_str.split()[0], int(start_date_str.split()[1])
        start_date = datetime.strptime(f"{start_month} {start_day} {year}", "%B %d %Y").date()

        # parse end date
        end_month, end_day = end_date_str.split()[0], end_date_str.split()[-1]
        if end_day == end_month:
            end_month = start_month

        end_day = int(end_date_str.split()[-1])

        end_date = datetime.strptime(f"{end_month} {end_day} {year}", "%B %d %Y").date()

        return start_date, end_date

    @staticmethod
    def __extract_list(data):
        result = {'next-page': 1, 'conferences': []}
        soup = BeautifulSoup(data, 'html.parser')

        conference_list = soup.find("div", {"id": "eventList"}).find_all("li")
        for item in conference_list:
            if len(item.contents) > 1:
                conference_name = item.find("a").text.strip()
                location_info = item.contents[-1].split('-')[-1].strip()
                conference_link = item.find("a").get("href")

                result['conferences'].append({
                    '_id': '',
                    'name': conference_name,
                    'location': location_info,
                    'website': conference_link
                })

        pagination = soup.find("ul", class_="pagination")

        if pagination:
            next_page = pagination.find("a", rel="next")
            if next_page:
                result['next-page'] = next_page.get("href").split('page=')[-1]

        return result

    def __extract_details(self, data):
        details = {}
        soup = BeautifulSoup(data, 'html.parser')

        details_container = soup.find("div", {"class": "row mb-3"})

        li_container = details_container.find_all('li')
        for item in li_container:
            if item.find(string=re.compile('Website URL')):
                details['website'] = item.find('strong').get_text(strip=True)
            elif item.find(string=re.compile('Date')):
                date_tag = item.find_next('strong')
                start_date, end_date = self.__parse_dates(date_tag.get_text(strip=True))
                details['start_date'] = start_date
                details['end_date'] = end_date

        details['description'] = soup.find("div", {"id": "event-description"}).find_next('p').get_text(strip=True)

        tags_container = details_container.find('li', {"class": "mt-3"}).find_all('a')
        tags = []
        for tag in tags_container:
            tags.append(tag.get_text(strip=True))

        return {'conference': details, 'topics': tags}
