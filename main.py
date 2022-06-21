import time
from dataclasses import dataclass
from signal import SIGINT, signal
from os import _exit
from threading import Lock
from urllib.parse import urlparse

from halo import Halo
from publicsuffix2 import fetch, get_sld
from requests import Session
from scrapy.http import Response
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from shared import get_session_id, add_url


halo: Halo = None
session_id: int = None

@dataclass(frozen=True)
class Item:
    url: str

class WaybackItemProcessor:
    def __init__(self):
        self.session = Session()
        self.lock = Lock()
        # self.session_model = add_session()

    def process_item(self, item: Item, spider: "WaybackCrawler"):
        spider.halo.text = "Archiving " + item.url + "."
        with self.lock:
            r = self.session.get(f"https://web.archive.org/save/" + item.url, allow_redirects=False)
            retry_count = 1
            while not r.ok and retry_count <= 5:
                spider.log("Recieved non-302 response, sleeping 60 seconds.")
                spider.halo.text = "Retrying " + item.url + " [Attempt #" + str(retry_count) + "]."
                time.sleep(60)
                r = self.session.get(f"https://web.archive.org/save/" + item.url, allow_redirects=False)
                retry_count += 1
            if r.ok:
                add_url(session_id, item.url)
        return item


class WaybackCrawler(CrawlSpider):
    name = "WaybackCrawler"
    custom_settings = {
        "ITEM_PIPELINES": {
            WaybackItemProcessor: 100
        },
        "LOG_ENABLED": False
    }

    def __init__(self, start_url: str):
        global halo
        global session_id
        self.start_urls = [start_url]
        parsed = urlparse(start_url)
        fetched = fetch()
        root = get_sld(parsed.hostname, fetched)
        self.rules = [Rule(LinkExtractor(allow_domains=(parsed.hostname, root)), callback=self.process_wayback,
                           follow=True)]
        self.custom_settings = WaybackCrawler.custom_settings.copy()
        self.halo = halo = Halo(text="Scraping...")
        self.session_id = session_id = get_session_id()
        super().__init__()
        self.halo.start()

    def process_wayback(self, response: Response):
        return Item(response.url)


def do_my_exit(*_):
    # orm_session.invalidate()
    if halo:
        halo.stop()
    _exit(0)

signal(SIGINT, do_my_exit)
