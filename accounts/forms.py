from django import forms
from .models import User

class ProfileForm(forms.ModelForm):
    """사용자 프로필 폼"""
    class Meta:
        model = User
        fields = ['nickname', 'profile_image', 'bio']
        widgets = {
            'nickname': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        } 