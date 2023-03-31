from django.urls import path
from django.contrib.auth.views import LoginView
from django.contrib.auth import views as auth_views
from .views import search_results, register, delete_movie, save_movie, favorites, dashboard_view, home_view


urlpatterns = [
    path('', home_view, name='home'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),
    path('favorites/', favorites, name='favorites'),
    path('movies/<int:movie_id>/delete/', delete_movie, name='delete_movie'),
    path('search/', search_results, name='search_results'),
    path('save_movie/', save_movie, name='save_movie'),


]
