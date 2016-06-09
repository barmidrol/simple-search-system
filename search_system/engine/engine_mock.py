import threading
import json
import pymorphy2

from search_system.query_handler import QueryHandler
from search_system.snippet_generator import SnippentsGenerator
from search_engine.utils import word_tokenize

class SearchEngine(object):
    analyzer = pymorphy2.MorphAnalyzer()
    handler = QueryHandler()
    snippet_generator = SnippentsGenerator(200)

    def process_query(self, query):
        return [self.analyzer.parse(word)[0].normal_form for word in word_tokenize(query)]

    def search(self, query):
        if query is not None and query.strip():
            processed_query = self.process_query(query)
            self.handler.feed(processed_query)
            result = self.handler.get_documents_list()
            print(result)
            for document in result:
                self.snippet_generator.feed(document['url'], processed_query)
                document['Title'] = self.snippet_generator.get_title()
                document['Snippet'] = self.snippet_generator.get_snippet()

        return result



class SearchResultsManager(object):
    def dispense(self, search_results_id):
        threading._sleep(1)
        with open("search_results{0}".format(search_results_id), 'r') as f:
            decoder = json.JSONDecoder()
            result_info = decoder.decode(f.read())
            resume_point = result_info["resume_point"]
            if (resume_point < len(result_info["result"]) - 10):
                result = result_info["result"][resume_point:resume_point + 10]
                result_info["resume_point"] += 10
            else:
                result = result_info["result"][resume_point:-1]
                result_info["resume_point"] = len(result_info["result"])
        with open("search_results{0}".format(search_results_id), 'w') as f:
            encoder = json.JSONEncoder()
            f.write(encoder.encode(result_info))
        return result
