from django.shortcuts import render
from search_system.engine.engine_mock import SearchEngine
from search_system.engine.engine_mock import SearchResultsManager
from django.views.decorators.csrf import ensure_csrf_cookie

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt

from .tasks import hello_world, crawl


def home(request):
    return render(request, 'search_system/home.html', {})

def index_page(request):
    if request.method == 'POST':
        redis_conn = RedisManager()
        crawl(request.POST['url'])

    return render(request, 'search_system/index_page.html', {})

@csrf_protect
@csrf_exempt
def search(request):
    if request.method == 'POST':
        searchEngine = SearchEngine()
        result = searchEngine.search(request.POST["text"])
        return JsonResponse(result, safe=False)


@csrf_protect
@csrf_exempt
def load_results(request):
    if request.method == 'POST':
        searchResultsManager = SearchResultsManager()
        result = searchResultsManager.dispense(request.POST["resultsId"])
        return JsonResponse(result, safe=False)
