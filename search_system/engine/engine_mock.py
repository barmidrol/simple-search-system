import threading
import json

class SearchEngine(object):
    def search(self, request):
        threading._sleep(1)
        result = [
            {
                "Title" : "{0}#{1}".format(request, i),
                "Snippet" : request * 200,
                "Link" : "http://lmgtfy.com/?q={0}".format(request)
            }
            for i in range(50)
        ]
        result_info = {"resume_point" : 0, "result" : result}
        result_id = 0
        with open("search_results{0}".format(result_id), 'w') as f:
            encoder = json.JSONEncoder()
            f.write(encoder.encode(result_info))

        return {"result_id" : result_id, "result_amount" : len(result)}


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