import time

from multiprocessing import Process
from urlparse import urlparse

from db.mongo_manager import MongoManager
from bs4 import BeautifulSoup
from search_engine.html_parser import Parser

class PageHandler:
    def __init__(self):
        self.mongo_conn = MongoManager()
        self.parser = Parser()

    def start(self):
        while True:
            page = self.mongo_conn.get_html_page()
            print('Process page ', page['url'])
            self.process_page(page)

    def process_page(self, page):
        indexed_page = self.mongo_conn.document_indexed(page['url'])

        if indexed_page is None:
            try:
                html = page['body']
            except Exception as err:
                print('Decode error on {0}: '.format(page['url'], err))
                return

            self.parser.feed(html, page['url'])

            data = {
                'url': page['url'],
                'text': self.parser.text,
                'title': self.parser.title,
                'h1': self.parser.h1,
                'h2': self.parser.h2,
                'h3': self.parser.h3,
                'h4': self.parser.h4,
                'h5': self.parser.h5,
                'h6': self.parser.h6,
            }

            if indexed_page is None:
                self.mongo_conn.write_processed_document(page['url'])

            self.mongo_conn.document_to_indexing(data)
