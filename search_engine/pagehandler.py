import time

from multiprocessing import Process
from urlparse import urlparse

from db.mongo_manager import MongoManager
from bs4 import BeautifulSoup

class PageHandler:
    def __init__(self):
        self.mongo_conn = MongoManager()

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

            soup = BeautifulSoup(html, "html.parser")

            data = {
                'url': page['url'],
                'text': soup.text if soup else "",
                'title': soup.title.text if soup.title else "",
                'h1': soup.h1.text if soup.h1 else "",
                'h2': soup.h2.text if soup.h2 else "",
                'h3': soup.h3.text if soup.h3 else "",
                'h4': soup.h4.text if soup.h4 else "",
                'h5': soup.h5.text if soup.h5 else "",
                'h6': soup.h6.text if soup.h6 else "",
            }

            if indexed_page is None:
                self.mongo_conn.write_processed_document(page['url'])

            self.mongo_conn.document_to_indexing(data)

def main(process_count):
    def process_documents():
        handler = PageHandler()
        handler.start()

    workers = [Process(target=process_documents) for _ in range(process_count)]
    [worker.start() for worker in workers]
    [worker.join() for worker in workers]


if __name__ == '__main__':
    main(3)
