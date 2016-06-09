from multiprocessing import Process

from text_handler import TextHandler
from db.mongo_manager import MongoManager
from db.cassandra_manager import CassandraManager

class Indexer:
    def __init__(self):
        self.mongo_conn = MongoManager()
        self.cassandra_conn = CassandraManager()
        self.text_handler = TextHandler()

    def start(self):
        while True:
            document = self.mongo_conn.get_document_to_indexing()

            h1_length = len(document['h1'] or '')
            if h1_length == 1:
                h1 = document['h1'][0]
            elif h1_length == 0:
                h1 = ''

            if h1_length > 1 or not document['title'] and not h1:
                continue

            print('text = {0}'.format(document['text'].encode('utf-8')))
            try:
                self.text_handler.feed(
                    text=document['text'],
                    title=document['title'],
                    h1=h1,
                    h2=document['h2'],
                    h3=document['h3'],
                    h4=document['h4'],
                    h5=document['h5'],
                    h6=document['h6']
                )
            except IndexError as err:
                print(
                    'Index error for {0}: '.format(document['url']),
                    document['text'],
                    err
                )

                break

            self.write_data_to_cassandra(
                document['url'],
                document['title'],
                h1
            )

    def write_data_to_cassandra(self, url, title, h1):
        self.cassandra_conn.write_data_to_index(url, self.text_handler.frequencies)
        self.cassandra_conn.write_document(
            url,
            self.text_handler.sentences,
            title,
            h1
        )

def main(process_count):
    def indexing():
        indexer = Indexer()
        indexer.start()

    workers = [Process(target=indexing) for _ in range(process_count)]
    [worker.start() for worker in workers]
    [worker.join() for worker in workers]


if __name__ == '__main__':
    main(3)
