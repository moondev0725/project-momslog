# ═══════════════════════════════════════════════════════════════════════
# board/views.py
# 맘스로그 프로젝트 - 게시판 뷰 (공지사항, 자유게시판, 벼룩시장)
# ═══════════════════════════════════════════════════════════════════════
# 작성일: 2025-12-29
# 기능:
#   [공지사항] notice_list, notice_detail, notice_write (관리자 전용)
#   [자유게시판] free_list, free_create
#   [벼룩시장] flea_list, flea_detail, flea_create, flea_edit, flea_delete
#   [벼룩시장 찜] flea_like_toggle (25-12-29 추가)
#   [벼룩시장 댓글] flea_comment_create, flea_comment_edit, flea_comment_delete (25-12-29 추가)
#   [벼룩시장 검색] flea_list에 통합 (제목, 내용, 작성자 검색)
# ═══════════════════════════════════════════════════════════════════════

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.db.models import Q, F
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Notice, FreePost, FreeComment, FleaItem, FleaComment, FleaReport, Notification, FreePostReaction, HotDeal, ParentingInfo, ParentingComment, ParentingImage, PetPost, PetComment, MomDiary, DiaryEntry
from .forms import NoticeForm, FreePostForm, FleaItemForm, FleaCommentForm, FleaReportForm
from django.contrib.auth.decorators import login_required
from datetime import datetime
from urllib.parse import urlencode
from django.contrib import messages
from django.db import transaction
from .models import FreePost, FreePostAttachment
from django.db.models import Count, F, IntegerField, Value, Case, When, BooleanField
from django.db.models.functions import Coalesce
from django.utils import timezone

# 1. 목록 보기
def notice_list(request):
    notices = Notice.objects.all().order_by('-created_at') # 최신글 순서
    return render(request, 'board/notice_list.html', {'notices': notices})

# 2. 상세 보기
def notice_detail(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    
    # 조회수 +1 증가
    notice.view_count += 1
    notice.save()
    
    return render(request, 'board/notice_detail.html', {'notice': notice})

# ★ 글쓰기 기능 추가
@login_required # 로그인은 필수
def notice_write(request):
    # 관리자가 아니면 메인으로 쫓아냄
    if not request.user.is_staff:
        return redirect('board:notice_list')

    if request.method == 'POST':
        form = NoticeForm(request.POST)
        if form.is_valid():
            notice = form.save(commit=False)
            # notice.writer = request.user  # (작성자 필드가 있다면 추가)
            notice.save()
            return redirect('board:notice_list')
    else:
        form = NoticeForm()
    
    return render(request, 'board/notice_write.html', {'form': form})




# ▼▼▼ [자유게시판] ▼▼▼ ============================================================
# 25-12-31 혜은 : 게시글 상세보기 추가

# 1. 자유게시판 목록 보기
def free_list(request):
    selected_category = request.GET.get("category", "all")
    sort = request.GET.get("sort", "latest")  
    # latest / views / comments

    # 1) 카테고리 필터
    if selected_category == "all":
        qs = FreePost.objects.all()
    else:
        qs = FreePost.objects.filter(category=selected_category)

    # 인기글 기준 (공감 합계 10 이상)
    POPULAR_THRESHOLD = 10

    # 2) 댓글수 + 공감합계 (annotate)
    qs = qs.annotate(
        cmt_cnt=Count("comments", distinct=True),
        react_cnt=(
            Coalesce(F("reaction_empathy"), Value(0), output_field=IntegerField()) +
            Coalesce(F("reaction_courage"), Value(0), output_field=IntegerField()) +
            Coalesce(F("reaction_cheer"), Value(0), output_field=IntegerField()) +
            Coalesce(F("reaction_support"), Value(0), output_field=IntegerField()) +
            Coalesce(F("reaction_thanks"), Value(0), output_field=IntegerField())
        )
    )
    
    # 🔥 인기글 플래그
    qs = qs.annotate(
        is_popular=Case(
            When(react_cnt__gte=POPULAR_THRESHOLD, then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        )
    )

    # 3) 정렬
    if sort == "views":
        qs = qs.order_by("-views", "-created_at")          # 조회수순
    elif sort == "comments":
        qs = qs.order_by("-cmt_cnt", "-created_at")        # 댓글순
    elif sort == "popular":
        qs = qs.order_by("-react_cnt", "-created_at")     # ⭐ 인기순(공감합계)
    else:
        qs = qs.order_by("-created_at")                    # 최신순

    # 4) 페이지네이션
    paginator = Paginator(qs, 5)
    page_obj = paginator.get_page(request.GET.get("page", 1))
    
    # 오늘날짜 게시글 표시용
    today = timezone.localdate()

    # 🔥 오늘 글 여부 표시 (NEW)
    for post in page_obj:
        post.is_new_today = (post.created_at.date() == today)

    context = {
        "posts": page_obj,
        "page_obj": page_obj,
        "selected_category": selected_category,
        "sort": sort,
        "total_count": qs.count(),
    }
    return render(request, "board/free_list.html", context)

# 글쓰기페이지로 이동
def free_write(request):
    return render(request, "board/free_write.html")

# 2. 글쓰기 (로그인한 사람만 가능)  ==== 26-01-07 혜은 추가 ====
@login_required(login_url='accounts:login')
def free_create(request):
    if request.method == "POST":
        print("🔥 free_create HIT:", request.method, request.path)
        print("🔥 POST category =", request.POST.get("category"))

        form = FreePostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user

            # ✅ 핵심: 사용자가 선택한 category는 cleaned_data로 저장
            post.category = form.cleaned_data["category"]

            post.save()
            return redirect(f"{reverse('board:free_list')}?category={post.category}")

        # 폼 에러나면 다시 렌더링
        return render(request, "board/free_write.html", {"form": form})

    # POST가 아니면 글쓰기 페이지로 보내기
    return redirect(f"{reverse('board:free_write')}?category=mom")

# 3. 상세 보기                                    ==== 25-12-31 혜은 추가 ====
def free_detail(request, pk):
    # 상세에 보여줄 글 하나
    post = get_object_or_404(FreePost, pk=pk)

    # ✅ 조회수 증가 (안전한 방식)
    FreePost.objects.filter(pk=pk).update(views=F('views') + 1)
    post.refresh_from_db()

    # =========================================================
    # ✅ 이전글/다음글 (같은 카테고리 기준)
    # =========================================================
    if post.category:
        same_category = FreePost.objects.filter(category=post.category).order_by('-created_at')
    else:
        same_category = FreePost.objects.all().order_by('-created_at')

    # 이전글(더 최근 글)
    prev_post = same_category.filter(created_at__gt=post.created_at).order_by('created_at').first()

    # 다음글(더 오래된 글)
    next_post = same_category.filter(created_at__lt=post.created_at).order_by('-created_at').first()

    # =========================================================
    # ✅ 상세 페이지 하단 "자유게시판 목록" (기존 유지)
    # =========================================================
    selected_category = request.GET.get('category', 'all')

    if selected_category == 'all':
        qs = FreePost.objects.all().order_by('-created_at')
    else:
        qs = FreePost.objects.filter(category=selected_category).order_by('-created_at')

    total_count = qs.count()

    per_page = 5
    paginator = Paginator(qs, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # 게시글 번호 계산
    start_number = total_count - per_page * (page_obj.number - 1)
    for idx, item in enumerate(page_obj.object_list):
        item.number = start_number - idx

    # 게시글 페이지 번호 범위 (이미지처럼 5개 묶음)
    total_pages = paginator.num_pages
    current_page = page_obj.number
    start_page = max(1, current_page - 2)
    end_page = min(total_pages, start_page + 4)
    if end_page - start_page < 4:
        start_page = max(1, end_page - 4)

    # =========================================================
    # ✅ 댓글 5개씩 페이지네이션 (cpage 사용)
    # =========================================================
    comments_qs = post.comments.select_related('author').order_by("-created_at")
    comment_paginator = Paginator(comments_qs, 3)
    cpage = request.GET.get("cpage", 1)
    comment_page_obj = comment_paginator.get_page(cpage)

    # ✅ 댓글 페이지 번호 범위 (이미지처럼 5개 묶음)
    c_total_pages = comment_paginator.num_pages
    c_current_page = comment_page_obj.number
    c_start_page = max(1, c_current_page - 2)
    c_end_page = min(c_total_pages, c_start_page + 4)
    if c_end_page - c_start_page < 4:
        c_start_page = max(1, c_end_page - 4)

    # =========================================================
    # ✅ 같은 카테고리 글 5개씩 페이지네이션 (rpage 사용)  ← 핵심 수정
    # =========================================================
    related_qs = (
        FreePost.objects
        .filter(category=post.category)
        .exclude(pk=post.pk)
        .order_by("-created_at")
    )

    related_paginator = Paginator(related_qs, 5)
    rpage = request.GET.get("rpage", 1)
    related_page_obj = related_paginator.get_page(rpage)

    # ✅ 같은 카테고리 글 페이지 번호 범위 (이미지처럼 5개 묶음)
    r_total_pages = related_paginator.num_pages
    r_current_page = related_page_obj.number
    r_start_page = max(1, r_current_page - 2)
    r_end_page = min(r_total_pages, r_start_page + 4)
    if r_end_page - r_start_page < 4:
        r_start_page = max(1, r_end_page - 4)

    # 목록 복귀용 page
    list_page = request.GET.get("page", 1)

    context = {
        'post': post,

        # 상세 하단 자유게시판 목록(기존 유지)
        'posts': page_obj,
        'page_obj': page_obj,
        'total_count': total_count,
        'selected_category': selected_category,
        'start_page': start_page,
        'end_page': end_page,

        # ✅ 댓글(수정)
        'comment_page_obj': comment_page_obj,
        'c_start_page': c_start_page,
        'c_end_page': c_end_page,

        # ✅ 같은 카테고리 글(페이지네이션) ← related_posts 대신
        'related_page_obj': related_page_obj,
        'r_start_page': r_start_page,
        'r_end_page': r_end_page,

        # 이전/다음글(기존 유지)
        'prev_post': prev_post,
        'next_post': next_post,

        # 템플릿에서 링크 유지용(추가)
        'list_page': list_page,
    }

    return render(request, 'board/free_detail.html', context)

# 4. 댓글 작성(저장) - 자유게시판
@login_required
@require_POST
def free_comment_create(request, post_id):
    post = get_object_or_404(FreePost, id=post_id)

    content = (request.POST.get("content") or "").strip()
    if content:
        FreeComment.objects.create(
            post=post,
            author=request.user,
            content=content
        )

    category = request.GET.get('category', 'all')
    page = request.GET.get('page', 1)
    comment_page = request.GET.get('comment_page', 1)
    url = reverse("board:free_detail", args=[post_id])
    return redirect(f"{reverse('board:free_detail', args=[post_id])}?category={category}&page={page}&comment_page={comment_page}")

# 5. 댓글 수정
@login_required
def free_comment_update(request, comment_id):
    comment = get_object_or_404(FreeComment, id=comment_id)

    # 권한 체크
    if request.user != comment.author and not request.user.is_staff:
        return redirect('board:free_detail', comment.post.id)

    # 수정 저장
    if request.method == "POST":
        content = (request.POST.get("content") or "").strip()
        if content:
            comment.content = content
            comment.save()

    # ✅ 쿼리스트링 유지 (category / page / comment_page)
    query = {}
    category = request.GET.get("category")
    page = request.GET.get("page")
    comment_page = request.GET.get("comment_page")  # ✅ 추가

    if category:
        query["category"] = category
    if page:
        query["page"] = page
    if comment_page:
        query["comment_page"] = comment_page  # ✅ 추가

    url = reverse('board:free_detail', args=[comment.post.id])
    if query:
        url += "?" + urlencode(query)

    # ✅ 수정 후 댓글 영역으로 이동 (원하면 특정 댓글로도 가능)
    url += "#comments-section"
    return redirect(url)


# 6. 댓글 삭제
@login_required
@require_POST
def free_comment_delete(request, comment_id):
    comment = get_object_or_404(FreeComment, id=comment_id)
    post_id = comment.post.id

    if request.user == comment.author or request.user.is_staff:
        comment.delete()

    category = request.GET.get("category", "all")
    page = request.GET.get("page", 1)
    comment_page = request.GET.get("comment_page", 1)

    url = reverse("board:free_detail", args=[post_id])
    return redirect(f"{url}?category={category}&page={page}&comment_page={comment_page}#comments-section")

# 4. 수정하기                                   ==== 26-01-07 혜은 추가 ====
@login_required
def free_update(request, pk):
    post = get_object_or_404(FreePost, pk=pk)

    # 권한 체크
    if request.user != post.author and not request.user.is_staff:
        return redirect("board:free_detail", pk=pk)

    if request.method == "POST":
        post.title = request.POST.get("title", "").strip()
        post.content = request.POST.get("content", "").strip()
        post.save()  # ✅ 기존 글 수정

        category = request.GET.get("category", "all")
        page = request.GET.get("page", 1)
        return redirect(f"/board/free/{pk}/?category={category}&page={page}")

    return render(request, "board/free_update.html", {"post": post})

# 5. 삭제하기                                   ==== 25-12-31 혜은 추가 ====
@login_required(login_url='accounts:login')
def free_delete(request, pk):
    post = get_object_or_404(FreePost, pk=pk)

    # 작성자 또는 관리자만 삭제 가능
    if request.user != post.author and not request.user.is_staff:
        return redirect('board:free_detail', pk=pk)

    if request.method == 'POST':
        post.delete()
        return redirect('board:free_list')

    # GET으로 들어오면 그냥 상세로 돌려보냄
    return redirect('board:free_detail', pk=pk)


# 6. 감정 리액션 추가/제거 (AJAX)              ==== 26-01-02 추가 ====
def free_reaction_toggle(request, pk):
    """
    AJAX로 감정 리액션을 토글합니다.
    POST 요청: reaction_type=empathy|courage|cheer|support|thanks
    """
    # 로그인 확인
    if not request.user.is_authenticated:
        return JsonResponse({'error': '로그인 필요'}, status=401)
    
    # POST 요청 확인
    if request.method != 'POST':
        return JsonResponse({'error': 'POST 요청만 허용'}, status=400)
    
    post = get_object_or_404(FreePost, pk=pk)
    reaction_type = request.POST.get('reaction_type', '').strip()
    
    # 유효한 리액션 타입 확인
    valid_types = ['empathy', 'courage', 'cheer', 'support', 'thanks']
    if reaction_type not in valid_types:
        return JsonResponse({'error': '유효하지 않은 리액션 타입'}, status=400)
    
    # 필드명 매핑
    field_map = {
        'empathy': 'reaction_empathy',
        'courage': 'reaction_courage',
        'cheer': 'reaction_cheer',
        'support': 'reaction_support',
        'thanks': 'reaction_thanks',
    }
    field_name = field_map[reaction_type]
    
    # 기존 리액션 확인
    reaction, created = FreePostReaction.objects.get_or_create(
        post=post,
        user=request.user,
        reaction_type=reaction_type
    )
    
    # 이미 있으면 제거 (토글)
    if not created:
        reaction.delete()
        # 카운트 감소
        setattr(post, field_name, max(0, getattr(post, field_name) - 1))
        is_active = False
    else:
        # 새로 추가되면 카운트 증가
        setattr(post, field_name, getattr(post, field_name) + 1)
        is_active = True
    
    post.save()
    
    # 현재 리액션 카운트 반환
    return JsonResponse({
        'success': True,
        'is_active': is_active,
        'counts': {
            'empathy': post.reaction_empathy,
            'courage': post.reaction_courage,
            'cheer': post.reaction_cheer,
            'support': post.reaction_support,
            'thanks': post.reaction_thanks,
        }
    })
# 게시물 첨부파일 추가
MAX_FILES = 5

@login_required(login_url='accounts:login')
@transaction.atomic
def free_create(request):
    if request.method == "POST":
        # ✅ 파일 포함해서 폼 생성 (이거 안 하면 이미지 업로드 절대 안 됨)
        form = FreePostForm(request.POST, request.FILES)

        # ✅ 첨부파일들 (input name="files" 기준)
        files = request.FILES.getlist("files")

        # ✅ 첨부파일 개수 제한
        if len(files) > MAX_FILES:
            messages.error(request, f"첨부파일은 최대 {MAX_FILES}개까지 업로드 가능합니다.")
            return render(request, "board/free_write.html", {"form": form})

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user

            # ✅ 카테고리는 폼 검증값 그대로 저장
            post.category = form.cleaned_data["category"]

            # ✅ 익명 체크 반영
            post.is_anonymous = request.POST.get("is_anonymous") == "on"

            post.save()

            # ✅ 첨부 저장 (FreePostAttachment 모델 사용)
            for f in files:
                FreePostAttachment.objects.create(post=post, file=f)

            # ✅ 저장 후 해당 카테고리 목록으로 이동
            return redirect(f"{reverse('board:free_list')}?category={post.category}")

        # 폼 에러면 다시 렌더링
        return render(request, "board/free_write.html", {"form": form})

    # GET: 글쓰기 페이지 진입 시 category 기본 선택
    selected_category = request.GET.get("category", "mom")
    form = FreePostForm(initial={"category": selected_category})
    return render(request, "board/free_write.html", {"form": form})
# =============================================================================

# 25-12-30 민혁 추가-----------------------------------------
# ▼▼▼ [반려동물 게시판 뷰] ▼▼▼
def pet_list(request):
    from django.db.models import Q
    
    search_query = request.GET.get('search', '')
    
    # 기본 쿼리셋
    posts = PetPost.objects.all().order_by('-created_at')
    
    # 검색 기능
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) | Q(content__icontains=search_query)
        )
    
    # 페이지네이션
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    # 각 게시물에 번호 추가
    if posts:
        start_num = paginator.count - (posts.start_index() - 1)
        for idx, post in enumerate(posts):
            post.number = start_num - idx
    
    return render(request, 'board/pet_list.html', {
        'posts': posts,
        'search_query': search_query,
    })
    
# 25-12-30 민혁 추가-----------------------------------------    
# ▼▼▼ [반려동물 게시판 글쓰기] ▼▼▼
@login_required(login_url='accounts:login')
def pet_write(request):
    from .models import PetImage
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')

        # 게시글 생성
        post = PetPost.objects.create(
            title=title,
            content=content,
            author=request.user
        )

        # 이미지 처리 (최대 10개)
        images = request.FILES.getlist('images')
        for idx, image in enumerate(images[:10]):  # 최대 10개까지만
            PetImage.objects.create(
                post=post,
                image=image,
                order=idx
            )

        return redirect('board:pet_list')

    return render(request, 'board/pet_write.html')
# ▼▼▼ [반려동물 게시판 상세보기] ▼▼▼
def pet_detail(request, pk):
    post = get_object_or_404(PetPost, pk=pk)

    # 조회수 증가 (F() 사용 → 동시성 안전)
    PetPost.objects.filter(pk=pk).update(views=F('views') + 1)
    post.refresh_from_db()

    return render(request, 'board/pet_detail.html', {
        'post': post
    })
# 25-12-30 민혁 추가-----------------------------------------
@login_required(login_url='accounts:login')
def pet_edit(request, pk):
    """
    반려동물 게시판 글 수정 (작성자만 가능)
    """
    from .models import PetImage
    
    post = get_object_or_404(PetPost, pk=pk)

    if request.user != post.author:
        return redirect('board:pet_detail', pk=pk)

    if request.method == 'POST':
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        post.save()
        
        # 삭제할 이미지 처리
        delete_image_ids = request.POST.getlist('delete_images')
        if delete_image_ids:
            PetImage.objects.filter(id__in=delete_image_ids, post=post).delete()
        
        # 새 이미지 추가
        new_images = request.FILES.getlist('images')
        existing_image_count = post.images.count()
        
        for idx, image in enumerate(new_images):
            if existing_image_count + idx < 10:  # 최대 10개까지만
                PetImage.objects.create(
                    post=post,
                    image=image,
                    order=existing_image_count + idx
                )
        
        return redirect('board:pet_detail', pk=pk)

    return render(request, 'board/pet_edit.html', {'post': post})

#25-12-31 민혁 추가-----------------------------------------
#▼▼▼ [반려동물 게시판 삭제] ▼▼▼
@login_required(login_url='accounts:login')
def pet_delete(request, pk):
    post = get_object_or_404(PetPost, pk=pk)

    if request.user != post.author:
        return redirect('board:pet_detail', pk=pk)

    if request.method == 'POST':
        post.delete()
        return redirect('board:pet_list')

    # GET 요청은 상세보기로 돌려보냄
    return redirect('board:pet_detail', pk=pk)

# ─────────────────────────────────────────
# 반려동물 게시판 댓글 작성
# ─────────────────────────────────────────
@login_required(login_url='accounts:login')
def pet_comment_create(request, pk):
    post = get_object_or_404(PetPost, pk=pk)

    if request.method == 'POST':
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')

        comment = PetComment.objects.create(
            post=post,
            author=request.user,
            content=content,
            parent_id=parent_id if parent_id else None
        )
        
        # ✅ 글 작성자에게 댓글 알림 생성
        if post.author != request.user:
            Notification.objects.create(
                user=post.author,
                pet_post=post,
                message=f"{request.user.nickname}님이 댓글을 남겼습니다.",
                is_read=False
            )

    return redirect('board:pet_detail', pk=pk)

# ─────────────────────────────────────────
# 반려동물 게시판 댓글 삭제 (POST 전용)
# ─────────────────────────────────────────
@login_required(login_url='accounts:login')
def pet_comment_delete(request, pk, comment_id):
    post = get_object_or_404(PetPost, pk=pk)
    comment = get_object_or_404(PetComment, pk=comment_id, post=post)

    # 작성자만 삭제 가능
    if request.user != comment.author:
        return redirect('board:pet_detail', pk=pk)

    if request.method == 'POST':
        comment.delete()

    return redirect('board:pet_detail', pk=pk)
# ─────────────────────────────────────────
# 반려동물 게시판 댓글 수정 (POST 전용)
# ─────────────────────────────────────────
@login_required(login_url='accounts:login')
def pet_comment_edit(request, pk, comment_id):
    post = get_object_or_404(PetPost, pk=pk)
    comment = get_object_or_404(PetComment, pk=comment_id, post=post)

    # 작성자만 수정 가능
    if request.user != comment.author:
        return redirect('board:pet_detail', pk=pk)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            comment.content = content
            comment.save()

    return redirect('board:pet_detail', pk=pk)
    
#25-12-31 민혁 추가-----------------------------------------

# ▼▼▼ [벼룩시장] ▼▼▼
# 25-12-29 슬기 수정: 검색 기능 추가 (제목, 내용, 작성자명, 닉네임 검색)
def flea_list(request):
    # 검색 기능
    search_query = request.GET.get('search', '').strip()

    # ✅ 지도 기준 반경 필터(선택): /board/flea/?clat=..&clng=..&r=1
    center_lat = request.GET.get('clat')
    center_lng = request.GET.get('clng')
    radius_km = request.GET.get('r', '1')  # 기본 1km

    # 전체 아이템 가져오기
    all_items = FleaItem.objects.select_related('author').prefetch_related('liked_by').all()

    # 검색어가 있으면 필터링
    if search_query:
        items = all_items.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(author__username__icontains=search_query) |
            Q(author__nickname__icontains=search_query)
        )
        # 디버깅: 검색 결과 출력
        print(f"[검색] 검색어: '{search_query}', 전체: {all_items.count()}건, 검색결과: {items.count()}건")
        for item in items[:5]:  # 최대 5개만 출력
            print(f"  - {item.title} (작성자: {item.author.nickname or item.author.username})")
    else:
        items = all_items

    # ✅ 반경 필터 적용 (위치 있는 상품만, 간단 bbox 방식)
    if center_lat and center_lng:
        try:
            import math
            clat = float(center_lat)
            clng = float(center_lng)
            rkm = float(radius_km)

            # 위도 1도 ≈ 111km
            lat_delta = rkm / 111.0
            # 경도는 위도에 따라 달라짐
            lng_delta = rkm / (111.0 * math.cos(math.radians(clat)) or 1e-6)

            items = items.filter(
                latitude__isnull=False,
                longitude__isnull=False,
                latitude__gte=clat - lat_delta,
                latitude__lte=clat + lat_delta,
                longitude__gte=clng - lng_delta,
                longitude__lte=clng + lng_delta,
            )
            print(f"[반경필터] 중심=({clat},{clng}) r={rkm}km -> 결과 {items.count()}건")
        except ValueError:
            print("[반경필터] 파라미터 값이 올바르지 않음")
            pass

    # 25-12-29 슬기 수정: 로그인한 사용자의 찜 목록 조회
    liked_items = None
    if request.user.is_authenticated:
        liked_items = FleaItem.objects.filter(liked_by=request.user).select_related('author')

    # ✅ 회원 기본 주소(회원가입 때 입력한 주소) - 지도 기본 중심용
    user_default_address = ""
    user_default_address_detail = ""
    if request.user.is_authenticated:
        # None 값을 빈 문자열로 확실하게 변환
        raw_address = getattr(request.user, "address", None)
        raw_detail = getattr(request.user, "address_detail", None)
        
        user_default_address = str(raw_address).strip() if raw_address else ""
        user_default_address_detail = str(raw_detail).strip() if raw_detail else ""

        # ✅ address가 비어있고 detail에만 있는 케이스 보정
        if not user_default_address and user_default_address_detail:
            user_default_address = user_default_address_detail

    # ✅ 페이지네이션 (5개씩)
    page_number = request.GET.get('page', '1')
    paginator = Paginator(items.order_by('-id'), 5)  # 최신순 유지
    page_obj = paginator.get_page(page_number)
    total_count = paginator.count

    # ✅ 페이지네이션 버튼 표시(현재 기준 앞2/뒤2 = 최대 5개)
    current_page = page_obj.number
    total_pages = page_obj.paginator.num_pages
    start_page = max(1, current_page - 2)
    end_page = min(total_pages, current_page + 2)
    page_numbers = range(start_page, end_page + 1)

    return render(request, 'board/flea_list.html', {
        'items': page_obj,              # ✅ queryset → Page 객체로
        'total_count': total_count,     # ✅ 전체 건수
        'liked_items': liked_items,
        'search_query': search_query,

        # ✅ 반경필터 파라미터(페이지 이동/검색 유지용)
        'clat': center_lat,
        'clng': center_lng,
        'r': radius_km,

        # ✅ 페이지네이션 UI용(현재±2)
        'page_numbers': page_numbers,
        'current_page': current_page,
        'total_pages': total_pages,

        # ✅ 거래지도 기본 중심(회원 주소)
        'user_default_address': user_default_address,
        'user_default_address_detail': user_default_address_detail,
    })


def flea_geo_items(request):
    """
    지도에 찍을 벼룩상품 좌표 목록(JSON)
    - 위치 정보가 있는 상품만 반환
    - (선택) clat/clng/r 있으면 근처만 반환 (bounding box)
    """
    qs = FleaItem.objects.select_related('author').filter(
        latitude__isnull=False,
        longitude__isnull=False
    )

    # ✅ 근처 필터 파라미터 (km)
    clat = request.GET.get("clat")
    clng = request.GET.get("clng")
    r = request.GET.get("r", "1")  # 기본 1km

    try:
        if clat and clng:
            import math
            lat0 = float(clat)
            lng0 = float(clng)
            rkm = float(r)

            # 안전 제한 (너무 커지는 것 방지)
            rkm = max(0.1, min(5.0, rkm))

            dlat = rkm / 111.0
            dlng = rkm / (111.0 * math.cos(math.radians(lat0)) + 1e-9)

            qs = qs.filter(
                latitude__gte=lat0 - dlat,
                latitude__lte=lat0 + dlat,
                longitude__gte=lng0 - dlng,
                longitude__lte=lng0 + dlng,
            )
    except Exception:
        pass

    data = []
    for item in qs[:200]:  # 근처만 뽑으니 200이면 충분
        # 썸네일
        img = ""
        try:
            if item.image:
                img = item.image.url
        except Exception:
            img = ""

        # 작성자 표시(닉네임 우선)
        author_name = ""
        try:
            author_name = getattr(item.author, "nickname", "") or getattr(item.author, "username", "")
        except Exception:
            author_name = ""

        data.append({
            "id": item.id,
            "title": item.title,
            "price": item.price,
            "address": item.location_address or "",
            "desc": (item.description or "")[:60],
            "img": img,
            "author": author_name,
            "status": getattr(item, "status", "selling"),
            "lat": float(item.latitude),
            "lng": float(item.longitude),
            "url": f"/board/flea/{item.id}/",
        })

    return JsonResponse({"items": data})


@login_required(login_url='accounts:login')
def flea_wishlist(request):
    """로그인 사용자의 벼룩시장 찜 목록 페이지"""
    items = FleaItem.objects.filter(liked_by=request.user).select_related('author').order_by('-id')

    # 페이지네이션: 10개씩
    page_number = request.GET.get('page', '1')
    paginator = Paginator(items, 10)
    page_obj = paginator.get_page(page_number)

    current_page = page_obj.number
    total_pages = page_obj.paginator.num_pages
    start_page = max(1, current_page - 2)
    end_page = min(total_pages, current_page + 2)
    page_numbers = range(start_page, end_page + 1)

    return render(request, 'board/flea_wishlist.html', {
        'items': page_obj,
        'page_numbers': page_numbers,
        'current_page': current_page,
        'total_pages': total_pages,
    })

# 25-12-29 슬기 수정: 댓글 목록 추가, 댓글 폼 전달
def flea_detail(request, pk):
    item = get_object_or_404(FleaItem.objects.select_related('author'), pk=pk)
    comments = item.comments.select_related('author')
    form = FleaCommentForm()
    # 조회수 증가 (작성자는 제외)
    if request.user != item.author:
        item.views = F('views') + 1
        item.save(update_fields=['views'])
        item.refresh_from_db()

    return render(request, 'board/flea_detail.html', {
        'item': item,
        'comments': comments,
        'comment_form': form,
        'report_form': FleaReportForm(),
        'report_count': item.reports.count(),
    })


def flea_report_create(request, pk):
    item = get_object_or_404(FleaItem, pk=pk)
    form = FleaReportForm(request.POST)

    if form.is_valid():
        report = form.save(commit=False)
        report.flea_item = item
        report.reporter = request.user
        report.save()
    else:
        comments = item.comments.select_related('author')
        return render(request, 'board/flea_detail.html', {
            'item': item,
            'comments': comments,
            'comment_form': FleaCommentForm(),
            'report_form': form,
            'report_count': item.reports.count(),
        })

    return redirect('board:flea_detail', pk=pk)

@login_required(login_url='accounts:login')
# 25-12-29 슬기 수정: 찜하기/취소 토글 기능 구현
def flea_like_toggle(request, pk):
    item = get_object_or_404(FleaItem, pk=pk)

    if request.user in item.liked_by.all():
        item.liked_by.remove(request.user)
    else:
        item.liked_by.add(request.user)

    return redirect('board:flea_detail', pk=pk)

@login_required(login_url='accounts:login')
# 25-12-29 슬기 수정: 댓글 작성 (닉네임 자동 설정, 비밀글 비밀번호 검증)
def flea_comment_create(request, pk):
    item = get_object_or_404(FleaItem, pk=pk)

    if request.method == 'POST':
        form = FleaCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.flea_item = item
            comment.nickname = getattr(request.user, 'nickname', None) or request.user.username
            comment.save()
            
            # 25-12-29 슬기 수정: 게시글 작성자에게 알림 생성
            if request.user != item.author:  # 자신의 글에는 알림 없음
                Notification.objects.create(
                    user=item.author,  # 글 작성자에게 알림
                    flea_item=item,
                    message=f"{comment.nickname}님이 댓글을 남겼습니다.",
                    is_read=False
                )
        else:
            comments = item.comments.select_related('author')
            return render(request, 'board/flea_detail.html', {
                'item': item,
                'comments': comments,
                'comment_form': form,
            })

    return redirect('board:flea_detail', pk=pk)

@login_required(login_url='accounts:login')
def flea_create(request):
    if request.method == 'POST':
        form = FleaItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.author = request.user
            item.save()
            return redirect('board:flea_list')
    else:
        form = FleaItemForm()

    return render(request, 'board/flea_write.html', {'form': form})

@login_required(login_url='accounts:login')
def flea_edit(request, pk):
    item = get_object_or_404(FleaItem, pk=pk)
    
    # 작성자만 수정 가능
    if request.user != item.author:
        return redirect('board:flea_detail', pk=pk)
    
    if request.method == 'POST':
        form = FleaItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('board:flea_detail', pk=pk)
    else:
        form = FleaItemForm(instance=item)
    
    return render(request, 'board/flea_write.html', {'form': form, 'item': item})

@login_required(login_url='accounts:login')
def flea_delete(request, pk):
    item = get_object_or_404(FleaItem, pk=pk)
    
    # 작성자만 삭제 가능
    if request.user != item.author:
        return redirect('board:flea_detail', pk=pk)
    
    if request.method == 'POST':
        item.delete()
        return redirect('board:flea_list')
    
    return render(request, 'board/flea_delete.html', {'item': item})

@login_required(login_url='accounts:login')
# 25-12-29 슬기 수정: 댓글 수정 (작성자만 가능, 닉네임 유지)
def flea_comment_edit(request, pk, comment_id):
    item = get_object_or_404(FleaItem, pk=pk)
    comment = get_object_or_404(FleaComment, pk=comment_id, flea_item=item)

    if request.user != comment.author and not request.user.is_staff:
        return redirect('board:flea_detail', pk=pk)

    if request.method == 'POST':
        form = FleaCommentForm(request.POST, instance=comment)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.nickname = getattr(request.user, 'nickname', None) or request.user.username
            updated.save()
            return redirect('board:flea_detail', pk=pk)
    else:
        form = FleaCommentForm(instance=comment)

    return render(request, 'board/flea_comment_form.html', {
        'form': form,
        'item': item,
        'comment': comment,
        'mode': 'edit',
    })

@login_required(login_url='accounts:login')
# 25-12-29 슬기 수정: 댓글 삭제 (작성자만 가능)
def flea_comment_delete(request, pk, comment_id):
    item = get_object_or_404(FleaItem, pk=pk)
    comment = get_object_or_404(FleaComment, pk=comment_id, flea_item=item)

    if request.user != comment.author and not request.user.is_staff:
        return redirect('board:flea_detail', pk=pk)

    if request.method == 'POST':
        comment.delete()
        return redirect('board:flea_detail', pk=pk)

    return render(request, 'board/flea_comment_delete.html', {
        'item': item,
        'comment': comment,
    })

# 25-12-29 슬기 수정: AJAX 상태 변경 (드롭다운 메뉴 선택)
@login_required(login_url='accounts:login')
def flea_status_update(request, pk):
    item = get_object_or_404(FleaItem, pk=pk)
    
    # 작성자만 상태 변경 가능
    if request.user != item.author:
        return JsonResponse({'success': False, 'error': '작성자만 변경 가능합니다.'}, status=403)
    
    if request.method == 'POST':
        # POST 데이터에서 새로운 상태 받기
        new_status = request.POST.get('status', item.status)
        
        # 유효한 상태 확인
        valid_statuses = ['selling', 'reserved', 'sold', 'share']
        if new_status not in valid_statuses:
            return JsonResponse({'success': False, 'error': '유효하지 않은 상태입니다.'}, status=400)
        
        item.status = new_status
        item.save()
        
        # 상태명 맵핑
        status_labels = {
            'selling': '판매중',
            'reserved': '예약중',
            'sold': '판매완료',
            'share': '나눔'
        }
        
        return JsonResponse({
            'success': True,
            'new_status': new_status,
            'status_label': status_labels[new_status]
        })
    
    return JsonResponse({'success': False, 'error': 'POST 요청만 가능합니다.'}, status=400)

# 25-12-29 슬기 수정: 알림 목록 조회
@login_required(login_url='accounts:login')
def notification_list(request):
    notifications = request.user.notifications.all().order_by('-created_at')
    
    # 각 알림에 대해 post 타입에 맞는 URL 생성
    notifications_with_url = []
    for notification in notifications:
        notifications_with_url.append({
            'notification': notification,
            'target_url': notification.get_post_url()
        })
    
    return render(request, 'board/notification_list.html', {'notifications_with_url': notifications_with_url})

# 25-12-29 슬기 수정: 알림 읽음 처리 (AJAX)
@login_required(login_url='accounts:login')
def notification_mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
    
    if request.method == 'POST':
        notification.is_read = True
        notification.save()
        
        # 읽지 않은 알림 개수 반환
        unread_count = request.user.notifications.filter(is_read=False).count()
        
        return JsonResponse({
            'success': True,
            'unread_count': unread_count
        })
    
    return JsonResponse({'success': False, 'error': 'POST 요청만 가능합니다.'}, status=400)

# 25-12-29 슬기 수정: 모든 알림 읽음 처리 (AJAX)
@login_required(login_url='accounts:login')
def notification_mark_all_read(request):
    if request.method == 'POST':
        request.user.notifications.filter(is_read=False).update(is_read=True)
        
        return JsonResponse({
            'success': True,
            'unread_count': 0
        })
    
    return JsonResponse({'success': False, 'error': 'POST 요청만 가능합니다.'}, status=400)


# ▼▼▼ [핫딜공유 게시판] ▼▼▼ ============================================================

# 1. 핫딜 목록
def hotdeal_list(request):
    from .models import HotDeal
    from django.db.models import Q
    
    category = request.GET.get('category', 'all')
    search_query = request.GET.get('search', '')
    
    # 카테고리 필터링
    if category and category != 'all':
        posts = HotDeal.objects.filter(category=category).order_by('-created_at')
    else:
        posts = HotDeal.objects.all().order_by('-created_at')
    
    # 검색 기능 추가
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) | Q(content__icontains=search_query)
        )
    
    print(f"DEBUG hotdeal_list: Total posts count = {posts.count()}", flush=True)
    print(f"DEBUG hotdeal_list: Posts = {[p.title for p in posts]}", flush=True)
    
    # 페이지네이션
    per_page = 10
    paginator = Paginator(posts, per_page)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    
    print(f"DEBUG hotdeal_list: page_obj count = {page_obj.paginator.count}", flush=True)
    print(f"DEBUG hotdeal_list: page_obj list = {[p.title for p in page_obj]}", flush=True)
    
    context = {
        'posts': page_obj,
        'category': category,
        'search_query': search_query,
    }
    return render(request, 'board/hotdeal_list.html', context)


# 2. 핫딜 작성
@login_required(login_url='accounts:login')
def hotdeal_create(request):
    from .models import HotDeal
    
    # 로그인 확인
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    if request.method == 'POST':
        try:
            title = request.POST.get('title', '').strip()
            content = request.POST.get('content', '').strip()
            category = request.POST.get('category', 'all')
            link = request.POST.get('link', '').strip()
            price = request.POST.get('price', '').strip()
            
            # 필수 필드 검증
            if not title or not content:
                return render(request, 'board/hotdeal_form.html', {
                    'error': '제목과 내용은 필수입니다.'
                })
            
            print(f"DEBUG: Creating HotDeal - title={title}, content={content}, author={request.user}")
            
            hotdeal = HotDeal.objects.create(
                title=title,
                content=content,
                category=category,
                link=link,
                price=price,
                author=request.user
            )
            print(f"DEBUG: HotDeal created with pk={hotdeal.pk}")
            return redirect('board:hotdeal_list')
        except Exception as e:
            print(f"DEBUG ERROR: {str(e)}")
            return render(request, 'board/hotdeal_form.html', {
                'error': f'등록 중 오류가 발생했습니다: {str(e)}'
            })
    
    return render(request, 'board/hotdeal_form.html')


# 3. 핫딜 상세보기
def hotdeal_detail(request, pk):
    from .models import HotDeal
    post = get_object_or_404(HotDeal, pk=pk)
    post.views += 1
    post.save()
    return render(request, 'board/hotdeal_detail.html', {'post': post})


# 4. 핫딜 수정
@login_required(login_url='accounts:login')
def hotdeal_update(request, pk):
    from .models import HotDeal
    post = get_object_or_404(HotDeal, pk=pk)
    
    if post.author != request.user:
        return redirect('board:hotdeal_detail', pk=pk)
    
    if request.method == 'POST':
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        post.category = request.POST.get('category', 'all')
        post.link = request.POST.get('link', '')
        post.price = request.POST.get('price', '')
        post.save()
        return redirect('board:hotdeal_detail', pk=pk)
    
    return render(request, 'board/hotdeal_form.html', {'post': post})


# 5. 핫딜 삭제
@login_required(login_url='accounts:login')
def hotdeal_delete(request, pk):
    from .models import HotDeal
    post = get_object_or_404(HotDeal, pk=pk)
    
    if post.author != request.user:
        return redirect('board:hotdeal_detail', pk=pk)
    
    if request.method == 'POST':
        post.delete()
        return redirect('board:hotdeal_list')
    
    return render(request, 'board/hotdeal_detail.html', {'post': post})


# ───────────────────────────────────────────────────────────────────────
# [육아정보] 게시판 뷰 함수들
# 26-01-02 슬기 추가: 육아정보 게시판 전체 기능 (목록, 작성, 상세, 수정, 삭제)
# ───────────────────────────────────────────────────────────────────────
def parenting_list(request):
    from .models import ParentingInfo
    from django.db.models import Q
    
    category = request.GET.get('category', 'all')
    search_query = request.GET.get('search', '').strip()
    # 커뮤니티형 필터 칩
    month = request.GET.get('month')   # 예: '12', '24', '36'
    kw = request.GET.get('kw')         # 예: '떼쓰기', '밤잠'
    
    if category == 'all':
        posts = ParentingInfo.objects.all()
    else:
        posts = ParentingInfo.objects.filter(category=category)
    
    # 검색 기능 추가
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) | Q(content__icontains=search_query)
        )
    # 추천 키워드/월령 칩 필터
    if month and month.isdigit():
        posts = posts.filter(month_age=int(month))
    if kw:
        posts = posts.filter(Q(title__icontains=kw) | Q(content__icontains=kw))
    
    # 최신순으로 정렬
    posts = posts.order_by('-created_at')
    
    # 페이지네이션
    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    context = {
        'posts': posts,
        'category': category,
        'search_query': search_query,
        'month': month,
        'kw': kw,
        'total_count': posts.paginator.count,
    }
    return render(request, 'board/parenting_list.html', context)


@login_required(login_url='accounts:login')
def parenting_create(request):
    from .models import ParentingInfo
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category = request.POST.get('category')
        
        # 월령별 발달 데이터 처리
        month_age = request.POST.get('month_age')
        physical_score = request.POST.get('physical_score')
        cognitive_score = request.POST.get('cognitive_score')
        language_score = request.POST.get('language_score')
        social_score = request.POST.get('social_score')
        height = request.POST.get('height')
        weight = request.POST.get('weight')
        
        post = ParentingInfo.objects.create(
            title=title,
            content=content,
            category=category,
            author=request.user,
            month_age=int(month_age) if month_age else None,
            physical_score=int(physical_score) if physical_score else None,
            cognitive_score=int(cognitive_score) if cognitive_score else None,
            language_score=int(language_score) if language_score else None,
            social_score=int(social_score) if social_score else None,
            height=float(height) if height else None,
            weight=float(weight) if weight else None,
        )
        # 이미지 업로드 (최대 10개)
        images = request.FILES.getlist('images')
        for idx, img in enumerate(images[:10]):
            ParentingImage.objects.create(post=post, image=img, order=idx)
        return redirect('board:parenting_list')
    
    return render(request, 'board/parenting_form.html')


def parenting_detail(request, pk):
    post = get_object_or_404(ParentingInfo, pk=pk)

    # 조회수 증가 (GET 요청에만 반영)
    if request.method == 'GET':
        post.views = F('views') + 1
        post.save(update_fields=['views'])
        post.refresh_from_db(fields=['views'])

    # 댓글 작성 처리
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        content = request.POST.get('content', '').strip()
        if content:
            ParentingComment.objects.create(post=post, author=request.user, content=content)
            post.comment_count = post.comments.count()
            post.save(update_fields=['comment_count'])
            return redirect('board:parenting_detail', pk=pk)
        messages.error(request, '댓글 내용을 입력해 주세요.')

    comments = post.comments.select_related('author').order_by('created_at')

    return render(request, 'board/parenting_detail.html', {
        'post': post,
        'comments': comments,
    })


@login_required
def parenting_update(request, pk):
    from .models import ParentingInfo
    post = get_object_or_404(ParentingInfo, pk=pk)
    
    if post.author != request.user:
        return redirect('board:parenting_detail', pk=pk)
    
    if request.method == 'POST':
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        post.category = request.POST.get('category')
        
        # 월령별 발달 데이터 업데이트
        month_age = request.POST.get('month_age')
        physical_score = request.POST.get('physical_score')
        cognitive_score = request.POST.get('cognitive_score')
        language_score = request.POST.get('language_score')
        social_score = request.POST.get('social_score')
        height = request.POST.get('height')
        weight = request.POST.get('weight')
        
        post.month_age = int(month_age) if month_age else None
        post.physical_score = int(physical_score) if physical_score else None
        post.cognitive_score = int(cognitive_score) if cognitive_score else None
        post.language_score = int(language_score) if language_score else None
        post.social_score = int(social_score) if social_score else None
        post.height = float(height) if height else None
        post.weight = float(weight) if weight else None
        
        post.save()

        # 이미지 삭제 처리
        delete_image_ids = request.POST.getlist('delete_images')
        if delete_image_ids:
            ParentingImage.objects.filter(id__in=delete_image_ids, post=post).delete()

        # 이미지 추가 처리 (총합 최대 10장)
        new_images = request.FILES.getlist('images')
        existing_count = post.images.count()
        allowed = max(0, 10 - existing_count)
        for idx, img in enumerate(new_images[:allowed]):
            ParentingImage.objects.create(post=post, image=img, order=existing_count + idx)
        return redirect('board:parenting_detail', pk=pk)
    
    return render(request, 'board/parenting_form.html', {'post': post})


@login_required
def parenting_delete(request, pk):
    from .models import ParentingInfo
    post = get_object_or_404(ParentingInfo, pk=pk)
    
    if post.author != request.user:
        return redirect('board:parenting_detail', pk=pk)
    
    if request.method == 'POST':
        post.delete()
        return redirect('board:parenting_list')
    
    return redirect('board:parenting_detail', pk=pk)


# ───────────────────────────────────────────────────────────────────────
# [육아정보] 댓글 CRUD (자유게시판 free_comment_*와 동일한 패턴)
# ───────────────────────────────────────────────────────────────────────
from django.views.decorators.http import require_POST
from urllib.parse import urlencode
from django.urls import reverse

@login_required
@require_POST
def parenting_comment_create(request, post_id):
    import json
    post = get_object_or_404(ParentingInfo, id=post_id)
    content = (request.POST.get("content") or "").strip()
    images = []
    
    # 이미지 데이터 처리 (base64로 받은 데이터)
    images_data = request.POST.get('images', '[]')
    try:
        images = json.loads(images_data)
    except:
        images = []
    
    if content:
        comment = ParentingComment.objects.create(
            post=post, 
            author=request.user, 
            content=content,
            images=images  # base64 이미지 저장
        )
        # 댓글수 갱신
        post.comment_count = post.comments.count()
        post.save(update_fields=['comment_count'])

    url = reverse('board:parenting_detail', args=[post_id])
    return redirect(url + "#comments")


@login_required
def parenting_comment_update(request, comment_id):
    comment = get_object_or_404(ParentingComment, id=comment_id)
    if request.user != comment.author and not request.user.is_staff:
        return redirect('board:parenting_detail', pk=comment.post.id)

    if request.method == 'POST':
        content = (request.POST.get('content') or '').strip()
        if content:
            comment.content = content
            comment.save()

    url = reverse('board:parenting_detail', args=[comment.post.id])
    return redirect(url + f"#comment-{comment.id}")


@login_required
@require_POST
def parenting_comment_delete(request, comment_id):
    comment = get_object_or_404(ParentingComment, id=comment_id)
    post = comment.post
    if request.user == comment.author or request.user.is_staff:
        comment.delete()
        # 댓글수 갱신
        post.comment_count = post.comments.count()
        post.save(update_fields=['comment_count'])

    url = reverse('board:parenting_detail', args=[post.id])
    return redirect(url + "#comments")


# 26-01-02 슬기 추가: 월령별 발달 차트 (사용자별 분리 + 평균치 표시)
@login_required(login_url='accounts:login')
def development_chart(request):
    import json
    from django.db.models import Avg
    from .models import ParentingInfo
    
    # 현재 로그인한 사용자의 월령별 발달 데이터만 가져오기 (월령 오름차순)
    developments = ParentingInfo.objects.filter(
        author=request.user,
        category='development',
        month_age__isnull=False
    ).order_by('month_age')
    
    # 차트용 데이터 준비 (사용자 데이터)
    months = [dev.month_age for dev in developments]
    physical = [dev.physical_score or 0 for dev in developments]
    cognitive = [dev.cognitive_score or 0 for dev in developments]
    language = [dev.language_score or 0 for dev in developments]
    social = [dev.social_score or 0 for dev in developments]
    height = [float(dev.height) if dev.height else 0 for dev in developments]
    weight = [float(dev.weight) if dev.weight else 0 for dev in developments]
    
    # 전체 사용자의 월령별 평균 데이터 계산
    all_months = ParentingInfo.objects.filter(
        category='development',
        month_age__isnull=False
    ).values('month_age').distinct().order_by('month_age')
    
    avg_months = []
    avg_physical = []
    avg_cognitive = []
    avg_language = []
    avg_social = []
    avg_height = []
    avg_weight = []
    
    for month_data in all_months:
        month = month_data['month_age']
        avg_data = ParentingInfo.objects.filter(
            category='development',
            month_age=month
        ).aggregate(
            avg_physical=Avg('physical_score'),
            avg_cognitive=Avg('cognitive_score'),
            avg_language=Avg('language_score'),
            avg_social=Avg('social_score'),
            avg_height=Avg('height'),
            avg_weight=Avg('weight')
        )
        
        avg_months.append(month)
        avg_physical.append(round(avg_data['avg_physical'] or 0, 1))
        avg_cognitive.append(round(avg_data['avg_cognitive'] or 0, 1))
        avg_language.append(round(avg_data['avg_language'] or 0, 1))
        avg_social.append(round(avg_data['avg_social'] or 0, 1))
        avg_height.append(round(float(avg_data['avg_height'] or 0), 1))
        avg_weight.append(round(float(avg_data['avg_weight'] or 0), 1))
    
    context = {
        'developments': developments,
        'months_json': json.dumps(months),
        'physical_json': json.dumps(physical),
        'cognitive_json': json.dumps(cognitive),
        'language_json': json.dumps(language),
        'social_json': json.dumps(social),
        'height_json': json.dumps(height),
        'weight_json': json.dumps(weight),
        # 평균 데이터 추가
        'avg_months_json': json.dumps(avg_months),
        'avg_physical_json': json.dumps(avg_physical),
        'avg_cognitive_json': json.dumps(avg_cognitive),
        'avg_language_json': json.dumps(avg_language),
        'avg_social_json': json.dumps(avg_social),
        'avg_height_json': json.dumps(avg_height),
        'avg_weight_json': json.dumps(avg_weight),
    }
    return render(request, 'board/development_chart.html', context)

# ★ 엄마 마음 케어 일기장 (26-01-02 추가)
import google.generativeai as genai
from django.conf import settings
import json

genai.configure(api_key=settings.GOOGLE_API_KEY)

@login_required
def diary_list(request):
    """엄마 마음 케어 일기장 리스트"""
    from .models import MomDiary, DiaryEntry
    
    diary, created = MomDiary.objects.get_or_create(user=request.user)
    entries = diary.entries.all()
    
    # 필터링
    mood_filter = request.GET.get('mood', '')
    search_query = request.GET.get('q', '')
    
    if mood_filter:
        entries = entries.filter(mood=mood_filter)
    if search_query:
        entries = entries.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))
    
    context = {
        'diary': diary,
        'entries': entries,
        'mood_filter': mood_filter,
        'search_query': search_query,
        'mood_choices': DiaryEntry.MOOD_CHOICES,
    }
    return render(request, 'board/diary_list.html', context)


@login_required
def diary_create(request):
    """새 일기 작성"""
    from .models import MomDiary, DiaryEntry
    
    diary, created = MomDiary.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        mood = request.POST.get('mood', 'peaceful')
        title = request.POST.get('title', '')
        content = request.POST.get('content', '')
        is_secret = request.POST.get('is_secret', False) == 'on'
        is_anonymous = request.POST.get('is_anonymous', False) == 'on'
        tags = request.POST.get('tags', '')
        
        entry = DiaryEntry.objects.create(
            diary=diary,
            mood=mood,
            title=title,
            content=content,
            is_secret=is_secret,
            is_anonymous=is_anonymous,
            tags=tags
        )
        
        # AI 케어 응답 생성
        generate_ai_care_response(entry)
        
        return redirect('board:diary_detail', pk=entry.pk)
    
    context = {
        'diary': diary,
        'mood_choices': DiaryEntry.MOOD_CHOICES,
    }
    return render(request, 'board/diary_create.html', context)


@login_required
def diary_detail(request, pk):
    """일기 상세 페이지"""
    from .models import DiaryEntry
    
    entry = get_object_or_404(DiaryEntry, pk=pk, diary__user=request.user)
    
    context = {
        'entry': entry,
        'mood_label': dict(DiaryEntry.MOOD_CHOICES).get(entry.mood, ''),
    }
    return render(request, 'board/diary_detail.html', context)


@login_required
def diary_edit(request, pk):
    """일기 수정"""
    from .models import DiaryEntry
    
    entry = get_object_or_404(DiaryEntry, pk=pk, diary__user=request.user)
    
    if request.method == 'POST':
        entry.mood = request.POST.get('mood', entry.mood)
        entry.title = request.POST.get('title', entry.title)
        entry.content = request.POST.get('content', entry.content)
        entry.is_secret = request.POST.get('is_secret', False) == 'on'
        entry.tags = request.POST.get('tags', entry.tags)
        entry.save()
        
        # AI 응답 재생성 여부
        if request.POST.get('regenerate_ai'):
            generate_ai_care_response(entry)
        
        return redirect('board:diary_detail', pk=entry.pk)
    
    context = {
        'entry': entry,
        'mood_choices': DiaryEntry.MOOD_CHOICES,
    }
    return render(request, 'board/diary_edit.html', context)


@login_required
def diary_delete(request, pk):
    """일기 삭제"""
    from .models import DiaryEntry
    
    if request.method == 'POST':
        entry = get_object_or_404(DiaryEntry, pk=pk, diary__user=request.user)
        entry.delete()
        return redirect('board:diary_list')
    
    return redirect('board:diary_list')


def generate_ai_care_response(entry):
    """
    Gemini API를 사용해 공감과 조언을 담은 AI 응답 생성
    """
    try:
        from .models import DiaryEntry
        
        mood_label = dict(DiaryEntry.MOOD_CHOICES).get(entry.mood, '')
        
        prompt = f"""당신은 따뜻하고 경험 많은 육아 전문가이자 감정 상담가입니다.
한 명의 엄마가 일기에 적은 감정과 일상을 읽고, 깊은 공감과 실질적인 조언을 해주세요.

【엄마의 현재 기분】: {mood_label}

【엄마가 적은 내용】:
{entry.content}

【요청사항】:
1. 먼저 엄마의 감정을 깊게 이해하고 공감해주세요 (2-3문장)
2. 엄마가 겪는 상황이 얼마나 어려운지 인정해주세요
3. 구체적이고 실천 가능한 조언을 3가지 제시하세요
4. 마지막으로 힘내라는 따뜻한 격려 말씀을 해주세요

【톤】: 친한 선배 엄마처럼 따뜻하고 다정하게

답변은 한국어로, 3-4단락으로 구성해주세요."""

        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        
        if response.text:
            entry.ai_care_response = response.text
            entry.ai_response_generated = True
            entry.save()
            return True
    
    except Exception as e:
        print(f"AI 응답 생성 오류: {str(e)}")
        return False
    
    return False


# ═══════════════════════════════════════════════════════════════════════
# 26-01-03 추가: 엄마마음일기장 (MoodDiary) 기능
# 기능: 감정 기록, AI 상담사, 대나무숲 모드, 감정 캘린더
# ═══════════════════════════════════════════════════════════════════════

@login_required(login_url='accounts:login')
def diary_list(request):
    """일기 목록 및 감정 캘린더"""
    diary, created = MomDiary.objects.get_or_create(user=request.user)
    entries = diary.entries.all()
    
    # 월별 필터링
    year = request.GET.get('year', datetime.now().year)
    month = request.GET.get('month', datetime.now().month)
    entries_filtered = entries.filter(
        created_at__year=int(year),
        created_at__month=int(month)
    )
    
    # 달력 생성
    import calendar
    cal = calendar.monthcalendar(int(year), int(month))
    
    # 감정 데이터 매핑 (day -> mood_emoji)
    mood_emoji = {
        'happy': '😊',
        'peaceful': '😌',
        'tired': '😫',
        'stressed': '😰',
        'sad': '😢',
        'angry': '😠',
        'confused': '😕',
    }
    
    calendar_weeks_with_mood = []
    for week in cal:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append({'day': 0, 'emoji': ''})
            else:
                entry = entries_filtered.filter(created_at__day=day).first()
                emoji = mood_emoji.get(entry.mood, '📝') if entry else ''
                week_data.append({'day': day, 'emoji': emoji})
        calendar_weeks_with_mood.append(week_data)
    
    context = {
        'diary': diary,
        'entries': entries_filtered,
        'year': int(year),
        'month': int(month),
        'calendar_weeks_with_mood': calendar_weeks_with_mood,
    }
    return render(request, 'board/diary_list.html', context)


@login_required(login_url='accounts:login')
def diary_create(request):
    """일기 작성"""
    diary, created = MomDiary.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        mood = request.POST.get('mood', 'peaceful')
        title = request.POST.get('title', '')
        content = request.POST.get('content', '')
        is_anonymous = request.POST.get('is_anonymous') == 'on'
        is_secret = request.POST.get('is_secret') == 'on' if not is_anonymous else False
        
        entry = DiaryEntry.objects.create(
            diary=diary,
            mood=mood,
            title=title,
            content=content,
            is_anonymous=is_anonymous,
            is_secret=is_secret,
        )
        
        # AI 상담사 응답 생성 (비동기 또는 배경 작업)
        # generate_ai_counseling.delay(entry.id)  # Celery 사용 시
        
        return redirect('board:diary_detail', pk=entry.id)
    
    return render(request, 'board/diary_create.html')


@login_required(login_url='accounts:login')
def diary_detail(request, pk):
    """일기 상세 보기"""
    entry = get_object_or_404(DiaryEntry, pk=pk)
    
    # 권한 확인: 작성자 본인이거나 익명 공개인 경우만 조회 가능
    if not (entry.diary.user == request.user or entry.is_anonymous):
        return redirect('board:diary_list')
    
    # 태그 리스트로 변환
    tags_list = [tag.strip() for tag in entry.tags.split(',') if tag.strip()] if entry.tags else []
    
    context = {
        'entry': entry,
        'tags_list': tags_list,
        'is_owner': entry.diary.user == request.user,
    }
    return render(request, 'board/diary_detail.html', context)


@login_required(login_url='accounts:login')
def diary_edit(request, pk):
    """일기 수정"""
    entry = get_object_or_404(DiaryEntry, pk=pk)
    
    if entry.diary.user != request.user:
        return redirect('board:diary_detail', pk=pk)
    
    if request.method == 'POST':
        entry.mood = request.POST.get('mood', entry.mood)
        entry.title = request.POST.get('title', entry.title)
        entry.content = request.POST.get('content', entry.content)
        entry.is_anonymous = request.POST.get('is_anonymous') == 'on'
        entry.is_secret = request.POST.get('is_secret') == 'on' if not entry.is_anonymous else False
        entry.save()
        
        return redirect('board:diary_detail', pk=entry.id)
    
    context = {'entry': entry}
    return render(request, 'board/diary_edit.html', context)


@login_required(login_url='accounts:login')
def diary_delete(request, pk):
    """일기 삭제"""
    entry = get_object_or_404(DiaryEntry, pk=pk)
    
    if entry.diary.user != request.user:
        return redirect('board:diary_detail', pk=pk)
    
    if request.method == 'POST':
        entry.delete()
        return redirect('board:diary_list')
    
    return render(request, 'board/diary_delete.html', {'entry': entry})


@login_required(login_url='accounts:login')
def bamboo_diary_list(request):
    """대나무숲 - 익명 공개 일기 목록"""
    entries = DiaryEntry.objects.filter(is_anonymous=True, ai_response_generated=True).order_by('-created_at')
    
    # 페이지네이션
    paginator = Paginator(entries, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'title': '🎋 대나무숲 - 누군가의 감정 나눔',
    }
    return render(request, 'board/bamboo_diary_list.html', context)


def generate_ai_counseling(entry_id):
    """AI 상담사 응답 생성 (Gemini API 사용)"""
    import google.generativeai as genai
    from django.conf import settings
    
    try:
        entry = DiaryEntry.objects.get(id=entry_id)
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
당신은 따뜻하고 공감 능력이 뛰어난 육아 전문 상담사입니다.
다음은 한 엄마가 쓴 일기입니다.

감정: {entry.get_mood_display()}
제목: {entry.title}
내용: {entry.content}

이 엄마에게 따뜻한 말씀과 가벼운 조언을 해주세요. 
- 먼저 공감과 위로를 주세요.
- 실질적인 조언이나 팁을 가볍게 제시해주세요.
- 2-3문단 정도의 친근한 문체로 작성해주세요.
"""
        
        response = model.generate_content(prompt)
        entry.ai_care_response = response.text
        entry.ai_response_generated = True
        entry.save()
        
    except Exception as e:
        print(f"AI 상담사 생성 오류: {e}")


# ═══════════════════════════════════════════════════════════════════════
# 🐾 반려동물 건강팁/고민상담 게시판 (26-01-08 민혁 추가)
# ═══════════════════════════════════════════════════════════════════════
from .models import PetHealthPost, PetHealthImage, PetHealthComment, PetCounselPost, PetCounselImage, PetCounselComment
from django.contrib.admin.views.decorators import staff_member_required

# 🐾 반려동물 건강팁 - LIST
def pet_health_list(request):
    qs = PetHealthPost.objects.all().order_by('-id')
    paginator = Paginator(qs, 10)  # 페이지당 10개
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    # 각 게시물에 번호 추가
    if posts:
        start_num = paginator.count - (posts.start_index() - 1)
        for idx, post in enumerate(posts):
            post.number = start_num - idx

    return render(request, 'board/pet_health_list.html', {
        'posts': posts
    })


# 🐾 반려동물 건강팁 - DETAIL (조회수 포함)
def pet_health_detail(request, pk):
    post = get_object_or_404(PetHealthPost, pk=pk)
    post.views += 1
    post.save(update_fields=['views'])

    return render(
        request,
        "board/pet_health_detail.html",
        {"post": post}
    )


# 🐾 반려동물 건강팁 - WRITE (관리자 전용)
@staff_member_required
def pet_health_write(request):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")

        post = PetHealthPost.objects.create(
            title=title,
            content=content,
            author=request.user
        )

        # ✅ 이미지 저장 (최대 10장)
        images = request.FILES.getlist("images")
        for idx, img in enumerate(images[:10]):
            PetHealthImage.objects.create(
                post=post,
                image=img,
                order=idx
            )

        return redirect("board:pet_health_list")

    return render(
        request,
        "board/pet_health_write.html",
        {
            "is_edit": False
        }
    )


# 🐾 반려동물 건강팁 - Edit (관리자 전용)
@staff_member_required
def pet_health_edit(request, pk):
    post = get_object_or_404(PetHealthPost, pk=pk)

    if request.method == "POST":
        post.title = request.POST.get("title")
        post.content = request.POST.get("content")
        post.save()

        # ✅ 삭제할 이미지
        delete_image_ids = request.POST.getlist("delete_images")
        if delete_image_ids:
            PetHealthImage.objects.filter(
                id__in=delete_image_ids,
                post=post
            ).delete()

        # ✅ 새 이미지 추가 (총합 최대 10장)
        new_images = request.FILES.getlist("images")
        existing_count = post.images.count()
        allowed = max(0, 10 - existing_count)

        for idx, img in enumerate(new_images[:allowed]):
            PetHealthImage.objects.create(
                post=post,
                image=img,
                order=existing_count + idx
            )

        return redirect("board:pet_health_detail", pk=pk)

    return render(
        request,
        "board/pet_health_write.html",  # ✅ write 템플릿 재사용
        {
            "post": post,
            "is_edit": True,
        }
    )


@staff_member_required
def pet_health_delete(request, pk):
    post = get_object_or_404(PetHealthPost, pk=pk)
    if request.method == 'POST':
        post.delete()
        return redirect('board:pet_health_list')
    return redirect('board:pet_health_detail', pk=pk)


# 🐾 반려동물 건강팁 댓글 작성
@login_required(login_url='accounts:login')
def pet_health_comment_create(request, pk):
    post = get_object_or_404(PetHealthPost, pk=pk)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            PetHealthComment.objects.create(
                post=post,
                author=request.user,
                content=content
            )

    return redirect('board:pet_health_detail', pk=pk)


@login_required
def pet_health_comment_edit(request, comment_id):
    comment = get_object_or_404(PetHealthComment, id=comment_id)

    if request.user != comment.author and not request.user.is_staff:
        return redirect('board:pet_health_detail', pk=comment.post.id)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            comment.content = content
            comment.save()

    return redirect('board:pet_health_detail', pk=comment.post.id)


@login_required
@require_POST
def pet_health_comment_delete(request, comment_id):
    comment = get_object_or_404(PetHealthComment, id=comment_id)
    post_id = comment.post.id

    if request.user == comment.author or request.user.is_staff:
        comment.delete()

    return redirect('board:pet_health_detail', pk=post_id)


# ═══════════════════════════════════════════════════════════════════════
# 🐾 반려동물 고민상담 게시판 (26-01-09 민혁 추가)
# ═══════════════════════════════════════════════════════════════════════

def pet_counsel_list(request):
    search_query = request.GET.get('search', '')

    qs = PetCounselPost.objects.all().order_by('-id')

    if search_query:
        qs = qs.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )

    paginator = Paginator(qs, 10)  # ✅ 페이지당 10개
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    # 각 게시물에 번호 추가
    if posts:
        start_num = paginator.count - (posts.start_index() - 1)
        for idx, post in enumerate(posts):
            post.number = start_num - idx

    return render(request, 'board/pet_counsel_list.html', {
        'posts': posts,
        'search_query': search_query,
    })


def pet_counsel_detail(request, pk):
    post = get_object_or_404(PetCounselPost, pk=pk)

    # 조회수 증가 (F expression 사용으로 데이터베이스 레벨에서 안전하게 증가)
    PetCounselPost.objects.filter(pk=pk).update(views=F('views') + 1)
    post.refresh_from_db()

    return render(
        request,
        "board/pet_counsel_detail.html",
        {"post": post}
    )


@login_required
def pet_counsel_write(request):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")

        post = PetCounselPost.objects.create(
            title=title,
            content=content,
            author=request.user
        )

        for img in request.FILES.getlist("images"):
            PetCounselImage.objects.create(post=post, image=img)

        return redirect("board:pet_counsel_detail", pk=post.pk)

    return render(request, "board/pet_counsel_write.html", {
        "is_edit": False
    })


@login_required
def pet_counsel_edit(request, pk):
    post = get_object_or_404(PetCounselPost, pk=pk)

    if request.user != post.author and not request.user.is_staff:
        return redirect("board:pet_counsel_detail", pk=pk)

    if request.method == "POST":
        post.title = request.POST.get("title")
        post.content = request.POST.get("content")
        post.save()

        # 🔥 기존 이미지 삭제
        delete_ids = request.POST.getlist("delete_images")
        if delete_ids:
            PetCounselImage.objects.filter(id__in=delete_ids, post=post).delete()

        # 🔥 새 이미지 추가 (총 10장 제한)
        new_images = request.FILES.getlist("images")
        existing = post.images.count()
        for idx, img in enumerate(new_images):
            if existing + idx < 10:
                PetCounselImage.objects.create(
                    post=post,
                    image=img,
                    order=existing + idx
                )

        return redirect("board:pet_counsel_detail", pk=pk)

    return render(
        request,
        "board/pet_counsel_write.html",
        {"post": post, "is_edit": True}
    )


@login_required
def pet_counsel_delete(request, pk):
    post = get_object_or_404(PetCounselPost, pk=pk)

    # 작성자 or 관리자만 삭제 가능
    if request.user != post.author and not request.user.is_staff:
        return redirect("board:pet_counsel_detail", pk=pk)

    if request.method == "POST":
        post.delete()
        return redirect("board:pet_counsel_list")

    # GET 접근 차단 (실수 삭제 방지)
    return redirect("board:pet_counsel_detail", pk=pk)


@login_required
def pet_counsel_comment_create(request, pk):
    post = get_object_or_404(PetCounselPost, pk=pk)

    if request.method == "POST":
        PetCounselComment.objects.create(
            post=post,
            author=request.user,
            content=request.POST.get("content")
        )

    return redirect("board:pet_counsel_detail", pk=pk)


@login_required
def pet_counsel_comment_delete(request, pk, comment_id):
    comment = get_object_or_404(
        PetCounselComment,
        pk=comment_id,
        post_id=pk
    )

    if request.user == comment.author or request.user.is_staff:
        comment.delete()

    return redirect("board:pet_counsel_detail", pk=pk)


@login_required
def pet_counsel_comment_edit(request, comment_id):
    comment = get_object_or_404(PetCounselComment, pk=comment_id)

    if request.method == "POST":
        if request.user == comment.author or request.user.is_staff:
            comment.content = request.POST.get("content")
            comment.save()

    return redirect("board:pet_counsel_detail", pk=comment.post.id)
