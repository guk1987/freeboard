from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Board, Post, Comment, Attachment, Vote
from .forms import PostForm, CommentForm  # 아직 만들지 않음
import markdown
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db import models
from django.db.models import Count, Q, Case, When, IntegerField
from django.urls import reverse

def home(request):
    # 오늘 날짜
    today = timezone.now().date().strftime("%Y-%m-%d")
    
    # 최신 게시글 5개 가져오기
    latest_posts = Post.objects.all().order_by('-created_at')[:5]
    
    # 인기 게시판 (게시글 수로 정렬)
    boards = Board.objects.annotate(
        post_count=Count('post')
    ).order_by('-post_count')[:5]
    
    # 각 게시판에 최신 게시글 추가
    for board in boards:
        board.latest_post = Post.objects.filter(board=board).order_by('-created_at').first()
    
    context = {
        'latest_posts': latest_posts,
        'boards': boards,
        'today': today,
    }
    
    return render(request, 'board/home.html', context)

def board_detail(request, board_id):
    today = timezone.now().date().strftime("%Y-%m-d")
    
    # 특정 게시판 조회
    board = get_object_or_404(Board, id=board_id)
    
    # 해당 게시판의 게시글 조회 (최신순)
    posts = Post.objects.filter(board=board).order_by('-created_at')
    
    # 각 게시글의 투표 수 계산
    for post in posts:
        post.upvotes_count = Vote.objects.filter(post=post, vote_type='up').count()
    
    # 게시글 페이지네이션
    paginator = Paginator(posts, 10)  # 페이지당 10개씩
    page_number = request.GET.get('page', 1)
    posts = paginator.get_page(page_number)
    
    context = {
        'board': board,
        'posts': posts,
        'today': today,
    }
    
    return render(request, 'board/board_detail.html', context)

def post_list(request):
    today = timezone.now().date().strftime("%Y-%m-d")
    
    # 모든 게시글 조회 (최신순)
    posts = Post.objects.all().order_by('-created_at')
    
    # 각 게시글의 투표 수 계산
    for post in posts:
        post.upvotes_count = Vote.objects.filter(post=post, vote_type='up').count()
    
    # 게시글 페이지네이션
    paginator = Paginator(posts, 10)  # 페이지당 10개씩
    page_number = request.GET.get('page', 1)
    posts = paginator.get_page(page_number)
    
    # 모든 게시판 목록 (필터링용)
    boards = Board.objects.all()
    
    context = {
        'posts': posts,
        'boards': boards,
        'today': today,
    }
    
    return render(request, 'board/post_list.html', context)

@login_required
def post_create(request):
    board_id = request.GET.get('board')
    
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, '게시글이 작성되었습니다.')
            return redirect('board:post_detail', pk=post.pk)
    else:
        form = PostForm()
        if board_id:
            form.fields['board'].initial = board_id
    
    return render(request, 'board/post_form.html', {'form': form})

def post_detail(request, pk):
    """게시글 상세 페이지"""
    post = get_object_or_404(Post, pk=pk)
    
    # 조회수 증가 (중복 방지 로직 추가 가능)
    post.views += 1
    post.save()
    
    # 댓글 처리
    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, '댓글이 작성되었습니다.')
            return redirect('board:post_detail', pk=pk)
    else:
        form = CommentForm()
    
    # 사용자의 투표 상태 확인
    user_vote = None
    if request.user.is_authenticated:
        vote = Vote.objects.filter(user=request.user, post=post).first()
        if vote:
            user_vote = vote.vote_type
    
    # 댓글에 대한 사용자 투표 상태 추가
    comments = post.comments.all()
    for comment in comments:
        comment.user_vote = None
        if request.user.is_authenticated:
            comment_vote = Vote.objects.filter(user=request.user, comment=comment).first()
            if comment_vote:
                comment.user_vote = comment_vote.vote_type
    
    # 투표 수 계산
    post.upvotes_count = Vote.objects.filter(post=post, vote_type='up').count()
    post.downvotes_count = Vote.objects.filter(post=post, vote_type='down').count()
    
    context = {
        'post': post,
        'form': form,
        'user_vote': user_vote,
        'comments': comments,
        'today': timezone.now().date().strftime("%Y-%m-%d")
    }
    
    return render(request, 'board/post_detail.html', context)

@login_required
def post_edit(request, pk):
    """게시글 수정"""
    post = get_object_or_404(Post, pk=pk)
    
    if post.author != request.user:
        messages.error(request, '자신의 게시글만 수정할 수 있습니다.')
        return redirect('board:post_detail', pk=post.pk)
    
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
            return redirect('board:post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    
    return render(request, 'board/post_form.html', {
        'form': form,
        'post': post
    })

@login_required
def post_delete(request, pk):
    """게시글 삭제"""
    post = get_object_or_404(Post, pk=pk)
    
    if post.author != request.user:
        messages.error(request, '자신의 게시글만 삭제할 수 있습니다.')
        return redirect('board:post_detail', pk=post.pk)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, '게시글이 삭제되었습니다.')
        
        # 게시판이 있으면 해당 게시판으로, 없으면 홈으로
        if post.board:
            return redirect('board:board_detail', board_id=post.board.id)
        else:
            return redirect('board:home')
    
    return render(request, 'board/post_confirm_delete.html', {'post': post})

@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    
    # 댓글 작성자만 삭제 가능
    if request.user != comment.author:
        messages.error(request, '댓글 작성자만 삭제할 수 있습니다.')
        return redirect('board:post_detail', pk=comment.post.pk)
    
    post_id = comment.post.id
    comment.delete()
    messages.success(request, '댓글이 삭제되었습니다.')
    return redirect('board:post_detail', pk=post_id)

@login_required
def comment_create(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, '댓글이 작성되었습니다.')
    
    return redirect('board:post_detail', pk=post_id)

@login_required
def vote_object(request):
    """게시물 또는 댓글에 추천/비추천 투표"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        object_type = request.POST.get('type')
        object_id = request.POST.get('id')
        vote_type = request.POST.get('vote_type')
        
        # 유효성 검사
        if not all([object_type, object_id, vote_type]) or vote_type not in ['up', 'down']:
            return JsonResponse({'status': 'error', 'message': '잘못된 요청입니다.'}, status=400)
        
        # 객체 타입에 따라 ContentType 가져오기
        if object_type == 'post':
            content_type = ContentType.objects.get_for_model(Post)
            obj = get_object_or_404(Post, id=object_id)
        elif object_type == 'comment':
            content_type = ContentType.objects.get_for_model(Comment)
            obj = get_object_or_404(Comment, id=object_id)
        else:
            return JsonResponse({'status': 'error', 'message': '지원하지 않는 객체 타입입니다.'}, status=400)
        
        # 이미 투표한 경우 확인
        existing_vote = Vote.objects.filter(
            user=request.user,
            content_type=content_type,
            object_id=object_id
        ).first()
        
        if existing_vote:
            # 같은 타입의 투표를 다시 누른 경우 -> 투표 취소
            if existing_vote.vote_type == vote_type:
                existing_vote.delete()
                action = 'removed'
            # 다른 타입의 투표를 누른 경우 -> 투표 타입 변경
            else:
                existing_vote.vote_type = vote_type
                existing_vote.save()
                action = 'changed'
        else:
            # 새로운 투표 생성
            Vote.objects.create(
                user=request.user,
                content_type=content_type,
                object_id=object_id,
                vote_type=vote_type
            )
            action = 'added'
        
        # 현재 추천/비추천 수 계산
        upvotes = obj.upvotes_count
        downvotes = obj.downvotes_count
        
        # 현재 사용자의 투표 상태 확인
        current_vote = Vote.objects.filter(
            user=request.user,
            content_type=content_type,
            object_id=object_id
        ).first()
        
        user_vote = current_vote.vote_type if current_vote else None
        
        return JsonResponse({
            'status': 'success',
            'action': action,
            'upvotes': upvotes,
            'downvotes': downvotes,
            'user_vote': user_vote
        })
    
    return JsonResponse({'status': 'error', 'message': '잘못된 요청입니다.'}, status=400)

def all_boards(request):
    today = timezone.now().date().strftime("%Y-%m-d")
    
    # 모든 게시판 조회
    boards = Board.objects.annotate(
        post_count=Count('post')
    ).order_by('name')
    
    # 각 게시판에 최신 게시글 추가
    for board in boards:
        board.latest_post = Post.objects.filter(board=board).order_by('-created_at').first()
    
    context = {
        'boards': boards,
        'today': today,
    }
    
    return render(request, 'board/all_boards.html', context)

# 게시글 투표 뷰 함수
@login_required
def post_vote(request, post_id, vote_type):
    post = get_object_or_404(Post, id=post_id)
    
    # 자신의 게시글에는 투표할 수 없음
    if post.author == request.user:
        messages.error(request, '자신의 게시글에는 투표할 수 없습니다.')
        return redirect('board:post_detail', pk=post_id)
    
    # 이미 투표한 경우, 투표 취소 또는 변경
    try:
        vote = Vote.objects.get(user=request.user, post=post)
        
        # 같은 유형으로 다시 투표하면 취소
        if vote.vote_type == vote_type:
            vote.delete()
            messages.success(request, '투표가 취소되었습니다.')
        # 다른 유형으로 투표하면 변경
        else:
            vote.vote_type = vote_type
            vote.save()
            messages.success(request, '투표가 변경되었습니다.')
    
    # 처음 투표하는 경우
    except Vote.DoesNotExist:
        Vote.objects.create(
            user=request.user,
            post=post,
            vote_type=vote_type
        )
        messages.success(request, '투표가 완료되었습니다.')
    
    # AJAX 요청인 경우 JSON 응답
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        upvotes = Vote.objects.filter(post=post, vote_type='up').count()
        downvotes = Vote.objects.filter(post=post, vote_type='down').count()
        
        return JsonResponse({
            'upvotes': upvotes,
            'downvotes': downvotes
        })
    
    # 일반 요청인 경우 리디렉션
    return redirect('board:post_detail', pk=post_id)

# 댓글 투표 뷰 함수
@login_required
def comment_vote(request, comment_id, vote_type):
    comment = get_object_or_404(Comment, id=comment_id)
    post_id = comment.post.id
    
    # 자신의 댓글에는 투표할 수 없음
    if comment.author == request.user:
        messages.error(request, '자신의 댓글에는 투표할 수 없습니다.')
        return redirect('board:post_detail', pk=post_id)
    
    # 이미 투표한 경우, 투표 취소 또는 변경
    try:
        vote = Vote.objects.get(user=request.user, comment=comment)
        
        # 같은 유형으로 다시 투표하면 취소
        if vote.vote_type == vote_type:
            vote.delete()
            messages.success(request, '투표가 취소되었습니다.')
        # 다른 유형으로 투표하면 변경
        else:
            vote.vote_type = vote_type
            vote.save()
            messages.success(request, '투표가 변경되었습니다.')
    
    # 처음 투표하는 경우
    except Vote.DoesNotExist:
        Vote.objects.create(
            user=request.user,
            comment=comment,
            vote_type=vote_type
        )
        messages.success(request, '투표가 완료되었습니다.')
    
    # AJAX 요청인 경우 JSON 응답
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        upvotes = Vote.objects.filter(comment=comment, vote_type='up').count()
        
        return JsonResponse({
            'upvotes': upvotes
        })
    
    # 일반 요청인 경우 리디렉션
    return redirect('board:post_detail', pk=post_id)
