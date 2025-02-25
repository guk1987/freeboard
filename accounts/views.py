from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from .forms import ProfileForm  # 아직 만들지 않음

# Create your views here.

@login_required
def profile_view(request):
    """사용자 프로필 보기"""
    return render(request, 'accounts/profile.html')

@login_required
def profile_edit(request):
    """사용자 프로필 수정"""
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '프로필이 업데이트되었습니다.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile_edit.html', {'form': form})
