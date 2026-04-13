# ═══════════════════════════════════════════════════════════════════════
# chat/management/commands/create_default_chatrooms.py
# 기본 채팅방 생성 스크립트
# ═══════════════════════════════════════════════════════════════════════

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from chat.models import ChatRoom

User = get_user_model()


class Command(BaseCommand):
    help = '기본 채팅방을 생성합니다.'

    def handle(self, *args, **options):
        # admin 사용자 확인 또는 생성
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={'is_staff': True, 'is_superuser': True}
        )
        
        # 기본 채팅방 목록
        rooms_data = [
            {
                'title': '육아 퇴근 후 수다',
                'description': '퇴근 후 육아하며 지친 엄마들이 모여 따뜻한 수다를 떠는 공간입니다.',
                'category': 'work',
            },
            {
                'title': '일반 수다방',
                'description': '일상적인 이야기를 자유롭게 나누는 공간입니다.',
                'category': 'general',
            },
            {
                'title': '육아 경험담',
                'description': '육아하면서 겪은 이야기와 팁을 공유합니다.',
                'category': 'parenting',
            },
            {
                'title': '꿀팁 공유 방',
                'description': '유용한 생활 꿀팁과 정보를 공유합니다.',
                'category': 'tips',
            },
        ]
        
        for room_data in rooms_data:
            room, created = ChatRoom.objects.get_or_create(
                title=room_data['title'],
                defaults={
                    'description': room_data['description'],
                    'category': room_data['category'],
                    'creator': admin_user,
                }
            )
            
            if created:
                # 생성된 경우 admin 사용자를 멤버로 추가
                room.members.add(admin_user)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ 채팅방 생성: {room.title}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  이미 존재: {room.title}')
                )
        
        self.stdout.write(self.style.SUCCESS('✨ 기본 채팅방 생성 완료!'))
