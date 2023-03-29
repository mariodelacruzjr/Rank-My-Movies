from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .utils import tmdb
from django.contrib.auth.forms import UserCreationForm
import requests
import json
from .models import Movie
from django.http import HttpResponse
from django.http import HttpResponseNotAllowed


# Create your views here.

def HomeView(request):
    response = requests.get(f'https://api.themoviedb.org/3/trending/movie/week?api_key=3372059c7957b772cf7c72b570ae110f')
    trending_all_week_results = json.loads(response.content)['results']
    

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

from django.shortcuts import render, redirect
from .models import Movie

def Favorites(request):
    if request.method == 'POST':
        # Retrieve movie data from TMDB API
        api_key = '3372059c7957b772cf7c72b570ae110f'
        movie_id = request.POST.get('movie_id')
        endpoint = f'https://api.themoviedb.org/3/movie/{movie_id}'
        response = requests.get(endpoint, params={'api_key': api_key})
        data = response.json()

        # Extract the title and poster path from the movie data
        movie_title = data['title']
        movie_poster_path = data['poster_path']

        # Create a new Movie instance and save it to the database
        movie = Movie(title=movie_title, poster_path=movie_poster_path)
        movie.save()

        # Redirect the user to a success page
        return redirect('favorites')

    # Retrieve all movies from the database
    movies = Movie.objects.all()

    return render(request, 'favorites.html', {'movies': movies})







