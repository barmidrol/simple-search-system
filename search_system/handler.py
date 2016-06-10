import threading
import json
import pymorphy2

from search_system.query_handler import QueryHandler
from search_system.snippet_generator import SnippentsGenerator
from search_engine.utils import word_tokenize
from django.utils.html import escape, mark_safe

class SearchEngine(object):
    analyzer = pymorphy2.MorphAnalyzer()
    handler = QueryHandler()
    snippet_generator = SnippentsGenerator(200)

    def process_query(self, query):
        return [self.analyzer.parse(word)[0].normal_form for word in word_tokenize(query)]

    def search(self, query):
        if query is not None and query.strip():
            result = []
            processed_query = self.process_query(query)
            self.handler.feed(processed_query)
            docs = self.handler.get_documents_list()
            for document in docs:
                self.snippet_generator.feed(document['url'], processed_query)
                data = {
                    "Title": self.snippet_generator.get_title(),
                    "Snippet": self.snippet_generator.get_snippet(),
                    "Link": document['url']
                }

                result.append(data)

            result_info = {"resume_point" : 0, "result" : result}
            result_id = 0
            with open("search_results{0}".format(result_id), 'w') as f:
                encoder = json.JSONEncoder()
                f.write(encoder.encode(result_info))

        return {"result_id" : result_id, "result_amount" : len(result)}



class SearchResultsManager(object):
    def dispense(self, search_results_id):
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
