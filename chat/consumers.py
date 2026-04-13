# ═══════════════════════════════════════════════════════════════════════
# chat/consumers.py
# 새벽 2시의 수다 - WebSocket Consumer
# ═══════════════════════════════════════════════════════════════════════
# 기능:
#   - WebSocket 연결/해제 관리
#   - 양방향 실시간 메시지 송수신
#   - 익명 닉네임 생성 (엄마#1234 형식)
#   - 시간 제한 확인 (00:00~05:00)
#   - 현재 접속자 수 계산 및 브로드캐스트
# ═══════════════════════════════════════════════════════════════════════

import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import MidnightChatRoom, MidnightChatMessage


class MidnightChatConsumer(AsyncWebsocketConsumer):
    """
    새벽 2시의 수다 WebSocket Consumer
    
    기능:
    - 사용자 연결/해제 처리
    - 메시지 수신 및 DB 저장
    - 모든 접속자에게 실시간 브로드캐스트
    - 익명 닉네임 자동 생성
    """
    
    async def connect(self):
        """
        WebSocket 연결 이벤트
        1. 시간 제한 확인
        2. session_id 생성 (익명성)
        3. 익명 닉네임 생성
        4. group 추가
        5. 현재 접속자 수 브로드캐스트
        """
        
        # 시간 제한 확인: 00:00 ~ 05:00만 허용
        if not await self.is_midnight_hours():
            await self.close(code=4000, reason="Operating hours: 00:00 - 05:00 only")
            return
        
        # 그룹 이름 설정 (고정: "midnight_chat_group")
        self.room_group_name = 'midnight_chat_group'
        self.room_name = 'midnight'
        
        # 세션 ID와 익명 닉네임 생성
        self.session_id = self.generate_session_id()
        self.anonymous_nickname = self.generate_anonymous_nickname()
        
        # 채널 그룹에 추가 (모든 사용자가 같은 그룹)
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # WebSocket 연결 수락
        await self.accept()
        
        # 사용자 입장 메시지 브로드캐스트
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_join',
                'session_id': self.session_id,
                'anonymous_nickname': self.anonymous_nickname,
            }
        )
    
    async def disconnect(self, close_code):
        """
        WebSocket 연결 해제 이벤트
        1. 그룹에서 제거
        2. 사용자 퇴장 메시지 브로드캐스트
        """
        
        # 채널 그룹에서 제거
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # 사용자 퇴장 메시지 브로드캐스트
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_leave',
                'session_id': self.session_id,
                'anonymous_nickname': self.anonymous_nickname,
            }
        )
    
    async def receive(self, text_data):
        """
        클라이언트로부터 메시지 수신
        1. JSON 파싱
        2. DB에 저장
        3. 모든 접속자에게 브로드캐스트
        """
        try:
            data = json.loads(text_data)
            message_content = data.get('message', '').strip()
            
            # 빈 메시지 무시
            if not message_content:
                return
            
            # 시간 제한 재확인 (메시지 전송 시점)
            if not await self.is_midnight_hours():
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': '새벽 2시의 수다는 00:00~05:00에만 이용 가능합니다.',
                }))
                return
            
            # DB에 메시지 저장
            message_obj = await self.save_message(
                session_id=self.session_id,
                anonymous_nickname=self.anonymous_nickname,
                content=message_content
            )
            
            # 모든 접속자에게 메시지 브로드캐스트
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message_id': message_obj.id,
                    'session_id': self.session_id,
                    'anonymous_nickname': self.anonymous_nickname,
                    'content': message_content,
                    'created_at': message_obj.created_at.isoformat(),
                }
            )
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format',
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Error: {str(e)}',
            }))
    
    # ═══════════════════════════════════════════════════════════════════════
    # 브로드캐스트 이벤트 핸들러
    # ═══════════════════════════════════════════════════════════════════════
    
    async def chat_message(self, event):
        """
        chat_message 타입 메시지 수신
        모든 접속자에게 전송
        """
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message_id': event['message_id'],
            'anonymous_nickname': event['anonymous_nickname'],
            'content': event['content'],
            'created_at': event['created_at'],
            'is_own_message': event['session_id'] == self.session_id,
        }))
    
    async def user_join(self, event):
        """
        user_join 타입 메시지 수신
        새 사용자 입장 알림 + 현재 접속자 수
        """
        # 현재 접속자 수 계산
        current_count = await self.get_active_users_count()
        
        await self.send(text_data=json.dumps({
            'type': 'user_join',
            'anonymous_nickname': event['anonymous_nickname'],
            'active_users_count': current_count,
        }))
    
    async def user_leave(self, event):
        """
        user_leave 타입 메시지 수신
        사용자 퇴장 알림 + 현재 접속자 수
        """
        # 현재 접속자 수 계산
        current_count = await self.get_active_users_count()
        
        await self.send(text_data=json.dumps({
            'type': 'user_leave',
            'anonymous_nickname': event['anonymous_nickname'],
            'active_users_count': current_count,
        }))
    
    # ═══════════════════════════════════════════════════════════════════════
    # 헬퍼 메서드
    # ═══════════════════════════════════════════════════════════════════════
    
    @staticmethod
    def generate_session_id():
        """
        고유한 세션 ID 생성
        형식: 6자리 랜덤 숫자 + 타임스탬프
        """
        random_part = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        timestamp = int(timezone.now().timestamp() * 1000) % 10000
        return f"{random_part}{timestamp}"
    
    @staticmethod
    def generate_anonymous_nickname():
        """
        익명 닉네임 생성
        형식: 엄마#4자리 숫자
        """
        num = random.randint(1000, 9999)
        return f"엄마#{num}"
    
    @database_sync_to_async
    def save_message(self, session_id, anonymous_nickname, content):
        """
        메시지를 DB에 저장
        """
        room = MidnightChatRoom.get_or_create_midnight_room()
        message = MidnightChatMessage.objects.create(
            room=room,
            session_id=session_id,
            anonymous_nickname=anonymous_nickname,
            content=content,
        )
        return message
    
    @staticmethod
    @database_sync_to_async
    def is_midnight_hours():
        """
        현재 시간이 운영 시간(00:00~05:00)인지 확인
        """
        return MidnightChatRoom.is_midnight_hours()
    
    @staticmethod
    @database_sync_to_async
    def get_active_users_count():
        """
        현재 active 채널의 수 반환
        WebSocket Consumer에는 active_count 속성이 없으므로,
        최근 5분 내 메시지를 보낸 unique session_id 수로 추정
        """
        from datetime import timedelta
        from django.utils import timezone
        
        five_minutes_ago = timezone.now() - timedelta(minutes=5)
        active_session_ids = MidnightChatMessage.objects.filter(
            created_at__gte=five_minutes_ago
        ).values_list('session_id', flat=True).distinct().count()
        
        # 최소 1명 이상 (현재 사용자)
        return max(active_session_ids, 1)
