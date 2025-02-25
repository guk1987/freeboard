from django.urls import path
from . import views

app_name = 'board'

urlpatterns = [
    path('', views.home, name='home'),
    path('board/<int:board_id>/', views.board_detail, name='board_detail'),
    path('post/create/', views.post_create, name='post_create'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('post/<int:post_id>/delete/', views.post_delete, name='post_delete'),
    path('post/<int:post_id>/comment/', views.comment_create, name='comment_create'),
] 