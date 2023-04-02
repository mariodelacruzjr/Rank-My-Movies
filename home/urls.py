from django.urls import path
from django.contrib.auth.views import LoginView
from django.contrib.auth import views as auth_views
from .views import search_results, register, delete_movie, save_movie, favorites, dashboard_view, home_view, poster_design, generate_image, poster_results


urlpatterns = [
    path('', home_view, name='home'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),
    path('favorites/', favorites, name='favorites'),
    path('delete-movie/<int:movie_id>/', delete_movie, name='delete_movie'),
    path('search/', search_results, name='search_results'),
    path('save_movie/', save_movie, name='save_movie'),
    path('poster_results/<int:movie_image_id>/', poster_results, name='poster_results'),
    path('poster_design/', poster_design, name='poster_design'),

    path('generate_image/<int:mov_id>/', generate_image, name='generate_image')
    


]
