from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """커스텀 사용자 모델"""
    nickname = models.CharField(max_length=50, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    bio = models.TextField(blank=True)
    
    def __str__(self):
        return self.username
