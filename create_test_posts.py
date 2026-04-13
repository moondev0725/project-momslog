#!/usr/bin/env python
"""
테스트 게시글 데이터 생성 (인기도 계산 테스트용)
d0105/mompjt 디렉토리에서 실행
python manage.py shell < create_test_posts.py
또는
python create_test_posts.py
"""

import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mompjt.settings')
django.setup()

from django.contrib.auth.models import User
from board.models import FreePost
from board.utils import update_post_popularity

# 관리자 사용자 가져오기 (없으면 생성)
admin_user, _ = User.objects.get_or_create(
    username='admin',
    defaults={'is_staff': True, 'is_superuser': True}
)

# 테스트 게시글 3개 생성
test_posts_data = [
    {
        'title': '어린이집 갑자기 휴원 안내',
        'content': '내일부터 1주일 휴원이라고 연락왔어요. 다들 어떻게 하세요? 같은 상황인 분들 계신가요? 급히 일정을 조정해야 할 것 같은데...',
        'views': 245,
        'comment_count': 38,
        'bookmark_count': 12,
        'reaction_empathy': 45,
        'region': 'seoul',
        'district': '강남구',
        'dong': '역삼동',
        'latitude': Decimal('37.4979'),
        'longitude': Decimal('127.0276'),
    },
    {
        'title': '학원 셔틀 사고 - 안전 문제',
        'content': '우리 동네 학원 셔틀이 신호위반했대요. 정말 위험하네요. 아이들이 타고 있었으면 어쩔 뻔했어요. 운영사에 항의했어요.',
        'views': 156,
        'comment_count': 42,
        'bookmark_count': 8,
        'reaction_courage': 52,
        'reaction_support': 38,
        'region': 'seoul',
        'district': '강남구',
        'dong': '논현동',
        'latitude': Decimal('37.5074'),
        'longitude': Decimal('127.0261'),
    },
    {
        'title': '학교 급식 식중독 사건',
        'content': '○○초등학교 급식에서 식중독 발생했다고 해요. 아이가 괜찮으신가요? 우리 아이는 다행히 그 날 도시락을 싸갔어요. 정말 위험해요.',
        'views': 389,
        'comment_count': 67,
        'bookmark_count': 15,
        'reaction_empathy': 78,
        'reaction_support': 91,
        'region': 'seoul',
        'district': '강남구',
        'dong': '신사동',
        'latitude': Decimal('37.5173'),
        'longitude': Decimal('127.0170'),
    },
]

created_count = 0
for post_data in test_posts_data:
    try:
        post = FreePost.objects.create(
            author=admin_user,
            category='mom',
            **post_data
        )
        # 인기도 점수 계산
        update_post_popularity(post)
        created_count += 1
        print(f"✓ 생성됨: {post.title} (인기도: {post.popularity_score:.1f})")
    except Exception as e:
        print(f"✗ 오류: {post_data['title']} - {e}")

print(f"\n총 {created_count}개의 테스트 게시글이 생성되었습니다.")
print("\n인기도 계산 공식:")
print("= (조회수 × 0.2) + (댓글수 × 2) + (저장수 × 3) + (공감 × 1.5) - 시간감쇠")
