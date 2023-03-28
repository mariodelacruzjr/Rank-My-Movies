import requests

def search_movies(query):
    api_key = '3372059c7957b772cf7c72b570ae110f'
    url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={query}'
    response = requests.get(url)
    return response.json()
