# ═══════════════════════════════════════════════════════════════════════
# chat/routing.py
# WebSocket URL 라우팅 설정
# ═══════════════════════════════════════════════════════════════════════
# Django Channels의 WebSocket 요청을 Consumer로 라우팅
# HTTP 요청과는 다르게, WebSocket은 이 파일에서 처리

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # 🌙 새벽 2시의 수다 WebSocket 경로
    # ws://localhost:8000/ws/midnight/ 로 연결
    re_path(r'ws/midnight/$', consumers.MidnightChatConsumer.as_asgi()),
]
