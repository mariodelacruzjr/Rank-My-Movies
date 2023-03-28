from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView, name='home'),
    path('movies/', views.MovieView, name='movies'),
]
