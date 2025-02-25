from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """커스텀 사용자 관리자"""
    list_display = ('username', 'email', 'nickname', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('추가 정보', {'fields': ('nickname', 'profile_image', 'bio')}),
    )
