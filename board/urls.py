# ═══════════════════════════════════════════════════════════════════════
# board/urls.py
# 맘스로그 프로젝트 - 게시판 URL 라우팅
# ═══════════════════════════════════════════════════════════════════════
# 작성일: 2025-12-29
# URL 패턴:
#   [공지사항] /board/notice/, /board/notice/<pk>/, /board/notice/write/
#   [자유게시판] /board/free/, /board/free/write/
#   [벼룩시장] /board/flea/, /board/flea/<pk>/, /board/flea/create/, edit, delete
#   [벼룩시장 찜] /board/flea/<pk>/like/ (25-12-29 추가)
#   [벼룩시장 댓글] /board/flea/<pk>/comment/, edit, delete (25-12-29 추가)
#   [벼룩시장 상태] /board/flea/<pk>/status/ (25-12-29 추가 - AJAX)
#   [알림] /board/notification/, /board/notification/<pk>/read/ (25-12-29 추가)
# ═══════════════════════════════════════════════════════════════════════

from django.urls import path, include
from . import views

app_name = 'board'

urlpatterns = [
    # 1. 목록 보기
    path('notice/', views.notice_list, name='notice_list'),
    
    # 2. 글쓰기 (★ 이 줄이 없어서 에러가 난 것입니다! 꼭 추가해주세요)
    path('notice/write/', views.notice_write, name='notice_write'),
    
    # 3. 상세 보기
    path('notice/<int:pk>/', views.notice_detail, name='notice_detail'),
    
    # ▼▼▼ [자유게시판] ▼▼▼
    path('free/', views.free_list, name='free_list'),  # 목록
    # path('free/write/', views.free_create, name='free_create'),  # 글쓰기/
    path("free_write/", views.free_write, name="free_write"),   # ✅ 작성 페이지(GET)
    path("free_create/", views.free_create, name="free_create"),# ✅ 작성 처리(POST)
    path('free/<int:pk>/', views.free_detail, name='free_detail'),   # 게시글 🔥상세보기  # (혜은 25-12-31 추가)
    path('free/<int:pk>/edit/', views.free_update, name='free_update'),  # 게시글 수정    # (혜은 25-12-31 추가)
    path('free/<int:pk>/delete/', views.free_delete, name='free_delete'),  # 게시글 삭제  # (혜은 25-12-31 추가)
    path('free/<int:pk>/reaction/', views.free_reaction_toggle, name='free_reaction_toggle'),  # 감정 리액션 (26-01-02 추가)
    path('free/<int:post_id>/comment/create/', views.free_comment_create, name='free_comment_create'),  # 댓글 작성
    path('free/comment/<int:comment_id>/update/', views.free_comment_update, name='free_comment_update'),  # 댓글 수정
    path('free/comment/<int:comment_id>/delete/', views.free_comment_delete, name='free_comment_delete'),  # 댓글 삭제
    
    
    # ▼▼▼ [엄마 마음 케어 일기장] 26-01-02 추가 - 자유게시판 하위 ▼▼▼
    path('free/diary/', views.diary_list, name='diary_list'),
    path('free/diary/create/', views.diary_create, name='diary_create'),
    path('free/diary/<int:pk>/', views.diary_detail, name='diary_detail'),
    path('free/diary/<int:pk>/edit/', views.diary_edit, name='diary_edit'),
    path('free/diary/<int:pk>/delete/', views.diary_delete, name='diary_delete'),
    path('bamboo/', views.bamboo_diary_list, name='bamboo_diary_list'),  # 대나무숲 - 26-01-03 추가
    
    # ▼▼▼ [벼룩시장] ▼▼▼
    path('flea/', views.flea_list, name='flea_list'),
    path('flea/geo/', views.flea_geo_items, name='flea_geo_items'),  # 지도용 JSON
    path('flea/wishlist/', views.flea_wishlist, name='flea_wishlist'),  # 찜 목록
    path('flea/write/', views.flea_create, name='flea_create'),
    path('flea/<int:pk>/', views.flea_detail, name='flea_detail'),
    path('flea/<int:pk>/report/', views.flea_report_create, name='flea_report_create'),  # 신고
    path('flea/<int:pk>/comment/', views.flea_comment_create, name='flea_comment_create'),
    path('flea/<int:pk>/comment/<int:comment_id>/edit/', views.flea_comment_edit, name='flea_comment_edit'),
    path('flea/<int:pk>/comment/<int:comment_id>/delete/', views.flea_comment_delete, name='flea_comment_delete'),
    path('flea/<int:pk>/like/', views.flea_like_toggle, name='flea_like_toggle'),
    path('flea/<int:pk>/edit/', views.flea_edit, name='flea_edit'),
    path('flea/<int:pk>/delete/', views.flea_delete, name='flea_delete'),
    path('flea/<int:pk>/status/', views.flea_status_update, name='flea_status_update'),  # 25-12-29 추가
    
    # ▼▼▼ [핫딜공유] 26-01-02 슬기 추가: 핫딜공유 게시판 URL ▼▼▼
    path('hotdeal/', views.hotdeal_list, name='hotdeal_list'),  # 목록
    path('hotdeal/write/', views.hotdeal_create, name='hotdeal_create'),  # 글쓰기
    path('hotdeal/<int:pk>/', views.hotdeal_detail, name='hotdeal_detail'),  # 상세보기
    path('hotdeal/<int:pk>/edit/', views.hotdeal_update, name='hotdeal_update'),  # 수정
    path('hotdeal/<int:pk>/delete/', views.hotdeal_delete, name='hotdeal_delete'),  # 삭제
    
    # ▼▼▼ [육아정보] 26-01-02 슬기 추가: 육아정보 게시판 URL ▼▼▼
    path('parenting/', views.parenting_list, name='parenting_list'),  # 목록
    path('parenting/write/', views.parenting_create, name='parenting_create'),  # 글쓰기
    path('parenting/<int:pk>/', views.parenting_detail, name='parenting_detail'),  # 상세보기
    path('parenting/<int:pk>/edit/', views.parenting_update, name='parenting_update'),  # 수정
    path('parenting/<int:pk>/delete/', views.parenting_delete, name='parenting_delete'),  # 삭제
    # ▼▼▼ [육아정보 댓글] 자유게시판과 동일하게 CRUD 제공 ▼▼▼
    path('parenting/<int:post_id>/comment/create/', views.parenting_comment_create, name='parenting_comment_create'),  # 댓글 작성
    path('parenting/comment/<int:comment_id>/update/', views.parenting_comment_update, name='parenting_comment_update'),  # 댓글 수정
    path('parenting/comment/<int:comment_id>/delete/', views.parenting_comment_delete, name='parenting_comment_delete'),  # 댓글 삭제
    path('parenting/development-chart/', views.development_chart, name='development_chart'),  # 월령별 발달 차트
    
    # ▼▼▼ [알림] ▼▼▼
    path('notification/', views.notification_list, name='notification_list'),
    path('notification/<int:notification_id>/read/', views.notification_mark_as_read, name='notification_mark_as_read'),
    path('notification/mark-all-read/', views.notification_mark_all_read, name='notification_mark_all_read'),
    
    #25-12-30 민혁 추가-----------------------------------------------------------------------
    # ▼▼▼ [반려동물 게시판URL] ▼▼▼
    path('pet/', views.pet_list, name='pet_list'),
    path('pet/write/', views.pet_write, name='pet_write'),
    path('pet/<int:pk>/', views.pet_detail, name='pet_detail'),
    path('pet/<int:pk>/edit/', views.pet_edit, name='pet_edit'),  
    path('pet/<int:pk>/delete/', views.pet_delete, name='pet_delete'), 
    
    #25-12-31 민혁 추가-----------------------------------------------------------------------
    # ▼▼▼ [반려동물 게시판댓글URL] ▼▼▼
    path('pet/<int:pk>/comment/create/',views.pet_comment_create,name='pet_comment_create'),
    path('pet/<int:pk>/comment/<int:comment_id>/delete/',views.pet_comment_delete,name='pet_comment_delete'),
    path('pet/<int:pk>/comment/<int:comment_id>/edit/', views.pet_comment_edit, name='pet_comment_edit'),
    
    #26-01-08 민혁 추가-----------------------------------------------------------------------
    # ▼▼▼ [반려동물 고민상담 게시판URL] ▼▼▼
    path("pet_counsel/",views.pet_counsel_list,name="pet_counsel_list"),
    path("pet_counsel/write/",views.pet_counsel_write,name="pet_counsel_write"),
    path("pet_counsel/<int:pk>/",views.pet_counsel_detail,name="pet_counsel_detail"), 
    path("pet/counsel/<int:pk>/edit/", views.pet_counsel_edit, name="pet_counsel_edit"),
    path("pet_counsel/<int:pk>/delete/",views.pet_counsel_delete,name="pet_counsel_delete"),
    path("pet_counsel/<int:pk>/comment/create/",views.pet_counsel_comment_create,name="pet_counsel_comment_create"),
    path('pet_counsel/<int:pk>/comment/<int:comment_id>/delete/',views.pet_counsel_comment_delete,name='pet_counsel_comment_delete'),
    path('pet_counsel/comment/<int:comment_id>/edit/',views.pet_counsel_comment_edit,name='pet_counsel_comment_edit'),
    
    #▼▼▼ [반려동물 건강 팁 게시판URL] ▼▼▼
    path("pet_health-tips/", views.pet_health_list, name="pet_health_list"),
    path("pet_health-tips/write/", views.pet_health_write, name="pet_health_write"),
    path("pet_health-tips/<int:pk>/", views.pet_health_detail, name="pet_health_detail"),
    path('pet_health-tips/<int:pk>/edit/', views.pet_health_edit, name='pet_health_edit'),
    path('pet_health-tips/<int:pk>/delete/', views.pet_health_delete, name='pet_health_delete'),
    path('pet_health/<int:pk>/comment/',views.pet_health_comment_create,name='pet_health_comment_create'),
    path('pet_health_comment/<int:comment_id>/edit/', views.pet_health_comment_edit, name='pet_health_comment_edit'),
    path('pet_health_comment/<int:comment_id>/delete/', views.pet_health_comment_delete, name='pet_health_comment_delete'),
]
