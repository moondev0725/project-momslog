from django.contrib import admin
from .models import ChatRoom, ChatMessage, ChatRoomMember

# ═══════════════════════════════════════════════════════════════════════
# chat/admin.py
# 맘스로그 프로젝트 - 실시간 채팅 관리자 패널
# ═══════════════════════════════════════════════════════════════════════
# 작성일: 2026-01-02
# 기능: 채팅방, 메시지, 멤버 관리자 등록
# ═══════════════════════════════════════════════════════════════════════


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'creator', 'get_member_count', 'created_at', 'is_active')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_member_count(self, obj):
        return obj.member_count()
    get_member_count.short_description = '멤버 수'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('room', 'user', 'content_preview', 'created_at', 'is_edited')
    list_filter = ('room', 'created_at', 'is_edited')
    search_fields = ('content', 'user__username', 'room__title')
    readonly_fields = ('created_at', 'edited_at')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '내용'


@admin.register(ChatRoomMember)
class ChatRoomMemberAdmin(admin.ModelAdmin):
    list_display = ('room', 'user', 'joined_at', 'is_muted')
    list_filter = ('room', 'joined_at', 'is_muted')
    search_fields = ('room__title', 'user__username')
    readonly_fields = ('joined_at', 'last_read_at')
