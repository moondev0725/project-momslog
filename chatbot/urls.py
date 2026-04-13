from django.urls import path
from . import views

app_name = 'chatbot'  # <--- 이 줄이 꼭 있어야 합니다!

urlpatterns = [
    path('', views.chatbot_view, name='chat'),
]