"""
댓글 생성 스크립트
Featured post에 20개 이상의 댓글을 추가합니다.
"""
import os
import django
import random
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mompjt.settings')
django.setup()

from django.contrib.auth import get_user_model
from board.models import FreePost, FreeComment, HotDeal

User = get_user_model()

# 댓글 샘플 데이터
COMMENT_SAMPLES = [
    "저도 딱 3월에 그랬어요. 근데 2주만 딱 눈 딱 감고 버티니까 적응하더라고요.",
    "공감돼요... 저는 매일 울면서 출근했어요. 지금은 잘 다니는데 그때가 생각나네요.",
    "엄마 마음이 다 그렇죠. 아이가 울면 나도 같이 울고 싶어요 ㅠㅠ",
    "선생님이 괜찮다고 하시면 정말 금방 적응한대요. 저희도 그랬어요!",
    "처음엔 다들 그래요. 엄마 잘못 아니에요. 시간이 약입니다.",
    "우리 애는 첫날부터 신나서 들어가더니 지금은 가기 싫다고... 역시 육아는 정답이 없네요.",
    "동감합니다. 이게 맞나 싶을 때가 한두 번이 아니죠.",
    "저도 뒤돌아서 울었어요. 근데 CCTV 보니까 금방 놀더라고요 ㅋㅋ",
    "아이들은 적응력이 좋아요. 엄마가 더 힘들 수 있어요.",
    "지금은 힘들어도 나중엔 추억이 될 거예요. 화이팅!",
    "맞아요, 그 순간이 제일 힘들어요. 하지만 곧 지나가요.",
    "저는 한 달 걸렸어요. 아이마다 다른 것 같아요.",
    "선생님께 여쭤보세요. 생각보다 금방 울음 그치는 경우가 많대요.",
    "같은 마음이에요. 우리 모두 힘내요!",
    "처음이 제일 어렵죠. 조금만 버티면 나아질 거예요.",
    "이해해요. 저도 지금 겪고 있어서요. 함께 힘내요.",
    "엄마들은 다 이 과정을 거치는 것 같아요. 너무 자책하지 마세요.",
    "CCTV 확인해보세요. 생각보다 빨리 적응하는 경우가 많아요.",
    "다들 처음엔 힘들어요. 곧 익숙해질 거예요.",
    "저희 아이도 처음엔 엄청 울었는데 지금은 어린이집 가는 걸 좋아해요.",
    "시간이 지나면 엄마도 아이도 익숙해져요. 조금만 참아보세요.",
    "매일 힘들지만 그래도 해내는 우리 모두 대단해요!",
    "이 시기를 잘 넘기면 더 단단해질 거예요. 화이팅!",
]

def create_comments_for_top_posts():
    """인기 게시글에 댓글 20개 이상 추가"""
    
    # 관리자 계정 가져오기
    try:
        admin_user = User.objects.get(username='admin')
    except User.DoesNotExist:
        print("❌ admin 계정이 없습니다. 먼저 슈퍼유저를 생성하세요.")
        return
    
    # 일반 사용자들 가져오기 (없으면 admin만 사용)
    users = list(User.objects.all()[:5])
    if not users:
        users = [admin_user]
    
    print("=" * 60)
    print("📝 댓글 생성 시작")
    print("=" * 60)
    
    # 자유게시판 인기 글 가져오기
    free_posts = FreePost.objects.order_by('-popularity_score')[:5]
    for post in free_posts:
        print(f"\n자유게시판: {post.title}")
        for i in range(25):  # 25개 댓글 생성
            comment = FreeComment.objects.create(
                post=post,
                author=random.choice(users),
                content=random.choice(COMMENT_SAMPLES),
            )
            # 생성 시간 랜덤화
            comment.created_at = timezone.now() - timedelta(hours=random.randint(1, 48))
            comment.save()
            print(f"  ✅ 댓글 {i+1} 생성")
    
    print("\n" + "=" * 60)
    print("✅ 댓글 생성 완료!")
    print("=" * 60)

if __name__ == '__main__':
    create_comments_for_top_posts()
