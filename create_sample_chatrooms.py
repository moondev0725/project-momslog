"""
채팅방 샘플 데이터 생성 스크립트
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mompjt.settings')
django.setup()

from django.contrib.auth import get_user_model
from chat.models import ChatRoom, ChatRoomMember

User = get_user_model()

# 기본 사용자 가져오기 (없으면 생성)
admin_user, _ = User.objects.get_or_create(
    username='admin',
    defaults={'email': 'admin@momslog.com', 'is_superuser': True, 'is_staff': True}
)

# 5개의 샘플 채팅방 데이터
sample_rooms = [
    {
        'title': '일반수다',
        'description': '육아, 일상, 뭐든 편하게 얘기해요',
        'category': 'general',
    },
    {
        'title': '퇴근후수다',
        'description': '하루종일 아이들과 있다 저녁에 숨 쉬는 시간',
        'category': 'work',
    },
    {
        'title': '육아이야기',
        'description': '아이 발달, 교육, 건강에 대해 나눠요',
        'category': 'parenting',
    },
    {
        'title': '꿀팁공유',
        'description': '엄마들의 생활 노하우와 꿀팁을 공유합니다',
        'category': 'tips',
    },
    {
        'title': '맘둥이 장난감 나눔',
        'description': '아이가 안 쓰는 장난감, 옷 나눔하고 교환해요',
        'category': 'general',
    },
]

# 기존 채팅방 삭제 (초기화)
ChatRoom.objects.all().delete()

# 새로운 채팅방 생성
created_count = 0
for room_data in sample_rooms:
    room, created = ChatRoom.objects.get_or_create(
        title=room_data['title'],
        defaults={
            'description': room_data['description'],
            'category': room_data['category'],
            'creator': admin_user,
            'is_active': True,
        }
    )
    if created:
        # 관리자를 멤버로 추가
        ChatRoomMember.objects.get_or_create(room=room, user=admin_user)
        created_count += 1
        print(f"✅ 채팅방 생성: {room.title}")
    else:
        print(f"⚠️ 채팅방 이미 존재: {room.title}")

print(f"\n총 {created_count}개의 채팅방이 생성되었습니다.")
