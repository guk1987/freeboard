from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Board, Post, Comment, Attachment
from .forms import PostForm, CommentForm  # 아직 만들지 않음

def home(request):
    """홈 페이지"""
    boards = Board.objects.all()
    recent_posts = Post.objects.order_by('-created_at')[:10]
    return render(request, 'board/home.html', {
        'boards': boards,
        'recent_posts': recent_posts
    })

def board_detail(request, board_id):
    """게시판 상세 페이지"""
    board = get_object_or_404(Board, id=board_id)
    posts = board.posts.order_by('-created_at')
    return render(request, 'board/board_detail.html', {
        'board': board,
        'posts': posts
    })

@login_required
def post_create(request):
    """게시글 작성"""
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            
            # 첨부 파일 처리
            for file in request.FILES.getlist('files'):
                Attachment.objects.create(
                    post=post,
                    file=file,
                    filename=file.name
                )
            
            messages.success(request, '게시글이 작성되었습니다.')
            return redirect('board:post_detail', post_id=post.id)
    else:
        form = PostForm()
    
    return render(request, 'board/post_form.html', {'form': form})

def post_detail(request, post_id):
    """게시글 상세 페이지"""
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.order_by('created_at')
    comment_form = CommentForm()
    
    # 조회수 증가
    post.view_count += 1
    post.save()
    
    return render(request, 'board/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form
    })

@login_required
def post_edit(request, post_id):
    """게시글 수정"""
    post = get_object_or_404(Post, id=post_id)
    
    # 작성자만 수정 가능
    if post.author != request.user:
        messages.error(request, '게시글을 수정할 권한이 없습니다.')
        return redirect('board:post_detail', post_id=post.id)
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            
            # 첨부 파일 처리
            for file in request.FILES.getlist('files'):
                Attachment.objects.create(
                    post=post,
                    file=file,
                    filename=file.name
                )
            
            messages.success(request, '게시글이 수정되었습니다.')
            return redirect('board:post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)
    
    return render(request, 'board/post_form.html', {
        'form': form,
        'post': post
    })

@login_required
def post_delete(request, post_id):
    """게시글 삭제"""
    post = get_object_or_404(Post, id=post_id)
    
    # 작성자만 삭제 가능
    if post.author != request.user:
        messages.error(request, '게시글을 삭제할 권한이 없습니다.')
        return redirect('board:post_detail', post_id=post.id)
    
    if request.method == 'POST':
        board_id = post.board.id
        post.delete()
        messages.success(request, '게시글이 삭제되었습니다.')
        return redirect('board:board_detail', board_id=board_id)
    
    return render(request, 'board/post_confirm_delete.html', {'post': post})

@login_required
def comment_create(request, post_id):
    """댓글 작성"""
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, '댓글이 작성되었습니다.')
    
    return redirect('board:post_detail', post_id=post.id)
