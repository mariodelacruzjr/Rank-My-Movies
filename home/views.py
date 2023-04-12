
import requests
import json
import openai
import stripe
from .models import MovieImage, Movie, Token
from django.core.files.temp import NamedTemporaryFile
from urllib.request import urlopen
from django.views import View
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.http import HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in

from django.contrib import messages
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.temp import NamedTemporaryFile
from urllib.request import urlopen
from .models import Movie, MovieImage, Token
import openai
import requests
import json

@receiver(user_logged_in)
def create_token(sender, user, request, **kwargs):
    # Check if the user already has a Token object
    if not Token.objects.filter(user=user).exists():
        # If the user does not have a Token object, create one with 0 tokens
        token = Token.objects.create(user=user, token_count=0)

def checkout(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    for item in cart.values():
        
        total += float(item['price'])
        image_url = request.build_absolute_uri(item['image_url'])
        cart_items.append({
            'price_data': {
                'currency': 'usd',
                'unit_amount': int(item['price']*100),
                'product_data': {
                    'name': item['title'],
                    'images': [image_url],
                    
                },
            },
            'quantity': 1,
        })
       

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=cart_items,
        mode='payment',
        success_url='http://localhost:8000/success/',
        cancel_url='http://localhost:8000/cancel/',
    )
    

    return render(request, 'checkout.html', {
        'session_id': session.id,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })

def success(request):
    return render(request, 'success.html')

def cancel(request):
    return render(request, 'cancel.html')

def remove_from_cart(request, image_id):
    cart = request.session.get('cart', {})
    cart_item = cart.get(str(image_id))

    if cart_item:
        del cart[str(image_id)]
        request.session['cart'] = cart

    return redirect('cart_view')

def add_to_cart(request, image_id):
    image = get_object_or_404(MovieImage, id=image_id)
    cart = request.session.get('cart', {})
    cart_item = cart.get(str(image_id))

    if cart_item:
        cart_item['quantity'] += 1
        cart_item['price'] = float(cart_item['price']) + float(request.POST.get('price'))
        cart_item['size'] = request.POST.get('size') # Add selected size to cart
    else:
        size = request.POST.get('size')
        price = 10 if size == 'small' else 20 if size == 'medium' else 30
        cart[str(image_id)] = {
            'id': str(image.id),
            'title': image.movie.title,
            'image_url': image.image.url,
            'quantity': 1,
            'price': float(price),
            'size': size # Add selected size to cart
        }

    request.session['cart'] = cart
    print(f"cart is {cart}")
    print(f"cart items are {cart.items}")
    return redirect('cart_view')

def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    for item in cart.values():
        total += float(item['price'])
        item['image_url'] = item.get('image_url', '')
        cart_items.append(item)
    print("Cart Items:", cart_items)
    print("Total:", total)
    context = {
        'cart_items': cart_items,
        'total': total
    }
    return render(request, 'cart.html', context)

class HomeView(View):
    template_name = 'home.html'
    dashboard_template_name = 'dashboard.html'
    

    def get(self, request):
        if request.user.is_authenticated:
            # Make a request to the TMDB API to get the trending movies from the past week
            response = requests.get(f'https://api.themoviedb.org/3/trending/movie/week?api_key={settings.TMDB_API_KEY}')
            print(response)
            # Parse the response and extract the list of trending movies
            trending_all_week_results = json.loads(response.content)['results']
            # Create a dictionary containing the trending movies to pass to the template
            context = {
                'trending_all_week_results': trending_all_week_results
            }
            return render(request, self.dashboard_template_name, context)
        return render(request, self.template_name)

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

def generate_image(request, mov_id):
    user_tokens = Token.objects.get(user=request.user).token_count
    if user_tokens < 20:
        messages.error(request, "You need at least 20 tokens to generate an image.")
        return redirect('home')
    # Use the movie description as the text prompt
    BASE_URL = f"https://api.themoviedb.org/3/"
    endpoint = f"movie/{mov_id}"
    params = {"api_key": settings.TMDB_API_KEY}
    tmdb_response = requests.get(BASE_URL + endpoint, params=params)
    tmdb_response_json = json.loads(tmdb_response.text)
    text_prompt = tmdb_response_json.get("overview")
    m_title = tmdb_response_json.get("title")
    # Try to retrieve a movie with the given mov_id from the database
    openai.api_key=settings.OPENAI_API_KEY
    res = openai.Image.create(prompt=text_prompt, n=1, size="1024x1024")
    image_url = res["data"][0]["url"]
    img_temp = NamedTemporaryFile()
    img_temp.write(urlopen(image_url).read())
    img_temp.flush()
    my_movie, created = Movie.objects.get_or_create(
        mov_id=mov_id, defaults={"title": m_title}
    )
    movie_image = MovieImage(movie=my_movie)
    movie_image.image.save(f"{my_movie.title}.jpg", img_temp)

    user_tokens -= 20
    token_obj = Token.objects.get(user=request.user)
    token_obj.token_count = user_tokens
    token_obj.save()
    messages.success(request, "Image generated successfully. 20 tokens deducted from your account.")
    return render(request, "generated_image.html", {"movie_image": movie_image})

def poster_design(request):
    if request.method == 'POST':
        movie_id = request.POST.get('movie_id')
        movie_title = request.POST.get('movie_title')
        url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={settings.TMDB_API_KEY}&language=en-US'
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

def delete_movie(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    
    if request.method == 'POST':
        movie.delete()
        return HttpResponse('', status=204)
    
    return render(request, 'delete_movie.html', {'movie': movie})

@login_required
def save_movie(request):
    # Check if the request method is POST
    if request.method == 'POST':
        # Get the movie ID from the POST request
        movie_id = request.POST.get('movie_id')
        
        # Call The Movie Database API to get movie details
        endpoint = f'https://api.themoviedb.org/3/movie/{movie_id}'
        response = requests.get(endpoint, params={'api_key': settings.TMDB_API_KEY})
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
        endpoint = f'https://api.themoviedb.org/3/search/movie'
        params = {
            'api_key': settings.TMDB_API_KEY,
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
        return render(request, 'search_results.html', context)

    # If the request method is not POST, render the dashboard page
    return render(request, 'dashboard.html')



