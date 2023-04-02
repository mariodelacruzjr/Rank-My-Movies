from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Movie(models.Model):
    title = models.CharField(max_length=255)
    overview = models.TextField()
    poster_path = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    rank = models.IntegerField(null=True, blank=True)
    mov_id = models.CharField(max_length=10, default='0000000000')

    

    def __str__(self):
        return self.title
    
class MovieImage(models.Model):
    movie = models.OneToOneField(Movie, on_delete=models.CASCADE, related_name='image')
    image = models.ImageField(upload_to='movie_images')

    def __str__(self):
        return self.movie.title + ' Image'


