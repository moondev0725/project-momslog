# ═══════════════════════════════════════════════════════════════════════
# chat/urls.py
# ═══════════════════════════════════════════════════════════════════════

from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_lobby, name='chat_lobby'),  # 채팅 로비
    path('room/<int:room_id>/', views.chat_room, name='chat_room'),  # 채팅방
    path('room/<int:room_id>/send/', views.send_message, name='send_message'),  # 메시지 전송
    path('room/<int:room_id>/fetch/', views.fetch_messages, name='fetch_messages'),  # 메시지 조회
    path('room/<int:room_id>/leave/', views.leave_room, name='leave_room'),  # 채팅방 나가기
    
    # ★ 26-01-02 추가: 🌙 새벽 2시의 수다 (WebSocket 기반 익명 채팅)
    path('midnight/', views.midnight_chat, name='midnight_chat'),  # 새벽 채팅방 페이지

    # Popup Widget APIs (Ajax)
    path('api/rooms/', views.api_rooms, name='api_rooms'),  # GET: 방 목록
    path('api/rooms/<int:room_id>/join/', views.api_join_room, name='api_join_room'),  # POST: 방 참여 보장
    path('api/rooms/<int:room_id>/member-info/', views.api_member_info, name='api_member_info'),  # GET: 사용자 정보
    path('api/rooms/<int:room_id>/leave/', views.leave_room_popup, name='leave_room_popup'),  # POST: 방 나가기 (팝업용)
    path('room/<int:room_id>/clear/', views.clear_room_messages, name='clear_room_messages'),  # POST: 메시지 전체 삭제
]
