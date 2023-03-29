from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .utils import tmdb
from django.contrib.auth.forms import UserCreationForm
import requests
import json
from .models import Movie
from django.http import HttpResponse
from django.http import HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required


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

from django.shortcuts import render, redirect
from .models import Movie
@login_required
def Favorites(request):
    if request.method == 'POST':
        movie_id = request.POST.get('movie_id')
        api_key = '3372059c7957b772cf7c72b570ae110f'
        endpoint = f'https://api.themoviedb.org/3/movie/{movie_id}'
        response = requests.get(endpoint, params={'api_key': api_key})
        data = response.json()
        movie_title = data['title']
        movie_overview = data['overview']
        movie_poster_path = data['poster_path']
        movie = Movie(title=movie_title, overview=movie_overview, poster_path=movie_poster_path, user=request.user)
        movie.save()
        return redirect('favorites')

    movies = Movie.objects.filter(user=request.user)
    context = {
        'movies': movies
    }
    return render(request, 'favorites.html', context)







