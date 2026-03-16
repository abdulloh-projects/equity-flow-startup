from django.db import models


# Create your models here.
class Startup(models.Model):
    user_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.TextField()
    website_url = models.URLField()
