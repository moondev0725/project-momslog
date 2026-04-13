# ═══════════════════════════════════════════════════════════════════════
# chat/models.py
# 맘스로그 프로젝트 - 실시간 채팅 모델
# ═══════════════════════════════════════════════════════════════════════
# 작성일: 2026-01-02
# 모델:
#   1. ChatRoom: 채팅방 (제목, 설명, 멤버 수, 생성일)
#   2. ChatMessage: 채팅 메시지 (채팅방, 사용자, 메시지 내용, 시간)
#   3. ChatRoomMember: 채팅방 멤버 (채팅방, 사용자, 참여일)
# ═══════════════════════════════════════════════════════════════════════

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class ChatRoom(models.Model):
    """
    채팅방 모델
    """
    CATEGORY_CHOICES = [
        ('general', '일반수다'),
        ('work', '퇴근후수다'),
        ('parenting', '육아이야기'),
        ('tips', '꿀팁공유'),
    ]
    
    title = models.CharField(max_length=100, verbose_name="채팅방 제목")
    description = models.TextField(blank=True, null=True, verbose_name="채팅방 설명")
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='general',
        verbose_name="카테고리"
    )
    
    # 생성자 및 멤버
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_chatrooms', verbose_name="생성자")
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through='ChatRoomMember', related_name='joined_chatrooms', verbose_name="멤버")
    
    # 메타 정보
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")
    is_active = models.BooleanField(default=True, verbose_name="활성 여부")
    max_members = models.IntegerField(default=100, verbose_name="최대 멤버 수")
    
    class Meta:
        verbose_name = '채팅방'
        verbose_name_plural = '채팅방'
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.title
    
    def member_count(self):
        """현재 참여 중인 멤버 수"""
        return self.members.count()


class ChatMessage(models.Model):
    """
    채팅 메시지 모델
    """
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages', verbose_name="채팅방")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="사용자")
    content = models.TextField(verbose_name="메시지 내용")
    
    # 메타 정보
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")
    is_edited = models.BooleanField(default=False, verbose_name="수정 여부")
    edited_at = models.DateTimeField(blank=True, null=True, verbose_name="수정일")
    
    class Meta:
        verbose_name = '채팅 메시지'
        verbose_name_plural = '채팅 메시지'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['room', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"


class ChatRoomMember(models.Model):
    """
    채팅방 멤버 모델
    사용자가 어느 채팅방에 참여했는지 추적
    """
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, verbose_name="채팅방")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="사용자")
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="참여일")
    last_read_at = models.DateTimeField(auto_now=True, verbose_name="마지막 읽은 시간")
    is_muted = models.BooleanField(default=False, verbose_name="알림 차단")
    
    class Meta:
        verbose_name = '채팅방 멤버'
        verbose_name_plural = '채팅방 멤버'
        unique_together = ('room', 'user')
        ordering = ['-joined_at']


# ═══════════════════════════════════════════════════════════════════════
# 🌙 새벽 2시의 수다 (Midnight Chat) - WebSocket 기반 실시간 채팅
# ═══════════════════════════════════════════════════════════════════════
# 새벽 수유로 잠 못 자는 엄마들을 위한 익명 채팅
# 운영시간: 밤 12시(00:00) ~ 새벽 5시(05:00)
# 기술: Django Channels WebSocket (양방향 실시간 통신)
# ═══════════════════════════════════════════════════════════════════════

from django.utils import timezone
from datetime import datetime, time

class MidnightChatRoom(models.Model):
    """
    새벽 2시의 수다 - 익명 채팅방 모델
    - 하나의 고정 채팅방만 존재 (singleton)
    - 밤 12시 ~ 새벽 5시에만 활성화
    - 사용자 익명 처리 (session_id로 식별)
    """
    title = models.CharField(
        max_length=100,
        default="🌙 새벽 2시의 수다",
        verbose_name="채팅방 제목"
    )
    description = models.TextField(
        default="새벽 수유로 외로운 엄마들의 따뜻한 수다 공간",
        verbose_name="채팅방 설명"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    is_active = models.BooleanField(default=True, verbose_name="활성 여부")
    
    # 운영 시간 설정
    start_hour = models.IntegerField(default=0, verbose_name="시작 시간 (00:00)")
    end_hour = models.IntegerField(default=5, verbose_name="종료 시간 (05:00)")
    
    class Meta:
        verbose_name = '새벽 2시 채팅방'
        verbose_name_plural = '새벽 2시 채팅방'
    
    def __str__(self):
        return self.title
    
    @staticmethod
    def is_midnight_hours():
        """
        현재 시간이 운영 시간(00:00~05:00)인지 확인
        True: 운영 중 / False: 운영 시간 아님
        """
        now = timezone.now()
        current_hour = now.hour
        # 밤 12시(0시)부터 새벽 5시 이전까지
        return 0 <= current_hour < 5
    
    @staticmethod
    def get_or_create_midnight_room():
        """
        새벽 채팅방 가져오기 또는 생성 (singleton pattern)
        """
        room, created = MidnightChatRoom.objects.get_or_create(
            pk=1,  # 항상 pk=1로 유지 (하나의 채팅방만)
            defaults={
                'title': '🌙 새벽 2시의 수다',
                'description': '새벽 수유로 외로운 엄마들의 따뜻한 수다 공간',
            }
        )
        return room


class MidnightChatMessage(models.Model):
    """
    새벽 2시의 수다 - 메시지 모델
    - 익명 처리 (session_id 기반)
    - 타임스탬프와 익명 닉네임 저장
    """
    room = models.ForeignKey(
        MidnightChatRoom,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name="채팅방"
    )
    
    # 익명 처리: session_id로 사용자 식별
    # 실제 사용자 정보는 저장하지 않음 (익명성 보장)
    session_id = models.CharField(
        max_length=100,
        verbose_name="세션 ID (익명 식별용)"
    )
    
    # 익명 닉네임 (자동 생성: "엄마#1234" 형식)
    anonymous_nickname = models.CharField(
        max_length=20,
        default="익명의 엄마",
        verbose_name="익명 닉네임"
    )
    
    # 메시지 내용
    content = models.TextField(verbose_name="메시지 내용")
    
    # 메타 정보
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")
    
    class Meta:
        verbose_name = '새벽 2시 메시지'
        verbose_name_plural = '새벽 2시 메시지'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['room', '-created_at']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"{self.anonymous_nickname}: {self.content[:50]}"
    
    def __str__(self):
        return f"{self.room.title} - {self.user.username}"
