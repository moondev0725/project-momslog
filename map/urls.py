from django.urls import path
from . import views

app_name = 'map'

urlpatterns = [
    path('', views.map_view, name='map'),
    # 26-01-02: 일기장 기능이 board 앱으로 이동되었습니다.
    # URL: /board/free/diary/
]
