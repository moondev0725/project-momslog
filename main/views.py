# ?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═??
# main/views.py
# 맘스로그 ?�로?�트 - 메인 ?�이지 �??�합 검??�?
# ?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═??
# ?�성?? 2025-12-29
# 기능:
#   1. index: 메인 ?�이지 ?�더�?(배너, ?�기글, 로그??박스)
#   2. search: ?�합 검??(공�??�항, ?�유게시?? 벼룩?�장 ?�체 검??
# ?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═?�═??

import json
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.utils import timezone
from django.core.cache import cache
from itertools import chain
from operator import attrgetter
import requests
from datetime import datetime
# 게시판 모델 import (Notice, FreePost, FleaItem, HotDeal)  # 26-01-02 슬기 추가: HotDeal
from board.models import Notice, FreePost, FleaItem, HotDeal, ParentingInfo, PetPost, Notification
from recipes.models import RecipePost
from board.utils import calculate_popularity_score, get_popularity_icon  # 26-01-05 추가
from .models import GrowthRecord, CalendarRecord
from .forms import GrowthRecordForm

# ?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�
# 메인 ?�이지
# ?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�
# 26-01-02 ?�기 ?�정: ?�시�??�기글 ?�제 ?�이???�시
# 26-01-05 ?�기 ?�구?? ?�기???�수 기반 ?�렬 + ?�영�?고정글
def index(request):
    """
    맘스로그 메인 ?�이지
    - 배너 ?�라?�더 (?�벤???�딜 게시?�에???�적 로드)
    - ?�시�??�기글 ?�시 (?�기???�수 기반, ?�영�?고정글 ?�선)
    - 로그??로그?�웃 박스
    """
    # 배너글 HotDeal/ParentingInfo에서 최신 5개씩 가져오기 (캐싱: 120초)
    banner_posts_cache_key = 'banner_posts'
    banner_posts = cache.get(banner_posts_cache_key)
    
    if banner_posts is None:
        banner_posts = []
        
        # HotDeal 글 (이벤트 체험품 - 상위 3개)
        hotdeals = HotDeal.objects.filter(category='event').select_related('author').order_by('-created_at')[:3]
        for post in hotdeals:
            post.post_type = 'hotdeal'
            post.post_url = f'/board/hotdeal/{post.pk}/'
            banner_posts.append(post)
        
        # ParentingInfo 글 - 상위 2개
        parentings = ParentingInfo.objects.all().select_related('author').order_by('-created_at')[:2]
        for post in parentings:
            post.post_type = 'parenting'
            post.post_url = f'/board/parenting/{post.pk}/'
            banner_posts.append(post)
        
        cache.set(banner_posts_cache_key, banner_posts, 120)  # 120초 캐싱
    
    # 현시호기글 조회 (기기점 기반)
    # 1. 영우고정글 (최대 1개씩, 캐싱 60초)
    pinned_posts_cache_key = 'pinned_posts'
    pinned_posts = cache.get(pinned_posts_cache_key)
    
    if pinned_posts is None:
        pinned_posts = []
        pinned_free = FreePost.objects.filter(is_pinned=True).select_related('author').order_by('-pinned_at')[:1]
        pinned_hotdeal = HotDeal.objects.filter(is_pinned=True).select_related('author').order_by('-pinned_at')[:1]
        pinned_parenting = ParentingInfo.objects.filter(is_pinned=True).select_related('author').order_by('-pinned_at')[:1]
        
        for post in pinned_free:
            post.post_type = 'free'
            post.popularity_icon = get_popularity_icon(post.popularity_score)
            pinned_posts.append(post)
        for post in pinned_hotdeal:
            post.post_type = 'hotdeal'
            post.popularity_icon = get_popularity_icon(post.popularity_score)
            pinned_posts.append(post)
        for post in pinned_parenting:
            post.post_type = 'parenting'
            post.popularity_icon = get_popularity_icon(post.popularity_score)
            pinned_posts.append(post)
        
        cache.set(pinned_posts_cache_key, pinned_posts, 60)  # 60초 캐싱
    
    # 2. 배너 기기글 (쿼리 최적화: select_related, prefetch_related 적용, 캐싱: 300초)
    hot_posts_cache_key = 'hot_posts_carousel'
    hot_posts = cache.get(hot_posts_cache_key)
    
    if hot_posts is None:
        free_posts = list(FreePost.objects.filter(is_pinned=False).select_related('author').order_by('-popularity_score', '-created_at')[:10])
        hotdeal_posts = list(HotDeal.objects.filter(is_pinned=False).select_related('author').order_by('-popularity_score', '-created_at')[:10])
        parenting_posts = list(ParentingInfo.objects.filter(is_pinned=False).select_related('author').order_by('-popularity_score', '-created_at')[:10])
        
        # 포스트에 정보 추가 (post_type, 인기도 아이콘)
        for post in free_posts:
            post.post_type = 'free'
            post.popularity_icon = get_popularity_icon(post.popularity_score)
        for post in hotdeal_posts:
            post.post_type = 'hotdeal'
            post.popularity_icon = get_popularity_icon(post.popularity_score)
        for post in parenting_posts:
            post.post_type = 'parenting'
            post.popularity_icon = get_popularity_icon(post.popularity_score)
        
        # 합치고 상위 12개 추출
        all_posts = free_posts + hotdeal_posts + parenting_posts
        hot_posts = sorted(all_posts, key=lambda x: x.popularity_score, reverse=True)[:12]
        
        cache.set(hot_posts_cache_key, hot_posts, 300)  # 5분 캐싱

    # 2-1. 큐레이션: 1 Big + 3 Small (hot_posts에서 선별)
    def get_signal_badge(p):
        comments = getattr(p, 'comment_count', 0) or 0
        views = getattr(p, 'views', 0) or 0
        try:
            is_recent = (timezone.now() - p.created_at).total_seconds() < (15 * 60)
        except Exception:
            is_recent = False
        if comments >= 10:
            return ('댓글 활발', 'is-comments')
        elif views >= 20:
            return ('조회 급상승', 'is-views')
        elif is_recent:
            return ('방금 올라옴', 'is-new')
        else:
            return ('조회 급상승', 'is-views')

    curation_featured = hot_posts[0] if hot_posts else None
    curation_others = hot_posts[1:4] if hot_posts and len(hot_posts) > 1 else []

    # 뱃지 라벨/클래스 주입
    if curation_featured:
        lbl, cls = get_signal_badge(curation_featured)
        curation_featured.signal_label = lbl
        curation_featured.signal_class = cls
        
        # 베스트 댓글 가져오기 (반응이 가장 많은 댓글)
        from board.models import FreeComment
        best_comment = None
        try:
            if curation_featured.post_type == 'free':
                comments = FreeComment.objects.filter(post=curation_featured).order_by('-created_at')
                if comments.exists():
                    best_comment = comments.first()  # 최신 댓글 사용
        except Exception:
            best_comment = None
        curation_featured.best_comment = best_comment
    for p in curation_others:
        lbl, cls = get_signal_badge(p)
        p.signal_label = lbl
        p.signal_class = cls

    # 핫 포스트 탭에 표시될 모든 목록에 뱃지 주입
    for p in hot_posts:
        lbl, cls = get_signal_badge(p)
        p.signal_label = lbl
        p.signal_class = cls
    
    # 4. 엄마들 속 얘기 (공감 게시글) - 캐싱 적용
    empathy_cache_key = 'empathy_posts_carousel'
    empathy_posts = cache.get(empathy_cache_key)
    if empathy_posts is None:
        empathy_posts = list(FreePost.objects.select_related('author').order_by('-reaction_empathy', '-created_at')[:4])
        for post in empathy_posts:
            post.post_type = 'free'
        cache.set(empathy_cache_key, empathy_posts, 300)
    for p in empathy_posts:
        lbl, cls = get_signal_badge(p)
        p.signal_label = lbl
        p.signal_class = cls

    # 5. 실전 육아 정보 - 캐싱 적용
    parenting_info_cache_key = 'parenting_info_posts_carousel'
    parenting_info_posts = cache.get(parenting_info_cache_key)
    if parenting_info_posts is None:
        parenting_info_posts = list(ParentingInfo.objects.select_related('author').order_by('-popularity_score', '-created_at')[:6])
        for post in parenting_info_posts:
            post.post_type = 'parenting'
        cache.set(parenting_info_cache_key, parenting_info_posts, 300)
    for p in parenting_info_posts:
        lbl, cls = get_signal_badge(p)
        p.signal_label = lbl
        p.signal_class = cls
    
    # 6. 중고물품판매 - 캐싱 적용
    flea_posts_cache_key = 'flea_posts_carousel'
    flea_posts = cache.get(flea_posts_cache_key)
    if flea_posts is None:
        flea_posts = list(FleaItem.objects.select_related('author').prefetch_related('comments').filter(status='selling').order_by('-views', '-created_at')[:8])
        for post in flea_posts:
            post.post_type = 'flea'
            post.comment_count = post.comments.count()  # FleaItem용 comment_count 추가
        cache.set(flea_posts_cache_key, flea_posts, 300)
    for p in flea_posts:
        lbl, cls = get_signal_badge(p)
        p.signal_label = lbl
        p.signal_class = cls
    
    # ═══════════════════════════════════════════════════════════════════════
    # 26-01-06 슬기 추가: 2026년 달력 생성 (일요일 기준)
    # 설명: 사용자가 날짜를 클릭하면 육아 기록을 작성할 수 있는 인터랙티브 달력
    #      기록이 있는 날짜에는 빨간 동그라미로 표시됨
    # ═══════════════════════════════════════════════════════════════════════
    import calendar
    year = 2026
    months_calendar = []
    month_names = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']
    
    # 캘린더 설정: 일요일(6)부터 시작하도록 지정
    cal = calendar.Calendar(firstweekday=6)
    
    for month in range(1, 13):
        # 일요일부터 시작하는 달력 생성 (각 주별로 0은 다른 달의 날짜)
        weeks = cal.monthdayscalendar(year, month)
        
        months_calendar.append({
            'month': month,
            'name': month_names[month - 1],
            'days': weeks,
            'weekdays': ['일', '월', '화', '수', '목', '금', '토']
        })
    
    # 우측 마이페이지 동기부여 문구/알림 데이터
    motivation_hint = None
    unread_notifications = 0
    recent_notifications = []
    if request.user.is_authenticated:
        try:
            unread_notifications = Notification.objects.filter(user=request.user, is_read=False).count()
            recent_notifications = list(Notification.objects.filter(user=request.user).order_by('-created_at')[:3])
        except Exception:
            unread_notifications = 0
            recent_notifications = []

        # 등급 진행 정보는 context processor로 제공되므로 여기서는 힌트 문구만 생성
        # 남은 포인트가 3 이하라면 "게시글 1개면 충분해요" 메시지 노출
        # 그 외에는 다음 레벨 레이블과 남은 포인트 중심으로 안내
        # 템플릿에서 grade_progress와 조합해 사용
        motivation_hint = {
            'post_enough': False,
        }
        try:
            # grade_progress를 템플릿에서 사용하므로 남은 포인트 임계만 계산
            # 포인트 3 이하라면 게시글 1개면 충분 메시지를 활성화
            from accounts.services import get_grade_progress
            gp = get_grade_progress(request.user)
            motivation_hint['post_enough'] = (gp.get('remaining', 0) <= 3) and not gp.get('is_max', False)
        except Exception:
            motivation_hint['post_enough'] = False

    context = {
        'banner_posts': banner_posts,
        'pinned_posts': pinned_posts,
        'hot_posts': hot_posts,
        'curation_featured': curation_featured,
        'curation_others': curation_others,
        'empathy_posts': empathy_posts,
        'parenting_info_posts': parenting_info_posts,
        'flea_posts': flea_posts,
        'months_calendar': months_calendar,
        'current_month': 0,  # 1월 (0-indexed)
        'motivation_hint': motivation_hint,
        'unread_notifications': unread_notifications,
        'recent_notifications': recent_notifications,
        'best_comment': curation_featured.best_comment if curation_featured and hasattr(curation_featured, 'best_comment') else None,
    }
    
    return render(request, 'main/index.html', context)


# ?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�
# 지??�?- ?�네�??�기글 ?�시
# 26-01-05 ?�기 추�?: Leaflet 지?�에 게시글 마커 ?�시
# ?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�
def map_view(request):
    """
    ?�네�??�기글??지?�에 ?�시
    - Leaflet ?�이브러�??�용
    - 좌표가 ?�는 게시글�??�시
    - ?�기???�수 기�? 마커 ?�기 ?�름
    """
    import json
    from django.utils.dateformat import format as date_format
    
    # 모든 게시글 �?좌표가 ?�는 것만 ?�집
    all_posts = []
    
    # FreePost
    free_posts = FreePost.objects.filter(
        latitude__isnull=False, 
        longitude__isnull=False
    ).order_by('-popularity_score')[:100]
    
    for post in free_posts:
        all_posts.append({
            'id': f'free_{post.id}',
            'title': post.title,
            'content': post.content[:100] if post.content else '',
            'latitude': str(post.latitude),
            'longitude': str(post.longitude),
            'region': post.region or 'seoul',
            'district': post.district or '',
            'dong': post.dong or '',
            'author': post.author.username if post.author else '?�명',
            'views': post.views,
            'comment_count': post.comment_count,
            'bookmark_count': post.bookmark_count,
            'popularity_score': post.popularity_score,
            'created_at': date_format(post.created_at, 'm.d H:i'),
            'url': f'/board/free/{post.id}/',
            'post_type': 'free',
            'user_region': post.region or 'seoul'
        })
    
    # HotDeal
    hotdeal_posts = HotDeal.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False
    ).order_by('-popularity_score')[:100]
    
    for post in hotdeal_posts:
        all_posts.append({
            'id': f'hotdeal_{post.id}',
            'title': post.title,
            'content': post.content[:100] if post.content else '',
            'latitude': str(post.latitude),
            'longitude': str(post.longitude),
            'region': post.region or 'seoul',
            'district': post.district or '',
            'dong': post.dong or '',
            'author': post.author.username if post.author else '?�명',
            'views': post.views,
            'comment_count': post.comment_count,
            'bookmark_count': post.bookmark_count,
            'popularity_score': post.popularity_score,
            'created_at': date_format(post.created_at, 'm.d H:i'),
            'url': f'/board/hotdeal/{post.id}/',
            'post_type': 'hotdeal',
            'user_region': post.region or 'seoul'
        })
    
    # ParentingInfo
    parenting_posts = ParentingInfo.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False
    ).order_by('-popularity_score')[:100]
    
    for post in parenting_posts:
        all_posts.append({
            'id': f'parenting_{post.id}',
            'title': post.title,
            'content': post.content[:100] if post.content else '',
            'latitude': str(post.latitude),
            'longitude': str(post.longitude),
            'region': post.region or 'seoul',
            'district': post.district or '',
            'dong': post.dong or '',
            'author': post.author.username if post.author else '?�명',
            'views': post.views,
            'comment_count': post.comment_count,
            'bookmark_count': post.bookmark_count,
            'popularity_score': post.popularity_score,
            'created_at': date_format(post.created_at, 'm.d H:i'),
            'url': f'/board/parenting/{post.id}/',
            'post_type': 'parenting',
            'user_region': post.region or 'seoul'
        })
    
    # ?�기???�으�??�렬
    all_posts = sorted(all_posts, key=lambda x: x['popularity_score'], reverse=True)
    
    # ?�용?�의 지???�보 (?�후 ?�용)
    user_region = request.GET.get('region', 'seoul')
    
    context = {
        'posts_json': json.dumps(all_posts),
        'user_region': user_region,
        'total_posts': len(all_posts),
    }
    
    return render(request, 'map/map.html', context)


# ?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�
# ?�장 기록 그래??(Chart.js) - ?�령�?발달 지??
# 26-01-04 ?�기 ?�작?? ??몸무�????�령�?발달지?�로 ?�환
# ?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�
@login_required(login_url='accounts:login')
def growth_chart(request):
    """
    ?�령�?발달 지?��? ?�인 그래??+ ?�균 밴드�??�시
    - ?�체발달, ?��?발달, ?�어발달, ?�회?�발??4가지 ?�역
    - ParentingInfo 모델?�서 category�?최신 ?�수 추출
    """
    
    # ParentingInfo?�서 ?�용?�의 발달 기록 가?�오�?
    developments = ParentingInfo.objects.filter(author=request.user).order_by('month_age')
    
    if not developments.exists():
        context = {'developments': None}
        return render(request, 'main/growth_chart.html', context)
    
    # ?�령 추출 (1~12개월)
    months = []
    physical_scores = []
    cognitive_scores = []
    language_scores = []
    social_scores = []
    
    # 카테고리별로 최신 데이터만 추출
    for month in range(1, 13):
        dev_data = {}

        # 신체발달 (월령별 최신 1개)
        physical = developments.filter(month_age=month, category='신체발달').order_by('-created_at').first()
        if physical:
            dev_data['physical'] = int(physical.physical_score) if physical.physical_score else 50

        # 인지발달
        cognitive = developments.filter(month_age=month, category='인지발달').order_by('-created_at').first()
        if cognitive:
            dev_data['cognitive'] = int(cognitive.cognitive_score) if cognitive.cognitive_score else 50

        # 언어발달
        language = developments.filter(month_age=month, category='언어발달').order_by('-created_at').first()
        if language:
            dev_data['language'] = int(language.language_score) if language.language_score else 50

        # 사회발달
        social = developments.filter(month_age=month, category='사회발달').order_by('-created_at').first()
        if social:
            dev_data['social'] = int(social.social_score) if social.social_score else 50

        # 최소 1개 이상 발달 데이터가 있으면 추가
        if dev_data:
            months.append(month)
            physical_scores.append(dev_data.get('physical', 50))
            cognitive_scores.append(dev_data.get('cognitive', 50))
            language_scores.append(dev_data.get('language', 50))
            social_scores.append(dev_data.get('social', 50))
    
    # ?�국 ?�균�?(?�?�소?�과?�회 기�?)
    avg_months = list(range(1, 13))
    avg_physical = [42, 48, 54, 60, 66, 72, 76, 80, 84, 88, 92, 96]
    avg_cognitive = [40, 46, 52, 58, 64, 70, 74, 78, 82, 86, 90, 94]
    avg_language = [35, 42, 49, 56, 63, 70, 76, 82, 88, 92, 96, 100]
    avg_social = [38, 45, 52, 59, 66, 73, 79, 85, 91, 94, 97, 100]
    
    context = {
        'developments': developments if developments.exists() else None,
        'months_json': json.dumps(months, ensure_ascii=False),
        'physical_json': json.dumps(physical_scores),
        'cognitive_json': json.dumps(cognitive_scores),
        'language_json': json.dumps(language_scores),
        'social_json': json.dumps(social_scores),
        'avg_months_json': json.dumps(avg_months, ensure_ascii=False),
        'avg_physical_json': json.dumps(avg_physical),
        'avg_cognitive_json': json.dumps(avg_cognitive),
        'avg_language_json': json.dumps(avg_language),
        'avg_social_json': json.dumps(avg_social),
    }
    return render(request, 'main/growth_chart.html', context)

# ?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�
# ?�합 검??(공�??�항 + ?�유게시??+ 벼룩?�장 + ?�딜공유)
# 25-12-29 ?�기 ?�정: 공�??�항 검??추�?
# 26-01-02 ?�기 ?�정: ?�딜공유 검??추�?
# ?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�
def search(request):
    """
    ?�체 게시???�합 검??
    - 공�??�항: ?�목, ?�용 검??
    - ?�유게시?? ?�목, ?�용 검??
    - 벼룩?�장: ?�목, ?�명 검??
    - ?�딜공유: ?�목, ?�용 검??
    - 결과??최신?�으�??�렬?�여 반환
    """
    query = request.GET.get('q', '')
    posts = []

    if query:
        # 1. 공�??�항 검??(?�목, ?�용)
        notice_results = Notice.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
        # 꼬리???�기 (?�플릿에??게시??구분??
        for post in notice_results:
            post.board_type = 'notice'

        # 2. ?�유게시??검??(?�목, ?�용)
        free_results = FreePost.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
        for post in free_results:
            post.board_type = 'free'

        # 3. 벼룩?�장 검??(?�목, ?�명)
        flea_results = FleaItem.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
        for post in flea_results:
            post.board_type = 'flea'

        # 4. ?�딜공유 검??(?�목, ?�용)  # 26-01-02 ?�기 추�?
        hotdeal_results = HotDeal.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
        for post in hotdeal_results:
            post.board_type = 'hotdeal'

        # 5. 요리레시피 검색 (제목, 내용)  # 26-01-06 추가
        recipe_results = RecipePost.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
        for post in recipe_results:
            post.board_type = 'recipe'

        # 6. 반려동물 검색 (제목, 내용)  # 26-01-06 추가
        pet_results = PetPost.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
        for post in pet_results:
            post.board_type = 'pet'

        # 7. 육아정보 검색 (제목, 내용)  # 26-01-06 추가
        parenting_results = ParentingInfo.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
        for post in parenting_results:
            post.board_type = 'parenting'

        # 8. 결과 ?�치�?
        posts = list(chain(notice_results, free_results, flea_results, hotdeal_results, recipe_results, pet_results, parenting_results))

        # 9. 최신???�렬 (created_at 기�?)
        posts.sort(key=attrgetter('created_at'), reverse=True)

    context = {
        'posts': posts,
        'q': query,
    }
    return render(request, 'main/search_result.html', context)


# ?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�
# ?�시�?반응 ?�드 - ?�체 보기
# 26-01-05 ?�기 추�?: ?�시�?반응 ???�렬??무한 ?�크�??�드
# ?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�
def realtime_feed(request):
    """
    ?�시�?반응 ?�드 ?�이지
    - 모든 게시글???�시�?반응 ?�수 기반?�로 ?�렬
    - 무한 ?�크�?방식?�로 ??많�? 글 ?�시
    - ?�이지?�이???�용 ????
    - ?�동 갱신 기능 (JavaScript AJAX)
    """
    # ?�이지?�이??(무한 ?�크롤용)
    page = request.GET.get('page', 1)
    limit = 20  # ??번에 로드??글??개수
    
    try:
        page = int(page)
        if page < 1:
            page = 1
    except (ValueError, TypeError):
        page = 1
    
    offset = (page - 1) * limit
    
    # 1. 모든 게시글 ?�집 (?�시�?반응 ?�수 기반)
    free_posts = list(FreePost.objects.order_by('-popularity_score', '-created_at')[:200])
    hotdeal_posts = list(HotDeal.objects.order_by('-popularity_score', '-created_at')[:200])
    parenting_posts = list(ParentingInfo.objects.order_by('-popularity_score', '-created_at')[:200])
    
    # 2. ?�???�보 �??�이�?추�?
    for post in free_posts:
        post.post_type = 'free'
        post.popularity_icon = get_popularity_icon(post.popularity_score)
    for post in hotdeal_posts:
        post.post_type = 'hotdeal'
        post.popularity_icon = get_popularity_icon(post.popularity_score)
    for post in parenting_posts:
        post.post_type = 'parenting'
        post.popularity_icon = get_popularity_icon(post.popularity_score)
    
    # 3. ?�치�??�기???�으�??�렬
    all_posts = free_posts + hotdeal_posts + parenting_posts
    sorted_posts = sorted(all_posts, key=lambda x: (x.popularity_score, x.created_at), reverse=True)
    
    # 4. ?�이지?�이???�용
    total_count = len(sorted_posts)
    paginated_posts = sorted_posts[offset:offset + limit]
    
    # AJAX ?�청??경우 JSON 반환
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.utils.dateformat import format as date_format
        from django.http import JsonResponse
        
        posts_data = []
        for post in paginated_posts:
            comments = getattr(post, 'comment_count', 0) or 0
            views = getattr(post, 'views', 0) or 0
            
            # 상태 레이블 결정
            if comments >= 10:
                status_label = "방금 댓글 달림"
            elif views >= 20:
                status_label = "지금 읽는 중"
            else:
                status_label = "방금 올라옴"
            
            # URL 결정
            if post.post_type == 'free':
                url = f'/board/free/{post.pk}/'
            elif post.post_type == 'hotdeal':
                url = f'/board/hotdeal/{post.pk}/'
            else:  # parenting
                url = f'/board/parenting/{post.pk}/'
            
            # 카테고리명
            if post.post_type == 'free':
                category = '자유톡'
            elif post.post_type == 'hotdeal':
                category = '핫딜'
            else:
                category = '육아정보'
            
            posts_data.append({
                'pk': post.pk,
                'title': post.title,
                'comments': comments,
                'views': views,
                'created_at': date_format(post.created_at, 'm.d H:i'),
                'status_label': status_label,
                'post_type': post.post_type,
                'category': category,
                'url': url,
                'popularity_score': post.popularity_score,
            })
        
        return JsonResponse({
            'posts': posts_data,
            'has_next': (offset + limit) < total_count,
            'page': page,
        })
    
    context = {
        'posts': paginated_posts,
        'total_count': total_count,
        'page': page,
        'limit': limit,
        'has_next': (offset + limit) < total_count,
    }
    return render(request, 'main/realtime_feed.html', context)


def today_quick_posts(request):
    """오늘 작성된 오늘의 한 줄 목록 조회"""
    from datetime import date
    from django.http import JsonResponse
    
    today = date.today()
    quick_posts = FreePost.objects.filter(
        category='talk',
        created_at__date=today
    ).select_related('author').order_by('-created_at')
    
    posts_data = []
    for post in quick_posts:
        posts_data.append({
            'id': post.id,
            'content': post.content,
            'author': post.author.nickname if not post.is_anonymous else '익명',
            'created_at': post.created_at.strftime('%H:%M'),
            'is_anonymous': post.is_anonymous,
        })
    
    return JsonResponse({
        'count': len(posts_data),
        'posts': posts_data
    })


# 26-01-09: 달력 기록 저장 API
@login_required
@require_POST
def save_calendar_record(request):
    """달력 기록 저장 (로그인 필수)"""
    try:
        data = json.loads(request.body)
        date_key = data.get('date_key')  # YYYY-MM-DD
        content = data.get('content', '').strip()
        
        if not date_key:
            return JsonResponse({'success': False, 'error': '날짜가 필요합니다.'}, status=400)
        
        if content:
            # 기록 저장 또는 업데이트
            record, created = CalendarRecord.objects.update_or_create(
                user=request.user,
                record_date=date_key,
                defaults={'content': content}
            )
            return JsonResponse({'success': True, 'message': '저장되었습니다.'})
        else:
            # 내용이 비어있으면 삭제
            CalendarRecord.objects.filter(user=request.user, record_date=date_key).delete()
            return JsonResponse({'success': True, 'message': '삭제되었습니다.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def get_calendar_records(request):
    """달력 기록 불러오기 (로그인 필수)"""
    year = request.GET.get('year', 2026)
    records = CalendarRecord.objects.filter(
        user=request.user,
        record_date__year=year
    ).values('record_date', 'content')
    
    # YYYY-MM-DD: content 형식으로 변환
    records_dict = {}
    for record in records:
        date_key = record['record_date'].strftime('%Y-%m-%d')
        records_dict[date_key] = record['content']
    
    return JsonResponse({'success': True, 'records': records_dict})
