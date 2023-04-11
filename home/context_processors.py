from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Token


def token_count(request):
    if not request.user.is_authenticated:
        return {}
    
    try:
        token_count = Token.objects.get(user=request.user).token_count
    except Token.DoesNotExist:
        token_count = None
        
    return {'token_count': token_count}
