from bs4 import BeautifulSoup
import requests
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Sound:
    def __init__(self, item_id: str, title: str, mp3: str, duration: str, spectrum: str):
        self.id = item_id
        self.title = title
        self.mp3 = mp3
        self.duration = duration
        self.spectrum = spectrum

    def __repr__(self):
        return f"<{self.title} ({self.id}): {self.mp3}>"


class Request:
    url = "https://freesound.org"

    def __init__(self, query: str):
        self.query = query

    def get(self, page: int = None):
        params = {}
        if isinstance(page, int):
            params['page'] = str(page)

        response = requests.get(f"{self.url}/search/?q={self.query}", params=params)
        return response

    @classmethod
    def browse(cls):
        response = requests.get(f"{cls.url}/browse/")
        return response

    @classmethod
    def soup_browse(cls):
        html = cls.browse().text
        soup = BeautifulSoup(html, "html.parser")
        return cls._de_soup_items(soup)

    def soup(self, page: int = 1):
        html = self.get(page=page).text
        soup = BeautifulSoup(html, "html.parser")
        return self._de_soup_items(soup)

    @staticmethod
    def _de_soup_items(soup: BeautifulSoup):
        results = []
        for item in soup.find_all("div", {"class": "sample_player_small"}):
            item_id = item['id']
            title = item.find('a', attrs={'class': 'title'}).text
            mp3 = item.find('a', attrs={'class': 'mp3_file'})['href']
            spectrum = item.find('a', attrs={'class': 'spectrum'})['href']
            duration = item.find('span', attrs={'class': 'duration'}).text
            results.append(Sound(item_id, title, mp3, duration, spectrum))

        return results


def search_sound(query: str, page: int = 1):
    r = Request(query)
    results = r.soup(page=page)
    return results


def view_browse():
    results = Request.soup_browse()
    return results


if __name__ == '__main__':
    print(view_browse())
    print(search_sound('click'))
