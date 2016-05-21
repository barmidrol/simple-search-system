import urllib
import re
import time
from threading import Thread
import mechanize
import readability
from bs4 import BeautifulSoup
from readability.readability import Document
import urlparse


class Crawler:
    visited = []
    thread_list = []
    urls = []
    glob_visited = []

    depth = 0
    counter = 0
    root = ""

    def __init__(self, url, depth):
        self.glob_visited.append(url)
        self.depth = depth
        self.root = url

    def run(self):
        while self.counter < self.depth:
            for w in self.glob_visited:
                self.visited.append(w)
                self.urls.append(w)

            self.glob_visited = []
            for r in self.urls:
                try:
                    t = Thread(target=self.scrape, args=(r,))
                    self.thread_list.append(t)
                    t.start()
                except:
                    pass
            for g in self.thread_list:
                g.join()
            self.counter += 1

        return self.visited

    def scrape(self, root):
        result_urls = []
        br = mechanize.Browser()
        br.set_handle_robots(False)
        br.addheaders = [('User-Agent', 'Firefox')]

        try:
            br.open(root)
            for link in br.links():
                new_url = urlparse.urljoin(link.base_url, link.url)
                if urlparse.urlparse(root).netloc in urlparse.urlparse(link.base_url).netloc and new_url not in self.glob_visited:
                    result_urls.append(new_url)
        except:
            pass

        for res in result_urls:
            self.glob_visited.append(res)
