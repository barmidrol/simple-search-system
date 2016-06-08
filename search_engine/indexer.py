from multiprocessing import Process

from texthandler import TextHandler
from db.mongo_manager import MongoManager
#from db.cassandra_manager import CassandraManager
#from utils import compress_data, decompress_data


class Indexer:
    def __init__(self):
        self.__mongo_conn = MongoManager()
        #self.__cassandra_conn = CassandraManager()
        #self.__text_handler = TextHandler()

    def start(self):
        while True:
            document = self.mongo_conn.get_document_to_indexing()

            h1_length = len(document['h1'])
            if h1_length == 1:
                h1 = document['h1'][0]
            elif h1_length == 0:
                h1 = ''

            if h1_length > 1 or not document['title'] and not h1:
                continue

            try:
                self.__text_handler.feed(
                    text=decompress_data(document['text']).decode('utf-8'),
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
                    decompress_data(document['text']).decode('utf-8'),
                    err
                )

                break

            self.__write_data_to_cassandra(
                document['url'],
                document['title'],
                h1,
                document['time']
            )

    def __write_data_to_cassandra(self, url, title, h1, time):
        print('Indexing {0}'.format(url))
        self.__cassandra_conn.write_data_to_index(url, self.__text_handler.frequencies)
        self.__cassandra_conn.write_document(
            url,
            compress_data(self.__text_handler.sentences),
            title,
            h1,
            time
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
