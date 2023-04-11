from .models import Token

def token_count(request):
    if not request.user.is_authenticated:
        return {}
    
    try:
        token_count = Token.objects.get(user=request.user).token_count
    except Token.DoesNotExist:
        token_count = None
        
    return {'token_count': token_count}
