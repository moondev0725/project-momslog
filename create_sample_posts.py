import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mompjt.settings')
django.setup()

from board.models import HotDeal
from accounts.models import User

# 관리자 계정 찾기 또는 생성
admin = User.objects.filter(is_staff=True).first()
if not admin:
    admin = User.objects.create_user(username='admin', password='admin123', is_staff=True, is_superuser=True)
    print(f'관리자 계정 생성: {admin.username}')
else:
    print(f'기존 관리자: {admin.username}')

# 글 1: 신년 이벤트
post1 = HotDeal.objects.create(
    title='🎉 신년 맞이 육아용품 대할인 행사!',
    content='새해를 맞아 인기 육아용품 50~70% 할인! \n- 아기옷: 50% 할인\n- 이유식 관련 용품: 60% 할인\n- 유모차/카시트: 70% 할인\n\n지금 사용 가능한 추가 쿠폰: 신규회원 20% 할인',
    category='event',
    author=admin,
    link='https://example.com/sale',
    price='최대 100,000원 할인'
)
print(f'글 1 생성: {post1.title}')

# 글 2: 체험단 모집
post2 = HotDeal.objects.create(
    title='👶 신생아 용품 체험단 모집! (무료배송)',
    content='아기 피부 케어용품 체험단을 모집합니다!\n\n📦 제공 상품:\n- 신생아 보습 크림 (정가 25,000원)\n- 아기 샴푸&바디워시 세트 (정가 18,000원)\n- 아기 물티슈 3팩 (정가 12,000원)\n\n✅ 체험 후 솔직한 후기 작성하면 선물 추가 제공!\n\n📍 선착순 100명 선정',
    category='event',
    author=admin,
    link='https://example.com/review',
    price='무료 제공'
)
print(f'글 2 생성: {post2.title}')
print('✅ HotDeal 글 2개 생성 완료!')
