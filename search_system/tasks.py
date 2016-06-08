from __future__ import absolute_import, unicode_literals
from simple_search_system.celery import app
import time
import re
from urlparse import urlsplit
import requests
from celery import task, group
from eventlet import Timeout
from pybloom import BloomFilter
from search_engine.db.mongo_manager import MongoManager
from search_engine.pagehandler import PageHandler

url_regex = re.compile(
    r'\b(([\w-]+://?|www[.])[^\s()<>]+(?:\([\w\d]+\)|([^[:punct:]\s]|/)))')

def domain(url):
    """Return the domain part of a URL."""
    return urlsplit(url)[1].split(':')[0]

@app.task(ignore_result=True, serializer='pickle', compression='zlib')
def crawl(url, seen=None):
    print('crawling: {0}'.format(url))
    if not seen:
        seen = BloomFilter(capacity=50000, error_rate=0.0001)

    with Timeout(5, False):
        response = requests.get(url)
        conn = MongoManager()
        data = {'url': url, 'body': response.content}
        conn.html_to_process(data)

    location = domain(url)
    wanted_urls = []
    for url_match in url_regex.finditer(response.text):
        url = url_match.group(0)
        # To not destroy the internet, we only fetch URLs on the same domain.
        if url not in seen and location in domain(url):
            wanted_urls.append(url)
            seen.add(url)

    subtasks = group(crawl.s(url, seen) for url in wanted_urls)
    subtasks()

@app.task
def handle_pages():
    handler = PageHandler()
    handler.start()
