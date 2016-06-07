import redis


POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)


class RedisManager:
    def __init__(self):
        self.db_connection = redis.Redis(connection_pool=POOL)

    def add_url_to_main(self, url):
        self.db_connection.rpush('main:queue', url)

    def get_url_from_main(self):
        return self.db_connection.blpop('main:queue')[1].decode('utf-8')

    def put_url_to_crawling_domains(self, url):
        self.db_connection.rpush('crawling_domains', url)

    def get_url_from_crawling_domains(self):
        return self.db_connection.lpop('crawling_domains').decode('utf-8')

    def len_crawling_domains(self):
        return self.db_connection.llen('crawling_domains')

    def len_local_queue(self):
        return self.db_connection.llen('queue')

    def put_url_to_local_queue(self, urls):
        if type(urls) is list:
            [self.db_connection.rpush('queue', url) for url in urls]
        else:
            self.db_connection.rpush('queue', urls)

    def get_url_from_local(self):
        result = self.db_connection.blpop('queue', timeout=5)

        if result is not None:
            return result[1].decode('utf-8')
        else:
            return result

if __name__ == '__main__':
    print get_url_from_local()
