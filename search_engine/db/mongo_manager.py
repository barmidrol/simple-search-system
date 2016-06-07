from pymongo import MongoClient, ASCENDING
import time

class MongoManager:
    def __init__(self, sleep_time=3):
        self.client = MongoClient()
        self.db = self.client.search_system
        self.sleep_time = sleep_time

    def html_to_process(self, data):
        docs = self.db.documents_to_process
        docs.insert_one(data)

    def document_to_indexing(self, data):
        docs = self.db.documents_to_indexing
        docs.insert_one(data)

    def get_html_page(self):
        docs = self.db.documents_to_process

        while True:
            page = docs.find_one_and_delete({}, sort=[('time', ASCENDING)])

            if page:
                break
            else:
                print('No documents to process. Waiting {0} seconds...'.format(self.__sleep_time))
                time.sleep(self.__sleep_time)

        return page

    def write_processed_document(self, url):
        indexed_docs = self.db.indexed_documents
        indexed_docs.insert_one({'url': url, 'time': time.time()})

    def update_processed_document(self, url):
        indexed_docs = self.db.indexed_documents
        indexed_docs.update_one({'url': url}, {'$set': {'time': time.time()}})

    def document_indexed(self, url):
        indexed_docs = self.db.indexed_documents
        cursor = indexed_docs.find({'url': url})

        obj = next(cursor, None)

        return obj if obj else None

    def get_document_to_indexing(self):
        docs = self.db.documents_to_indexing

        while True:
            document = docs.find_one_and_delete({}, sort=[('time', ASCENDING)])

            if document:
                break
            else:
                print('No documents to indexing. Waiting {0} seconds...'.format(self.sleep_time))
                time.sleep(self.sleep_time)

        return document

    def __del__(self):
        self.client.close()


if __name__ == '__main__':
    m = MongoManager()
