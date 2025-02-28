from django.urls import path
from . import views

app_name = 'board'

urlpatterns = [
    path('', views.home, name='home'),
    path('board/<int:board_id>/', views.board_detail, name='board_detail'),
    path('post/list/', views.post_list, name='post_list'),
    path('post/create/', views.post_create, name='post_create'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('post/<int:pk>/delete/', views.post_delete, name='post_delete'),
    path('comment/<int:pk>/delete/', views.comment_delete, name='comment_delete'),
    path('post/<int:post_id>/comment/', views.comment_create, name='comment_create'),
    path('vote/', views.vote_object, name='vote_object'),
    path('boards/', views.all_boards, name='all_boards'),
    path('post/<int:post_id>/vote/<str:vote_type>/', views.post_vote, name='post_vote'),
    path('comment/<int:comment_id>/vote/<str:vote_type>/', views.comment_vote, name='comment_vote'),
] 