import urllib
import re
import time
from threading import Thread
import mechanize
import urlparse
from utils import compress_data
from db.redis_manager import RedisManager
from db.mongo_manager import MongoManager


class Crawler:
    visited = []
    thread_list = []
    counter = 0
    sleep_time = 0

    def __init__(self, sleep_time=1):
        self.redis_conn = RedisManager()
        self.mongo_conn = MongoManager()
        self.browser = mechanize.Browser()
        self.sleep_time = sleep_time

    def run(self):
        while True:
            if self.redis_conn.len_local_queue() == 0:
                print "No urls in local queue"
                time.sleep(self.sleep_time)

            while self.redis_conn.len_local_queue() > 0:
                data = {}
                url = self.redis_conn.get_url_from_local()
                try:
                    t = Thread(target=self.crawl_site, args=(url,))
                    self.thread_list.append(t)
                except:
                    pass

        [thread.start() for thread in self.thread_list]
        [thread.join() for thread in self.thread_list]

    def crawl_site(self, url):
        data = {}
        page = self.fetch(url)
        data['url'] = url
        data['body'] = compress_data(page)
        print(data['body'])
        #self.mongo_conn.html_to_process(data)

    def fetch(self, url):
        result_urls = []
        self.browser.set_handle_robots(False)
        self.browser.addheaders = [('User-Agent', 'Firefox')]
        return self.browser.open(url).read()
