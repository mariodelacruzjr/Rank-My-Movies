from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
import requests
import json
from .models import Movie
from django.shortcuts import render, redirect
from .models import Movie
from django.views.decorators.csrf import csrf_exempt





# Create your views here.

def HomeView(request):
    return render(request,'home.html')

@login_required
def DashBoardView(request):
    response = requests.get(f'https://api.themoviedb.org/3/trending/movie/week?api_key=3372059c7957b772cf7c72b570ae110f')
    trending_all_week_results = json.loads(response.content)['results']
    context = {
        
        'trending_all_week_results': trending_all_week_results
    }
    return render(request, 'dashboard.html', context)

def register(request):
    if request.method=='POST':
        form=UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form=UserCreationForm()

    return render(request, 'register.html', {'form': form})


@login_required
def Favorites(request):
    movies = Movie.objects.filter(user=request.user)
    context = {
        'movies': movies
    }
    return render(request, 'favorites.html', context)



def delete_movie(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    if request.method == 'POST':
        movie.delete()
        return redirect('favorites')
    return render(request, 'delete_movie.html', {'movie': movie})

@login_required
def save_movie(request):
    if request.method == 'POST':
        movie_id = request.POST.get('movie_id')
        api_key = '3372059c7957b772cf7c72b570ae110f'
        endpoint = f'https://api.themoviedb.org/3/movie/{movie_id}'
        response = requests.get(endpoint, params={'api_key': api_key})
        data = response.json()
        movie_title = data.get('title')
        movie_overview = data.get('overview')
        movie_poster_path = data.get('poster_path')
        if movie_title and movie_overview and movie_poster_path:
            print('movie_id:', movie_id)
            print('movie_title:', movie_title)
            print('movie_overview:', movie_overview)
            print('movie_poster_path:', movie_poster_path)
            movie = Movie(title=movie_title, overview=movie_overview, poster_path=movie_poster_path, user_id=request.user.id)
            movie.save()
        return redirect('favorites')
    return render(request, 'save_movie.html')



def search_results(request):
    if request.method == 'POST':
        # Retrieve the search query from the form
        query = request.POST.get('search_query')
        if not query:
            # If the search query is not present, render the search form template
            return render(request, 'search.html')
            
        # Make a request to the TMDB API
        api_key = '3372059c7957b772cf7c72b570ae110f'
        endpoint = f'https://api.themoviedb.org/3/search/movie'
        params = {
            'api_key': api_key,
            'query': query
        }
        response = requests.get(endpoint, params=params)
        results = response.json()['results']

        # Create a list of movie dictionaries containing the relevant data
        movies = []
        for movie in results:
            if movie['poster_path']:
                movie_data = {
                    'id': movie['id'],
                    'title': movie['title'],
                    'overview': movie['overview'],
                    'poster_path': 'https://image.tmdb.org/t/p/w500' + movie['poster_path']
                }
                movies.append(movie_data)


        # Create a context dictionary containing the movie data
        context = {
            'movies': movies,
            'search_query': query
        }

        # Render the results page template with the context dictionary
        return render(request, 'results.html', context)

    # If the request method is GET, render the search form template
    return render(request, 'search.html')












