from django.urls import path
from . import views
from django.contrib.auth.views import LoginView
from .views import  register

urlpatterns = [
    path('', views.HomeView, name='home'),
    path('dashboard/', views.DashBoardView, name='dashboard'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    #path('logout/', logout_view, name='logout'),
    path('register/', register, name='register'),
]
