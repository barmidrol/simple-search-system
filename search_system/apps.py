from django.apps import AppConfig
from search_engine.crawler import Crawler


class SearchSystemConfig(AppConfig):
    name = 'search_system'

    def ready(self):
        crawler = Crawler()
        Crawler.run()
