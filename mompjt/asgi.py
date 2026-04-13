"""
==================== ASGI 설정 ====================
ASGI: Asynchronous Server Gateway Interface
- Django의 비동기 지원을 위한 인터페이스
- WebSocket, 실시간 통신 등 비동기 작업이 필요할 때 사용
- Daphne, Uvicorn 등의 ASGI 서버와 함께 사용
- WSGI는 동기식, ASGI는 비동기식 처리 가능

For more information:
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

# ==================== Django 설정 파일 지정 ====================
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mompjt.settings')

# ==================== Django ASGI 애플리케이션 ====================
# HTTP 요청 처리
django_asgi_app = get_asgi_application()

# ==================== Django Channels WebSocket 라우팅 ====================
# chat.routing의 websocket_urlpatterns 임포트
from chat.routing import websocket_urlpatterns

# ==================== ASGI 애플리케이션 생성 (HTTP + WebSocket) ====================
# ProtocolTypeRouter: 프로토콜 타입에 따라 다른 애플리케이션으로 라우팅
# - 'http': 일반 HTTP 요청 (Django WSGI/ASGI)
# - 'websocket': WebSocket 요청 (Channels Consumer)
application = ProtocolTypeRouter({
    # HTTP 요청: 일반 Django 애플리케이션으로 처리
    'http': django_asgi_app,
    
    # WebSocket 요청: Channels Consumer로 처리
    # AuthMiddlewareStack: Django 인증 정보 전달
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns,  # chat/routing.py의 WebSocket URL 패턴
            )
        )
    ),
})
