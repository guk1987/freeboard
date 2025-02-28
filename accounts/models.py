from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError

class User(AbstractUser):
    """커스텀 사용자 모델"""
    nickname = models.CharField(max_length=50, unique=True, blank=False, null=False, verbose_name="닉네임")
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True, verbose_name="프로필 이미지")
    bio = models.TextField(blank=True, verbose_name="자기소개")
    
    # 이메일 필드를 unique로 설정 (AbstractUser에서 상속)
    email = models.EmailField(unique=True, verbose_name="이메일")
    
    def __str__(self):
        return self.nickname
    
    def clean(self):
        if not self.nickname:
            raise ValidationError({'nickname': '닉네임은 필수 항목입니다.'})
        return super().clean()
