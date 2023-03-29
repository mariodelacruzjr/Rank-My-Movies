from django.db import models

# Create your models here.
class Movie(models.Model):
    title=models.CharField(max_length=255)
    overview=models.TextField()
    poster_path=models.CharField(max_length=255)
    
    def __str__(self):
        return self.title

