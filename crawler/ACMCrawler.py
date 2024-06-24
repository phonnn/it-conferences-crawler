import logging
from asyncio import sleep
from datetime import datetime
from bs4 import BeautifulSoup

from .ICrawler import ICrawler
from datastore.model import Conference
from .utils import fetch, safe_int

logger = logging.getLogger(__name__)


class ACMCrawler(ICrawler):
    _url = 'https://www.acm.org/upcoming-conferences'
    _req_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cookie': 'CookieConsent={stamp:%276OpOTytpNfRPTW3jT0HBHO9BswSCYVTJzcn/C8nrJ8vj2fveACsdBQ==%27%2Cnecessary'
                  ':true%2Cpreferences:false%2Cstatistics:false%2Cmarketing:false%2Cmethod:%27explicit%27%2Cver:1'
                  '%2Cutc:1710661251396%2Cregion:%27vn%27}; '
                  'SERVERID=ca980f720986c5b17b55411c0fad1879|6ac32a46f0ed8948d8473f0f6e2e572e; '
                  'JSESSIONID=2E51F9EAE8E1C2D903C863FF49F62C61; '
                  '__cf_bm=mKJbEkygo4FEy4SCgPvUa_qnjT0tMLqto_pBI5BpN3M-1710772862-1.0.1.1-JHPhvJMwTRfth2.ogsF.IdZm'
                  '.s_VWcbJbcGUoOld8ki7XmTmZOlj0mU3XRbNkedxzR.wpLaH.W.ZrL15Pr0Ddw',

        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'
    }

    def __init__(self, _id, cache):
        self._id = int(_id)
        self._current_run = safe_int(cache, 0)

    def get_id(self):
        return self._id

    def get_cache(self):
        return self._current_run

    async def get_list(self):
        await sleep(5)  # show some mercy
        logger.info(f'Try to get list data from {self._url}')
        html_content = await fetch(self._url, self._req_headers)
        conferences = self.__extract_list(html_content)
        if self._current_run >= len(conferences) - 1:
            self._current_run = 0

        return conferences[self._current_run:]

    async def get_details(self, data):
        if not isinstance(data, dict):
            raise TypeError(f'Expecting a dict but getting an {type(data)}')

        name = data.get('name', '')
        website = data.get('website', '')
        location = data.get('location', '')
        start_date = data.get('start_date', '')
        end_date = data.get('end_date', '')
        conference = Conference('', '', '', name, location, start_date, end_date, website)

        self._current_run += 1
        return {'conference': conference, 'topics': []}

    @staticmethod
    def __parse_dates(date_string):
        if not isinstance(date_string, str):
            raise TypeError(f'Expecting a string but getting an {type(date_string)}')

        parts = [part.strip() for part in date_string.split(',')]
        year = int(parts[-1])

        start_date_str, end_date_str = [part.strip() for part in parts[0].split('-')]
        # parse start date
        start_month, start_day = start_date_str.split()[0], int(start_date_str.split()[1])
        start_date = datetime.strptime(f"{start_month} {start_day} {year}", "%b %d %Y").date()
        # parse end date
        end_month, end_day = end_date_str.split()[0], int(end_date_str.split()[1])
        end_date = datetime.strptime(f"{end_month} {end_day} {year}", "%b %d %Y").date()

        return start_date, end_date

    def __extract_list(self, data):
        conferences = []
        soup = BeautifulSoup(data, 'html.parser')
        conference_elements = soup.find_all('li', class_='hidden')
        for element in conference_elements:
            if element.find('a') is None:
                continue

            name = element.find('a').text.strip()
            website = element.find('a')['href']
            location = element.find('p').text.strip()

            # Parse the date string using the defined format
            date_str = element.find('time').text.strip()
            start_date, end_date = self.__parse_dates(date_str)
            conferences.append({
                '_id': '',
                'name': name,
                'location': location,
                'start_date': start_date,
                'end_date': end_date,
                'website': website
            })

        return conferences
