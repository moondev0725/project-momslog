from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('growth/', views.growth_chart, name='growth_chart'),
    path('map/', views.map_view, name='map'),  # 26-01-05 슬기 추가: 지도 뷰
    path('realtime-feed/', views.realtime_feed, name='realtime_feed'),  # 26-01-05 슬기 추가: 실시간 반응 피드
    path('today-quick-posts/', views.today_quick_posts, name='today_quick_posts'),  # 오늘의 한 줄 목록
    path('calendar/save/', views.save_calendar_record, name='save_calendar_record'),  # 26-01-09: 달력 기록 저장
    path('calendar/get/', views.get_calendar_records, name='get_calendar_records'),  # 26-01-09: 달력 기록 불러오기
]
