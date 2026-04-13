"""
==================== WSGI 설정 ====================
WSGI: Web Server Gateway Interface
- Django 애플리케이션을 웹 서버와 연결하는 인터페이스
- 운영환경에서 Apache, Nginx 등 웹 서버와 통신할 때 사용
- Gunicorn, uWSGI 등의 WSGI 서버와 함께 사용

For more information:
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# ==================== Django 설정 파일 지정 ====================
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mompjt.settings')

# ==================== WSGI 애플리케이션 생성 ====================
# 이 application 객체를 WSGI 서버에 전달하여 요청 처리
application = get_wsgi_application()
