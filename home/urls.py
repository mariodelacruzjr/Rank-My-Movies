from django.urls import path
from . import views
from django.contrib.auth.views import LoginView
from django.contrib.auth import views as auth_views
from .views import search_results, register, delete_movie
urlpatterns = [
    path('', views.HomeView, name='home'),
    path('dashboard/', views.DashBoardView, name='dashboard'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),
    path('favorites/', views.Favorites, name='favorites'),
    path('movies/<int:movie_id>/delete/', delete_movie, name='delete_movie'),
    path('search/', search_results, name='search_results'),
    path('save_movie/', views.save_movie, name='save_movie'),


]
