from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.http import HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
import os
import requests
import json
from .models import MovieImage, Movie
import openai
from django.core.files.temp import NamedTemporaryFile
from urllib.request import urlopen
from django.views import View


class HomeView(View):
    template_name = 'home.html'
    dashboard_template_name = 'dashboard.html'
    

    def get(self, request):
        if request.user.is_authenticated:
            tmdb_api_key=os.getenv("TMDB_API_KEY")
            # Make a request to the TMDB API to get the trending movies from the past week
            response = requests.get(f'https://api.themoviedb.org/3/trending/movie/week?api_key={tmdb_api_key}')
            print(response)
            # Parse the response and extract the list of trending movies
            trending_all_week_results = json.loads(response.content)['results']
            # Create a dictionary containing the trending movies to pass to the template
            context = {
                'trending_all_week_results': trending_all_week_results
            }
            return render(request, self.dashboard_template_name, context)
        return render(request, self.template_name)



# This view handles user registration using the built-in UserCreationForm in Django

def register(request):
    if request.method == 'POST':
        # If the form has been submitted, create a UserCreationForm with the submitted data
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # If the form is valid, save the new user and redirect to the home page
            form.save()
            return redirect('home')
    else:
        # If the form has not been submitted, create an empty UserCreationForm
        form = UserCreationForm()

    # Render the registration page with the UserCreationForm
    return render(request, 'register.html', {'form': form})


# This view displays the list of movies saved as favorites by the logged-in user


#def generated_image(request, movie_image_id):
    #movie_image = MovieImage.objects.get(id=movie_image_id)
    #return render(request, 'generated_image.html', {'movie_image': movie_image})



def generate_image(request, mov_id):
    # Use the movie description as the text prompt
    tmdb_api_key=os.getenv("TMDB_API_KEY")
    BASE_URL = f"https://api.themoviedb.org/3/"
    endpoint = f"movie/{mov_id}"
    params = {"api_key": tmdb_api_key}
    tmdb_response = requests.get(BASE_URL + endpoint, params=params)
    tmdb_response_json = json.loads(tmdb_response.text)
    text_prompt = tmdb_response_json.get("overview")
    m_title = tmdb_response_json.get("title")
    print(os.environ.get("OPENAI_API_KEY"))
    # Try to retrieve a movie with the given mov_id from the database
    openai.api_key=os.getenv("OPENAI_API_KEY")
    res = openai.Image.create(prompt=text_prompt, n=1, size="256x256")
    image_url = res["data"][0]["url"]
    img_temp = NamedTemporaryFile()
    img_temp.write(urlopen(image_url).read())
    img_temp.flush()
    my_movie, created = Movie.objects.get_or_create(
        mov_id=mov_id, defaults={"title": m_title}
    )
    movie_image = MovieImage(movie=my_movie)
    movie_image.image.save(f"{my_movie.title}.jpg", img_temp)

    return render(request, "generated_image.html", {"movie_image": movie_image})


def poster_design(request):
    if request.method == 'POST':
        movie_id = request.POST.get('movie_id')
        movie_title = request.POST.get('movie_title')
        tmdb_api_key=os.getenv("TMDB_API_KEY")
        url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={tmdb_api_key}&language=en-US'
        response = requests.get(url)
        movie = response.json()
        return render(request, 'poster_design.html', {'movie': movie, 'movie_title': movie_title})
    else:
        return HttpResponseNotAllowed(['POST'])


@login_required
def favorites(request):
    # Get all the movies that belong to the logged-in user
    movies = Movie.objects.filter(user=request.user)


    # Create a context dictionary containing the list of movies
    context = {
        'movies': movies,
    }

    # Render the favorites page with the list
    return render(request, 'favorites.html', context)




# This view deletes a movie from the user's favorites list

def delete_movie(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    
    if request.method == 'POST':
        movie.delete()
        return HttpResponse('', status=204)
    
    return render(request, 'delete_movie.html', {'movie': movie})



# This view saves a new movie to the user's favorites list

@login_required
def save_movie(request):
    # Check if the request method is POST
    if request.method == 'POST':
        # Get the movie ID from the POST request
        movie_id = request.POST.get('movie_id')
        
        # Call The Movie Database API to get movie details
        tmdb_api_key=os.getenv("TMDB_API_KEY")
        endpoint = f'https://api.themoviedb.org/3/movie/{movie_id}'
        response = requests.get(endpoint, params={'api_key': tmdb_api_key})
        data = response.json()
        
        # Get the movie title, overview, and poster path from the API response
        movie_title = data.get('title')
        movie_overview = data.get('overview')
        movie_poster_path = data.get('poster_path')
        
        # Check if all required movie details are available
        if movie_title and movie_overview and movie_poster_path:

            # Create a new Movie object and save it to the database
            movie = Movie(title=movie_title, overview=movie_overview, poster_path=movie_poster_path, user_id=request.user.id)
            movie.save()
        
        # Redirect the user to the favorites page
        return redirect('favorites')
    
    # If the request method is not POST, render the dashboard template
    return render(request, 'dashboard.html')



# This view allows a user to search for movies using The Movie Database API

@login_required
def search_results(request):
    # Check if the request method is POST
    if request.method == 'POST':
        # Get the search query from the form data
        query = request.POST.get('search_query')
        
        # If the search query is empty, render the search page again
        if not query:
            return render(request, 'search.html')
            
        # Set up API parameters and make request to The Movie Database API
        tmdb_api_key=os.getenv("TMDB_API_KEY")
        endpoint = f'https://api.themoviedb.org/3/search/movie'
        params = {
            'api_key': tmdb_api_key,
            'query': query
        }
        response = requests.get(endpoint, params=params)
        results = response.json()['results']

        # Process the results from the API and create a list of movies
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

        # Create a context dictionary containing the list of movies and the search query
        context = {
            'movies': movies,
            'search_query': query
        }

        # Render the results page with the list of movies and the search query
        return render(request, 'results.html', context)

    # If the request method is not POST, render the dashboard page
    return render(request, 'dashboard.html')












