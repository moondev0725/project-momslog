# ═══════════════════════════════════════════════════════════════════════
# board/utils.py
# 게시글 인기도 계산 유틸리티
# 26-01-05 슬기 추가
# ═══════════════════════════════════════════════════════════════════════

from datetime import datetime, timedelta
from django.utils import timezone


def calculate_popularity_score(post, user_region=None):
    """
    게시글의 인기도 점수를 계산합니다.
    
    인기점수 = (조회수 × 0.2) + (댓글수 × 2) + (저장수 × 3) + (공감 × 1.5) - 시간감쇠
    
    Args:
        post: FreePost, HotDeal, 또는 ParentingInfo 게시글 객체
        user_region: 사용자의 지역 (선택사항, 지역 가중치 적용용)
    
    Returns:
        float: 계산된 인기도 점수
    """
    
    # 기본 점수 계산
    views_score = post.views * 0.2
    comments_score = post.comment_count * 2
    bookmarks_score = post.bookmark_count * 3
    
    # 공감 점수 합산 (모든 종류의 리액션)
    empathy_reactions = 0
    if hasattr(post, 'reaction_empathy'):
        empathy_reactions += post.reaction_empathy
    if hasattr(post, 'reaction_courage'):
        empathy_reactions += post.reaction_courage
    if hasattr(post, 'reaction_cheer'):
        empathy_reactions += post.reaction_cheer
    if hasattr(post, 'reaction_support'):
        empathy_reactions += post.reaction_support
    if hasattr(post, 'reaction_thanks'):
        empathy_reactions += post.reaction_thanks
    
    empathy_score = empathy_reactions * 1.5
    
    # 지역 가중치
    region_weight = 0
    if user_region and hasattr(post, 'region') and post.region:
        if post.region == user_region:
            region_weight = 10  # 같은 지역
        else:
            region_weight = 2   # 같은 시
    
    # 시간 감쇠 계산
    now = timezone.now()
    elapsed_hours = (now - post.created_at).total_seconds() / 3600
    time_decay = elapsed_hours * 0.3
    
    # 최종 점수
    total_score = views_score + comments_score + bookmarks_score + empathy_score + region_weight - time_decay
    
    return max(0, total_score)  # 음수 방지


def get_popularity_icon(score):
    """
    점수에 따라 인기도 아이콘을 반환합니다.
    
    Args:
        score: 인기도 점수
    
    Returns:
        str: 아이콘 (또는 빈 문자열)
    """
    if score >= 100:
        return "fire-3"  # CSS에서 처리
    elif score >= 60:
        return "fire-2"
    elif score >= 30:
        return "fire-1"
    return ""


def update_post_popularity(post):
    """
    게시글의 인기도 점수를 업데이트합니다.
    
    Args:
        post: 업데이트할 게시글 객체
    """
    post.popularity_score = calculate_popularity_score(post)
    post.save(update_fields=['popularity_score'])


def batch_update_popularity(queryset):
    """
    여러 게시글의 인기도 점수를 일괄 업데이트합니다.
    
    Args:
        queryset: 업데이트할 게시글 쿼리셋
    """
    for post in queryset:
        update_post_popularity(post)
