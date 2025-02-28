from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User
from allauth.account.forms import LoginForm

class CustomUserCreationForm(UserCreationForm):
    """회원가입 폼"""
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="아이디는 150자 이하의 문자, 숫자, @, ., +, -, _만 사용 가능합니다.",
        label="아이디"
    )
    
    nickname = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="다른 사용자와 중복되지 않는 닉네임을 입력하세요.",
        label="닉네임"
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        help_text="유효한 이메일 주소를 입력하세요.",
        label="이메일"
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="• 비밀번호는 최소 8자 이상이어야 합니다.<br>"
                 "• 비밀번호는 일반적으로 사용되는 것이 아니어야 합니다.<br>"
                 "• 비밀번호는 숫자만으로 구성될 수 없습니다.<br>"
                 "• 비밀번호는 개인정보와 유사할 수 없습니다.",
        label="비밀번호"
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="확인을 위해 이전과 동일한 비밀번호를 입력하세요.",
        label="비밀번호 확인"
    )
    
    class Meta:
        model = User
        fields = ['username', 'nickname', 'email', 'password1', 'password2']
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("이미 사용 중인 아이디입니다.")
        return username
    
    def clean_nickname(self):
        nickname = self.cleaned_data.get('nickname')
        if User.objects.filter(nickname=nickname).exists():
            raise forms.ValidationError("이미 사용 중인 닉네임입니다.")
        return nickname
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("이미 사용 중인 이메일입니다.")
        return email

class ProfileForm(forms.ModelForm):
    """사용자 프로필 폼"""
    nickname = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="다른 사용자와 중복되지 않는 닉네임을 입력하세요.",
        label="닉네임"
    )
    
    class Meta:
        model = User
        fields = ['nickname', 'profile_image', 'bio']
        widgets = {
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'profile_image': '프로필 이미지',
            'bio': '자기소개'
        }
    
    def clean_nickname(self):
        nickname = self.cleaned_data.get('nickname')
        if User.objects.exclude(pk=self.instance.pk).filter(nickname=nickname).exists():
            raise forms.ValidationError("이미 사용 중인 닉네임입니다.")
        return nickname 

class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})
        self.fields['remember'].widget.attrs.update({'class': 'form-check-input'}) 