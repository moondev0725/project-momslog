import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mompjt.settings')
django.setup()

from board.models import FreePost, HotDeal, ParentingInfo

# 서울의 주요 지역별 좌표
coordinates_data = [
    # 강남
    {'lat': 37.4979, 'lng': 127.0276, 'district': '강남구', 'dong': '강남역'},
    {'lat': 37.5240, 'lng': 127.0227, 'district': '강남구', 'dong': '신사동'},
    {'lat': 37.5113, 'lng': 127.0283, 'district': '강남구', 'dong': '논현동'},
    # 서초
    {'lat': 37.4838, 'lng': 127.0175, 'district': '서초구', 'dong': '서초동'},
    {'lat': 37.5024, 'lng': 126.9961, 'district': '서초구', 'dong': '반포동'},
    # 마포
    {'lat': 37.5547, 'lng': 126.9224, 'district': '마포구', 'dong': '홍대입구'},
    {'lat': 37.5791, 'lng': 126.8893, 'district': '마포구', 'dong': '상암동'},
    # 송파
    {'lat': 37.5133, 'lng': 127.0827, 'district': '송파구', 'dong': '잠실동'},
    {'lat': 37.4849, 'lng': 127.1235, 'district': '송파구', 'dong': '문정동'},
    # 동작
    {'lat': 37.5142, 'lng': 126.9719, 'district': '동작구', 'dong': '노량진동'},
    # 종로
    {'lat': 37.5735, 'lng': 126.9779, 'district': '종로구', 'dong': '종로3가'},
    # 중구
    {'lat': 37.5640, 'lng': 126.9976, 'district': '중구', 'dong': '명동'},
]

print("📊 현재 게시물 통계\n")

free_count = FreePost.objects.count()
hot_count = HotDeal.objects.count()
parenting_count = ParentingInfo.objects.count()

print(f"FreePost: {free_count}개")
print(f"HotDeal: {hot_count}개")
print(f"ParentingInfo: {parenting_count}개\n")

# 모든 게시물 조회
all_posts = []
for post in FreePost.objects.all()[:15]:
    post.region = '서울'
    all_posts.append(post)
    
for post in HotDeal.objects.all()[:10]:
    post.region = '서울'
    all_posts.append(post)
    
for post in ParentingInfo.objects.all()[:10]:
    post.region = '서울'
    all_posts.append(post)

print(f"업데이트할 게시물 수: {len(all_posts)}\n")

# 좌표 할당
for idx, post in enumerate(all_posts):
    coord = coordinates_data[idx % len(coordinates_data)]
    post.region = '서울'
    post.district = coord['district']
    post.dong = coord['dong']
    post.latitude = coord['lat']
    post.longitude = coord['lng']
    post.save()
    print(f"✓ {post.__class__.__name__} ID {post.id}: {coord['district']} {coord['dong']} ({coord['lat']}, {coord['lng']})")

print(f"\n✓ 총 {len(all_posts)}개 게시물 좌표 추가 완료!")
