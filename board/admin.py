from django.contrib import admin
from .models import Board, Post, Comment, Attachment, Vote

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    """게시판 관리자"""
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)

class AttachmentInline(admin.TabularInline):
    """첨부 파일 인라인"""
    model = Attachment
    extra = 1

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """게시글 관리자"""
    list_display = ('title', 'board', 'author', 'created_at', 'views')
    list_filter = ('board', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    inlines = [AttachmentInline]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """댓글 관리자"""
    list_display = ('post', 'author', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username', 'post__title')

@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    """첨부 파일 관리자"""
    list_display = ('filename', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('filename', 'post__title')

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    """투표 관리자"""
    list_display = ['user', 'vote_type', 'content_object', 'created_at']
    list_filter = ['vote_type', 'created_at']
