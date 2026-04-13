"""
자유게시판 공감 게시글 30개 추가 스크립트
Django shell에서 실행: python manage.py shell < create_empathy_posts.py
"""

from board.models import FreePost
from accounts.models import User
from django.utils import timezone
from datetime import timedelta
import random

# 기본 사용자 (없으면 생성)
try:
    user = User.objects.first()
    if not user:
        user = User.objects.create_user(username='sample_user', password='1234')
except:
    user = User.objects.first()

# 공감 글 샘플 데이터
sample_titles = [
    "나만 이렇게 지치는 거 아니죠...",
    "출산 후 부부 사이 정말 변했어요",
    "워킹맘 죄책감 이거 정상인가요",
    "아이 훈육 때문에 자책해요",
    "모유수유 힘들다는 걸 왜 진작 안 했을까",
    "육아로 인한 우울증 정말 심해요",
    "남편이 육아를 안 도와줄 때 정말 화나요",
    "이 시간대 밤새우기 정말 힘들어요",
    "아이가 떼를 쓸 때 정말 미칠 것 같아요",
    "엄마라는 이유만으로 모든 게 내 책임인가요",
    "첫째 낳고 둘째 안 낳기로 결정했어요",
    "어린이집 등원 거부하는 아이 때문에 스트레스",
    "엄마 친구들이 자꾸 아이 비교를 해요",
    "시댁 간섭이 정말 심해요",
    "아이 교육비 때문에 마음이 안 놓여요",
    "정신병에 걸린 것 같아요",
    "육아와 일 병행 정말 어렵네요",
    "자녀 교육 방식으로 남편과 싸워요",
    "혼자라고 느껴져서 정말 외로워요",
    "아이 친구 엄마들과의 관계가 복잡해요",
    "매일이 같은 일의 반복이에요",
    "아이 학교 성적이 걱정돼요",
    "잠을 못 자서 정신이 없어요",
    "사춘기 아이 대하기가 정말 힘들어요",
    "엄마도 외로움을 느껴요",
    "아이 앞에서 울고 싶지 않아요",
    "자존감이 바닥인 것 같아요",
    "매일 기계처럼 살고 있어요",
    "아이 때문에 내 꿈을 포기했어요",
    "이 일상에서 벗어나고 싶어요",
]

sample_content = [
    "정말 힘든데 다들 쉬운 척하는 거 아닌가 싶어요. 나만 왜 이렇게 힘들까.",
    "아이 낳기 전과 다르게 너무 힘들어요. 부부 관계도 뭔가 어색해지고...",
    "일도 하고 아이도 봐야 하고... 언제 쉬어요? 정말 힘들어요.",
    "아이를 혼내야 하는데 혼내고 나면 미안하고 자책해요.",
    "밤새 울어서 모유수유했는데 정말 힘들어요.",
    "아무도 이 심정을 모를 것 같아요. 정말 답답해요.",
    "남편은 왜 모르는 거예요? 이렇게 힘든데.",
    "아이가 안 자면 나도 안 자요. 언제부터 숨 쉴 시간이 생길까요.",
    "공공장소에서 울고 싶은 마음을 참기가 너무 힘들어요.",
    "왜 모든 책임이 엄마한테만 있는 걸까요?",
    "둘째는 정말 힘들 것 같아서 못 낳겠어요.",
    "아이가 어린이집을 거부해서 매일 아침이 전쟁이에요.",
    "아이를 비교하는 엄마 친구들 말이 자꾸 신경 쓰여요.",
    "시댁에서 육아에 대해 이래라저래라 말씀하셔서 정말 힘들어요.",
    "교육비가 계속 늘어나서 경제적으로도 힘들어요.",
    "정신과를 가야 하나 싶을 정도로 힘들어요.",
    "일도 제대로 못 하고 아이도 충분히 못 봐줄 것 같아요.",
    "아이 교육 방식을 놓고 남편과 자꾸 싸워요.",
    "정말 혼자라는 생각이 들어요.",
    "학교 엄마들과의 관계도 정말 복잡하고 피곤해요.",
    "매일 같은 일의 반복... 언제까지 이러는 걸까요?",
    "아이 성적이 잘 안 나오면 나도 우울해져요.",
    "잠도 못 자고 정신도 없어요.",
    "사춘기 자식과의 대화가 정말 어려워요.",
    "나도 외로움을 느껴요. 누가 알아줄까요?",
    "자식 앞에서 울기 싫은데 눈물이 자꾸만 나와요.",
    "내 자존감이 정말 바닥인 것 같아요.",
    "기계처럼 살고 있는 것 같아요.",
    "이 일상에서 벗어나고 정말 싶어요.",
    "엄마는 왜 이렇게 힘들 까요?",
]

# 30개 게시글 생성
print("공감 게시글 생성 시작...")
for i in range(30):
    try:
        post = FreePost(
            title=sample_titles[i % len(sample_titles)],
            content=sample_content[i % len(sample_content)],
            author=user,
            category='육아 수다',  # 카테고리 지정
            views=random.randint(100, 1000),
            comment_count=random.randint(10, 200),
            bookmark_count=random.randint(5, 100),
            reaction_empathy=random.randint(50, 500),  # 공감 반응
            is_anonymous=False,
            created_at=timezone.now() - timedelta(hours=random.randint(1, 240)),
        )
        
        # 인기도 점수 자동 계산
        post.popularity_score = (
            post.comment_count * 5 +
            post.views +
            post.bookmark_count * 3 +
            post.reaction_empathy * 2
        )
        
        post.save()
        print(f"✓ {i+1}. {post.title[:30]}")
    except Exception as e:
        print(f"✗ 게시글 {i+1} 생성 실패: {e}")

print(f"\n총 {FreePost.objects.filter(category='육아 수다').count()}개의 육아 수다 게시글이 생성되었습니다!")
