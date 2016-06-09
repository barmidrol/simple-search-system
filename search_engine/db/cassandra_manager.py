from datetime import datetime

from cassandra.cluster import Cluster

class CassandraManager:
    def __init__(self):
        self.__cluster = Cluster()
        self.__session = self.__cluster.connect("search_system")

    def init_schema(self):
        self.__session.execute(
            '''
            CREATE TABLE main_index(
                   term text PRIMARY KEY,
                   url text,
                   frequence float,
                   positions list<int>
            )
            '''
        )
        self.__session.execute(
            '''
            CREATE TABLE documents(
                   url text PRIMARY KEY,
                   sentences text,
                   title text,
                   h1 text
            )
            '''
        )

    def write_data_to_index(self, url, frequencies):
        for item in frequencies:
            self.__session.execute(
                '''
                INSERT INTO main_index (term, url, frequence, positions)
                VALUES (%s, %s, %s, %s)
                ''',
                (item[0], url, item[1], item[2])
            )

    def write_document(self, url, sentences, title, h1):
        self.__session.execute(
            '''
            INSERT INTO documents (url, sentences, title, h1)
            VALUES (%s, %s, %s, %s)
            ''',
            (url, sentences, title, h1)
        )

    def get_document(self, url):
        result = self.__session.execute(
            '''
            SELECT sentences, title, h1 FROM documents
            WHERE url=%s
            ''',
            (url,)
        )[0]

        return result

    def document_exist(self, url):
        result = self.__session.execute(
            '''
            SELECT url FROM documents
            WHERE url=%s
            ''',
            (url,)
        )

        return bool(result)

    def get_documents_contain_term(self, term):
        result = self.__session.execute(
            '''
            SELECT url, frequence FROM main_index
            WHERE term=%s
            ''',
            (term,)
        )

        return list(result)

    def get_positions_of_term_in_doc(self, term, url):
        result = self.__session.execute(
            '''
            SELECT positions FROM main_index
            WHERE term=%s AND url=%s ALLOW FILTERING
            ''',
            (term, url)
        )

        return result[0].positions if result else None

    def get_count_of_documents(self):
        result = self.__session.execute(
            '''
            SELECT count(*) FROM documents
            '''
        )[0]

        return result.count

    def __del__(self):
        self.__cluster.shutdown()
