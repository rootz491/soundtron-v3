from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


# Create your models here.


class Album(models.Model):
        user = models.ForeignKey(User, on_delete=models.CASCADE)
        artist = models.CharField(max_length=50)
        artist_logo = models.ImageField(upload_to='artist_cover')
        album_title = models.CharField(max_length=300)
        genre = models.CharField(max_length=100)
        album_logo = models.ImageField(upload_to='album_cover')

        # whenever we create a new album, it will redirect to this URL.
        def get_absolute_url(self):
                return reverse('music:detail', kwargs={'pk': self.pk})


        def __str__(self):
                return self.album_title + ' - ' + self.artist


class song(models.Model):
        album = models.ForeignKey(Album, on_delete=models.CASCADE)
        song_title = models.CharField(max_length=200)
        audio_file = models.FileField(upload_to='music')
        is_fav = models.BooleanField(default=False)

        def get_absolute_url(self):
                return reverse('music:index')

        def __str__(self):
                return self.song_title