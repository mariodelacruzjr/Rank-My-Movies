from django.shortcuts import render
from .utils import tmdb
import requests
import json

# Create your views here.

def HomeView(request):
    response = requests.get(f'https://api.themoviedb.org/3/trending/all/week?api_key=3372059c7957b772cf7c72b570ae110f')
    trending_all_week_results = json.loads(response.content)['results']
    
    context = {
        
        'trending_all_week_results': trending_all_week_results
    }
    return render(request,'index.html',context)


"""def MovieView(request):
    query = request.GET.get('horror')
    if query:
        results = tmdb.search_movies(query)['results']
    else:
        results = []
    context = {'results': results}
    return render(request, 'movies/search.html', context)"""

def MovieView(request):
    #query="scary"
    #query = request.GET.get('query')
    #if query:
        #response = requests.get(f'https://api.themoviedb.org/3/search/movie?api_key=3372059c7957b772cf7c72b570ae110f&query={query}')
        #results = json.loads(response.content)['results']
    #else:
        #results = []
    #context = {'results': results}
    response = requests.get(f'https://api.themoviedb.org/3/trending/all/week?api_key=3372059c7957b772cf7c72b570ae110f')
    trending_all_week_results = json.loads(response.content)['results']
    context={'trending_all_week_results': trending_all_week_results}

    



    
    return render(request, 'movies/search.html', context)


