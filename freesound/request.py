from bs4 import BeautifulSoup
import requests
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Sound:
    def __init__(self, item_id: str, url: str, title: str, description: str, author: str, mp3: str, ogg: str, duration: str, spectrum: str):
        self.url = url
        self.id = item_id
        self.title = title
        self.description = description
        self.author = author
        self.mp3 = mp3
        self.ogg = ogg
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
            if item:
                if not item['id']:
                    continue
                item_id = item['id']
                url = f'{Request.url}{Request._get_item_arg(item, "a", "title", "href")}'
                title = Request._get_item_arg(item, 'a', 'title', '__text__')
                description = Request._get_item_arg(item, 'p', 'description', '__text__')
                author = Request._get_item_arg(item, 'a', 'user', '__text__')
                mp3 = Request._get_item_arg(item, 'a', 'mp3_file', 'href')
                ogg = Request._get_item_arg(item, 'a', 'ogg_file', 'href')
                spectrum = Request._get_item_arg(item, 'a', 'spectrum', 'href')
                duration = Request._get_item_arg(item, 'span', 'duration', '__text__')
                results.append(Sound(item_id, url, title, description, author, mp3, ogg, duration, spectrum))

        return results

    @staticmethod
    def _get_item_arg(item, tag, class_name, key):
        result = item.find(tag, attrs={'class': class_name})
        if result:
            if key == '__text__':
                return result.text
            if result[key]:
                return result[key]
        else:
            return 'empty'

    def __repr__(self):
        return f"<\"{self.url}\" ({self.query})>"


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
