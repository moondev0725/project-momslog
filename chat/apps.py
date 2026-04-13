# ═══════════════════════════════════════════════════════════════════════
# chat/apps.py
# 맘스로그 프로젝트 - 실시간 채팅 앱 설정
# ═══════════════════════════════════════════════════════════════════════
# 작성일: 2026-01-02
# 수정일: 26-01-02 - verbose_name 추가 및 AppConfig 경로로 settings 등록
# ═══════════════════════════════════════════════════════════════════════

from django.apps import AppConfig


class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'
    verbose_name = '실시간 채팅'  # ★ 26-01-02 추가: Django가 chat을 앱으로 인식하도록 설정
