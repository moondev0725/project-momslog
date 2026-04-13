#!/usr/bin/env python
"""
공지사항 게시판에 '이 카페가 필요한 이유' 글 3개 생성
d0105/mompjt 디렉토리에서 실행
python manage.py shell < create_notice_posts.py
또는
python create_notice_posts.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mompjt.settings')
django.setup()

from board.models import Notice

# 기존 공지사항 확인 (중복 방지)
existing = Notice.objects.filter(
    title__in=[
        "이 동네 정보, 왜 이렇게 흩어져 있을까?",
        "엄마들이 직접 만든 진짜 동네 지도",
        "광고 말고, 사람 얘기만 남기고 싶어서"
    ]
).exists()

if existing:
    print("이미 공지사항이 존재합니다. 중복 생성을 건너뜁니다.")
else:
    notices = [
        {
            'title': "이 동네 정보, 왜 이렇게 흩어져 있을까?",
            'content': """우리 동네 학교 공지는 학교 홈페이지에, 어린이집 소식은 카톡에, 진짜 평가는 블로그 리뷰에만 있어요. 

이 모든 정보를 한곳에서 찾을 수 있고, 엄마들이 직접 만드는 신뢰할 수 있는 지도가 필요했어요.

이제 맘스로그에서는:
- 어느 산부인과가 좋은지
- 어느 치과가 아이 친화적인지  
- 이 학원은 정말 괜찮은지
- 우리 동네의 모든 아이 관련 장소

이런 정보들을 한곳에서 찾을 수 있습니다. 우리 동네 엄마들의 솔직한 평가와 경험이 모여 있기 때문이에요.

지금 바로 가입하고 우리 동네 정보를 함께 만들어가세요!"""
        },
        {
            'title': "엄마들이 직접 만든 진짜 동네 지도",
            'content': """어느 산부인과가 좋은지, 어느 치과가 아이 친화적인지, 이 학원은 정말 괜찮은지 - 
이런 정보들이 네이버 평점에는 없어요. 

그래서 이곳은 엄마들 눈으로 검증된 정보만 모았습니다.

✓ 실제 다녀온 엄마들의 후기
✓ 숨겨진 강점과 약점까지 솔직하게
✓ "내 아이에게 맞나?"에 대한 답

우리가 만드는 지도는 어떤 광고보다 믿을 수 있어요.

왜냐하면 우리도 같은 엄마이고, 같은 동네에 살고 있거든요.

🗺️ 우리 동네를 함께 그려가세요!"""
        },
        {
            'title': "광고 말고, 사람 얘기만 남기고 싶어서",
            'content': """광고는 좋은 점만 보여줘요. 

하지만 엄마들은 진짜 사람들의 진짜 경험과 감정이 필요해요.

- "어린이집이 좋긴 한데..."
- "가격은 비싼데 질이..."
- "아이들이 나가는 게 싫어하더라고요"

이런 디테일한 얘기들이 있어야 실제 선택에 도움이 돼요.

그래서 이곳에선 솔직한 이야기들이 모이고, 그 속에서 우리는:

💬 서로를 이해하고
🤝 함께 결정하고  
💪 용기를 얻습니다

광고 없이 순수하게 엄마들의 목소리만 담은 커뮤니티.

이것이 맘스로그가 있는 이유입니다.

당신의 솔직한 이야기를 들려주세요. 누군가는 그 글을 읽고 결정을 내릴 거거든요."""
        }
    ]
    
    created_count = 0
    for notice_data in notices:
        notice = Notice.objects.create(**notice_data)
        created_count += 1
        print(f"✓ 생성됨: {notice.title} (ID: {notice.id})")
    
    print(f"\n총 {created_count}개의 공지사항이 생성되었습니다.")
