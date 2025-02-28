from django.db import models
from django.conf import settings
import markdown
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

class Board(models.Model):
    """게시판 모델"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_post_count(self):
        return self.post_set.count()

class Vote(models.Model):
    """추천/비추천 모델"""
    VOTE_CHOICES = (
        ('up', '추천'),
        ('down', '비추천'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='votes')
    vote_type = models.CharField(max_length=4, choices=VOTE_CHOICES)
    
    # GenericForeignKey를 사용하여 Post와 Comment 모두에 연결 가능하게 함
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'content_type', 'object_id')
        verbose_name = '투표'
        verbose_name_plural = '투표'
    
    def __str__(self):
        return f"{self.user.username}의 {self.get_vote_type_display()} - {self.content_object}"

class Post(models.Model):
    """게시글 모델"""
    title = models.CharField(max_length=200, verbose_name='제목')
    content = models.TextField(verbose_name='내용')
    content_html = models.TextField(blank=True, null=True, verbose_name='HTML 내용')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0, verbose_name='조회수')
    votes = GenericRelation(Vote, related_query_name='post')
    
    def __str__(self):
        return self.title

    def get_markdown_content(self):
        """마크다운 내용을 HTML로 변환"""
        return markdown.markdown(self.content, extensions=[
            'markdown.extensions.fenced_code',
            'markdown.extensions.tables',
            'markdown.extensions.nl2br',
        ])

    @property
    def upvotes_count(self):
        """추천 수 반환"""
        return self.votes.filter(vote_type='up').count()
    
    @property
    def downvotes_count(self):
        """비추천 수 반환"""
        return self.votes.filter(vote_type='down').count()

    def save(self, *args, **kwargs):
        # 마크다운 변환 로직 추가
        if self.content:
            self.content_html = markdown.markdown(
                self.content,
                extensions=[
                    'markdown.extensions.fenced_code',
                    'markdown.extensions.tables',
                    'markdown.extensions.nl2br',
                    'markdown.extensions.extra'
                ]
            )
        super().save(*args, **kwargs)

class Attachment(models.Model):
    """첨부 파일 모델"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/%Y/%m/%d/')
    filename = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.filename

class Comment(models.Model):
    """댓글 모델"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(verbose_name='내용')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    votes = GenericRelation(Vote, related_query_name='comment')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '댓글'
        verbose_name_plural = '댓글'
    
    def __str__(self):
        return f"{self.author.username}의 댓글: {self.content[:20]}"
    
    @property
    def upvotes_count(self):
        """추천 수 반환"""
        return self.votes.filter(vote_type='up').count()
    
    @property
    def downvotes_count(self):
        """비추천 수 반환"""
        return self.votes.filter(vote_type='down').count()
