from bs4 import BeautifulSoup
import requests
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Request:
    def __init__(self, request: str):
        self.request = request

    def get(self, **kwargs):
        params = {}
        if 'page' in kwargs:
            params['page'] = str(kwargs['page'])

        response = requests.get(f"https://freesound.org/search/?q={self.request}", params=params)
        return response

    def soup(self, page: int):
        results = {}

        html = self.get(page=page).text
        soup = BeautifulSoup(html, "html.parser")

        for item in soup.find_all("div", {"class": "sample_player"}):
            title = item.find('a', attrs={'class': 'title'}).text
            mp3 = item.find('a', attrs={'class': 'mp3_file'})['href']
            results[title] = mp3

        return results


def search_sound():
    r = Request('click')
    results = r.soup(1)
    for k, v in results.items():
        logger.info(f'{k} | {v}')


if __name__ == '__main__':
    search_sound()
