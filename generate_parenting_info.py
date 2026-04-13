import os
import django
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mompjt.settings')
django.setup()

from board.models import ParentingInfo
from accounts.models import User
from django.utils import timezone
import random

# 관리자 계정 찾기 또는 생성
admin = User.objects.filter(is_staff=True).first()
if not admin:
    admin = User.objects.create_user(username='admin', password='admin123', is_staff=True, is_superuser=True)
    print(f'관리자 계정 생성: {admin.username}')
else:
    print(f'기존 관리자: {admin.username}')

# ParentingInfo 제목들
titles = [
    '신생아 황달 증상 및 대처법',
    '예방접종 일정 완벽 가이드',
    '아기 수면 교육 방법 (수면 훈련)',
    '이유식 시작 전 필수 준비물',
    '월령별 아기 발달 체크리스트 (0-6개월)',
    '아기 배앓이 원인과 해결 방법',
    '신생아 황달 증상 및 관리',
    '아기 피부 트러블 관리 및 예방',
    '수유부 영양 식단 가이드',
    '아기 안전 낙상 예방 및 홈 세이프티',
    '신생아 특화 제품 추천 및 선택 가이드',
    '아기 울음의 의미 이해하기',
    '아기 에너지 필요량 및 영양 관리',
    '아기 배변 관찰 포인트',
    '월령별 인지 발달을 위한 활동',
    '육아용품 필수 vs 선택용품 정리',
    '아기 호흡 패턴 이해하기',
    '영아 급사 증후군(SIDS) 예방법',
    '신생아 장기 건강검진 일정',
    '아기 기저귀 선택 및 관리 팁'
]

contents = [
    '신생아의 60~80%가 경험하는 황달. 정상 범위 내 황달은 자연적으로 회복되지만, 광선요법이 필요한 경우도 있습니다. 신생아의 피부와 눈이 노란색으로 변하는 것이 주 증상입니다.',
    '생후 2개월부터 5세까지의 필수 백신 일정을 정리했습니다. 정기적인 예방접종은 감염병으로부터 아이를 보호하는 가장 효과적인 방법입니다.',
    '아기가 자연스럽게 좋은 수면 습관을 가지도록 도와주는 수면 훈련 방법을 소개합니다. 생후 4-6개월부터 시작할 수 있습니다.',
    '아기에게 새로운 맛을 소개하기 전에 필요한 도구, 식재료, 위생 관리법을 정리했습니다.',
    '0-3개월과 3-6개월 시기별로 아기가 보여야 할 발달 단계를 체계적으로 정리했습니다.',
    '아기의 복부 불편함으로 인한 울음. 마사지, 자세 변경, 따뜻한 물주머니 등의 해결법을 제시합니다.',
    '신생아 황달의 종류, 증상, 치료 방법에 대해 상세히 설명합니다.',
    '아기의 예민한 피부를 위한 제품 선택과 피부 질환 관리법을 소개합니다.',
    '수유 중인 엄마가 피해야 할 음식과 영양가 높은 음식을 정리했습니다.',
    '아기 침대 높이 조정, 콘센트 안전 커버, 계단 펜스 등 홈 세이프티 체크리스트입니다.',
    '신생아용 기저귀, 아기 침대, 유모차 등 아기용품 선택 기준을 제시합니다.',
    '아기가 우는 이유는 다양합니다. 배고픔, 졸음, 불편함 등 울음 종류별 해석을 돕습니다.',
    '월령별 아기의 에너지 요구량과 영양 균형을 맞추는 방법을 설명합니다.',
    '아기의 대변 색상, 횟수, 냄새로 건강 상태를 파악하는 방법을 알려드립니다.',
    '0-12개월 아기를 위한 시각, 청각, 촉각 자극 활동을 소개합니다.',
    '꼭 필요한 육아용품과 낭비할 수 있는 제품을 구분하여 정리했습니다.',
    '정상적인 아기 호흡 패턴과 주의해야 할 호흡 문제를 설명합니다.',
    '아기를 바르게 눕히고, 과열 방지, 담배 연기 회피 등 SIDS 예방법입니다.',
    '생후 1개월, 2개월, 4개월, 6개월의 건강검진 항목과 중요성을 정리했습니다.',
    '기저귀 종류별 특징과 아기 피부 건강을 위한 기저귀 관리법을 소개합니다.'
]

print("=" * 60)
print("육아정보 게시판 샘플 데이터 생성 시작")
print("=" * 60)

# 기존 데이터 확인
existing_count = ParentingInfo.objects.count()
print(f"기존 육아정보 게시물: {existing_count}개")

# 20개 글 생성
for i in range(20):
    post = ParentingInfo.objects.create(
        title=titles[i],
        content=contents[i],
        author=admin,
        category='육아정보',
        views=random.randint(100, 1000),
        comment_count=random.randint(5, 50),
        created_at=timezone.now() - timedelta(hours=random.randint(1, 480))
    )
    post.popularity_score = (post.comment_count * 5 + post.views)
    post.save()
    print(f'✓ {i+1}. {post.title}')

# 최종 확인
final_count = ParentingInfo.objects.count()
print("=" * 60)
print(f"✅ 생성 완료!")
print(f"   기존: {existing_count}개 → 현재: {final_count}개")
print(f"   추가된 글: {final_count - existing_count}개")
print("=" * 60)
