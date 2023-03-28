from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .utils import tmdb
from django.contrib.auth.forms import UserCreationForm
import requests
import json

# Create your views here.

def HomeView(request):
    response = requests.get(f'https://api.themoviedb.org/3/trending/all/week?api_key=3372059c7957b772cf7c72b570ae110f')
    trending_all_week_results = json.loads(response.content)['results']
    
    context = {
        
        'trending_all_week_results': trending_all_week_results
    }
    return render(request,'home.html',context)



@login_required
def DashBoardView(request):
    return render(request, 'dashboard.html')

def register(request):
    if request.method=='POST':
        form=UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form=UserCreationForm()

    return render(request, 'register.html', {'form': form})




