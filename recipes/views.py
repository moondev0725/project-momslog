# ═══════════════════════════════════════════════════════════════════════
# recipes/views.py
# 맘스로그 프로젝트 - 요리레시피 게시판 뷰
# ═══════════════════════════════════════════════════════════════════════
# 작성일: 2026-01-06
# ═══════════════════════════════════════════════════════════════════════

from .forms import RecipePostForm, RecipeCommentForm
from .models import RecipePost, RecipeImage, RecipeComment
from board.models import Notification
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Max, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods, require_POST

# ═══════════════════════════════════════════════════════════════════════
# 요리레시피 목록
# ═══════════════════════════════════════════════════════════════════════
def recipe_list(request):
    """
    요리레시피 목록 (카테고리 필터, 검색, 페이지네이션)
    """
    category = request.GET.get('category', 'all')
    search_query = request.GET.get('search', '').strip()
    # 커뮤니티형 필터 칩
    quick = request.GET.get('quick')  # '15'이면 15분 완성
    kid = request.GET.get('kid')      # '1'이면 아이도 먹는
    low = request.GET.get('low')      # '1'이면 재료 적은

    # 기본 쿼리
    posts = RecipePost.objects.all().select_related('author').prefetch_related('images')

    # 카테고리 필터 (생활형 명명 일부 매핑)
    if category and category != 'all':
        # 'main'은 현재 모델에 없으므로 한끼 해결 느낌을 'korean' 중심으로 표시
        if category == 'main':
            posts = posts.filter(category__in=['korean', 'western'])
        elif category == 'simple':
            posts = posts.filter(category='simple')
        else:
            posts = posts.filter(category=category)

    # 검색 필터
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) | Q(content__icontains=search_query)
        )

    # 필터 칩 적용 (모델 확장 전까지 카테고리로 대체)
    if quick == '15':
        posts = posts.filter(category__in=['simple'])
    if kid == '1':
        posts = posts.filter(category='baby')
    if low == '1':
        posts = posts.filter(category__in=['simple', 'diet'])

    posts = posts.order_by('-created_at')

    # 페이지네이션
    paginator = Paginator(posts, 12)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)

    context = {
        'page_obj': page_obj,
        'category': category,
        'search_query': search_query,
        'total_count': posts.count(),
        'quick': quick,
        'kid': kid,
        'low': low,
    }
    return render(request, 'recipes/recipe_list.html', context)


# ═══════════════════════════════════════════════════════════════════════
# 요리레시피 상세
# ═══════════════════════════════════════════════════════════════════════
def recipe_detail(request, pk):
    """
    요리레시피 상세 (조회수 증가, 댓글 목록)
    """
    post = get_object_or_404(RecipePost, pk=pk)

    # 조회수 증가
    post.views += 1
    post.save(update_fields=['views'])

    # 댓글 목록
    comments = (
        post.comments
            .filter(parent__isnull=True)
            .select_related('author')
            .prefetch_related('replies__author')
            .order_by('created_at')
    )

    # 전체 댓글 수
    comment_total_count = post.comments.count()

    # 이미지 목록
    images = post.images.all().order_by('order')

    # 댓글 폼 플레이스홀더 부여 (템플릿에서 직접 attrs 호출 방지)
    comment_form = RecipeCommentForm()
    comment_form.fields['content'].widget.attrs.update({
        'placeholder': '오늘 레시피 어땠는지, 식탁의 순간을 들려주세요 :)'
    })

    context = {
        'post': post,
        'comments': comments,
        'comment_total_count': comment_total_count,
        'images': images,
        'comment_form': comment_form,
    }
    return render(request, 'recipes/recipe_detail.html', context)

# ═══════════════════════════════════════════════════════════════════════
# 요리레시피 작성
# ═══════════════════════════════════════════════════════════════════════
@login_required(login_url='accounts:login')
def recipe_create(request):
    """
    요리레시피 작성 (이미지 최대 10개 업로드)
    """
    if request.method == 'POST':
        form = RecipePostForm(request.POST)
        images = request.FILES.getlist('images')

        if form.is_valid():
            # 이미지 개수 확인
            if len(images) > 10:
                form.add_error(None, '이미지는 최대 10개까지 업로드할 수 있습니다.')
            else:
                post = form.save(commit=False)
                post.author = request.user
                post.save()

                # 이미지 저장
                for idx, image_file in enumerate(images):
                    RecipeImage.objects.create(
                        post=post,
                        image=image_file,
                        order=idx + 1
                    )

                return redirect('recipes:recipe_detail', pk=post.pk)
    else:
        form = RecipePostForm()

    context = {
        'form': form,
        'mode': 'create',
    }
    return render(request, 'recipes/recipe_form.html', context)

# ═══════════════════════════════════════════════════════════════════════
# 요리레시피 수정
# ═══════════════════════════════════════════════════════════════════════
@login_required(login_url='accounts:login')
def recipe_update(request, pk):
    """
    요리레시피 수정
    """
    post = get_object_or_404(RecipePost, pk=pk)

    # 작성자 확인
    if post.author != request.user:
        return redirect('recipes:recipe_detail', pk=pk)

    if request.method == 'POST':
        form = RecipePostForm(request.POST, instance=post)
        images = request.FILES.getlist('images')

        if form.is_valid():
            # 기존 이미지 개수
            existing_images_count = post.images.count()

            # 삭제할 이미지 ID 목록
            delete_image_ids = request.POST.getlist('delete_images')
            if delete_image_ids:
                post.images.filter(id__in=delete_image_ids).delete()
                existing_images_count -= len(delete_image_ids)

            # 새 이미지 개수 확인
            if existing_images_count + len(images) > 10:
                form.add_error(None, f'이미지는 최대 10개까지 업로드할 수 있습니다. (현재: {existing_images_count}개)')
            else:
                post = form.save()

                # 새 이미지 저장
                current_max_order = post.images.aggregate(max_order=Max('order'))['max_order'] or 0
                for idx, image_file in enumerate(images):
                    RecipeImage.objects.create(
                        post=post,
                        image=image_file,
                        order=current_max_order + idx + 1
                    )

                return redirect('recipes:recipe_detail', pk=post.pk)
    else:
        form = RecipePostForm(instance=post)

    context = {
        'form': form,
        'post': post,
        'mode': 'update',
        'images': post.images.all().order_by('order'),
    }
    return render(request, 'recipes/recipe_form.html', context)

# ═══════════════════════════════════════════════════════════════════════
# 요리레시피 삭제
# ═══════════════════════════════════════════════════════════════════════
@login_required(login_url='accounts:login')
def recipe_delete(request, pk):
    """
    요리레시피 삭제
    """
    post = get_object_or_404(RecipePost, pk=pk)

    # 작성자 확인
    if post.author != request.user:
        return redirect('recipes:recipe_detail', pk=pk)

    if request.method == 'POST':
        post.delete()
        return redirect('recipes:recipe_list')

    return redirect('recipes:recipe_detail', pk=pk)

# ═══════════════════════════════════════════════════════════════════════
# 요리레시피 댓글 작성
# ═══════════════════════════════════════════════════════════════════════
@login_required(login_url='accounts:login')
@require_http_methods(["POST"])
def comment_create(request, pk):
    post = get_object_or_404(RecipePost, pk=pk)
    form = RecipeCommentForm(request.POST)

    if not form.is_valid():
        return JsonResponse({"success": False, "message": "댓글 내용을 입력해주세요."}, status=400)

    comment = form.save(commit=False)
    comment.post = post
    comment.author = request.user
    comment.save()

    # (알림 로직은 그대로 두고 싶으면 여기 유지)

    html = render_to_string(
        "recipes/_comment_card.html",
        {"post": post, "comment": comment, "user": request.user},
        request=request
    )
    return JsonResponse({
        "success": True,
        "comment_id": comment.id,
        "html": html,
    })

# ═══════════════════════════════════════════════════════════════════════
# 요리레시피 댓글 삭제
# ═══════════════════════════════════════════════════════════════════════
@login_required(login_url='accounts:login')
@require_http_methods(["POST"])
def comment_delete(request, pk, comment_id):
    post = get_object_or_404(RecipePost, pk=pk)
    comment = get_object_or_404(RecipeComment, pk=comment_id, post=post, parent__isnull=True)

    if comment.author != request.user:
        return JsonResponse({"success": False, "message": "권한이 없습니다."}, status=403)

    # 대댓글까지 같이 삭제(모델이 CASCADE라면 자동이지만, 명시해도 OK)
    comment.delete()
    return JsonResponse({"success": True, "comment_id": comment_id})

# ═══════════════════════════════════════════════════════════════════════
# 요리레시피 댓글 수정
# ═══════════════════════════════════════════════════════════════════════
@login_required(login_url='accounts:login')
def comment_update(request, pk, comment_id):
    if request.method == "POST":
        comment = get_object_or_404(RecipeComment, pk=comment_id)

        # 댓글 작성자가 맞는지 확인
        if comment.author != request.user:
            return JsonResponse({"success": False, "message": "작성자가 아닙니다."}, status=403)

        # 댓글 내용 수정
        new_content = request.POST.get('content', '').strip()
        if new_content:
            comment.content = new_content
            comment.save()
            return JsonResponse({"success": True, "message": "댓글이 수정되었습니다."})
        else:
            return JsonResponse({"success": False, "message": "댓글 내용을 입력해주세요."}, status=400)

    return JsonResponse({"success": False, "message": "잘못된 요청입니다."}, status=400)

# ═══════════════════════════════════════════════════════════════════════
# 요리레시피 대댓글 작성
# ═══════════════════════════════════════════════════════════════════════
@login_required(login_url='accounts:login')
@require_http_methods(["POST"])
def reply_create(request, pk, comment_id):
    post = get_object_or_404(RecipePost, pk=pk)

    parent_comment = get_object_or_404(
        RecipeComment,
        pk=comment_id,
        post=post,
        parent__isnull=True
    )

    form = RecipeCommentForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"success": False, "message": "답글 내용을 입력해주세요."}, status=400)

    reply = form.save(commit=False)
    reply.post = post
    reply.author = request.user
    reply.parent = parent_comment
    reply.save()

    html = render_to_string(
        "recipes/_reply_card.html",
        {"post": post, "reply": reply, "parent_id": parent_comment.id, "user": request.user},
        request=request
    )

    reply_count = parent_comment.replies.count()

    return JsonResponse({
        "success": True,
        "reply_id": reply.id,
        "parent_id": parent_comment.id,
        "reply_count": reply_count,
        "html": html,
    })

# ═══════════════════════════════════════════════════════════════════════
# 요리레시피 대댓글 삭제
# ═══════════════════════════════════════════════════════════════════════
@login_required(login_url='accounts:login')
@require_http_methods(["POST"])
def reply_delete(request, pk, comment_id, reply_id):
    post = get_object_or_404(RecipePost, pk=pk)
    parent_comment = get_object_or_404(RecipeComment, pk=comment_id, post=post, parent__isnull=True)
    reply = get_object_or_404(RecipeComment, pk=reply_id, post=post, parent=parent_comment)

    if reply.author != request.user:
        return JsonResponse({"success": False, "message": "권한이 없습니다."}, status=403)

    reply.delete()
    reply_count = parent_comment.replies.count()

    return JsonResponse({
        "success": True,
        "reply_id": reply_id,
        "parent_id": parent_comment.id,
        "reply_count": reply_count,
    })

# ═══════════════════════════════════════════════════════════════════════
# 요리레시피 대댓글 수정
# ═══════════════════════════════════════════════════════════════════════
@login_required(login_url='accounts:login')
def reply_update(request, pk, comment_id, reply_id):
    if request.method == "POST":
        reply = get_object_or_404(RecipeComment, pk=reply_id, parent_id=comment_id)

        if reply.author != request.user:
            return JsonResponse({"success": False, "message": "작성자가 아닙니다."}, status=403)

        new_content = request.POST.get('content', '').strip()
        if new_content:
            reply.content = new_content
            reply.save()
            return JsonResponse({"success": True, "message": "대댓글이 수정되었습니다."})
        else:
            return JsonResponse({"success": False, "message": "내용을 입력해주세요."}, status=400)

    return JsonResponse({"success": False, "message": "잘못된 요청입니다."}, status=400)
