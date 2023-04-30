from django.db import models


# Create your models here.

class Video(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField()
    video_id = models.CharField(max_length=11, unique=True)
