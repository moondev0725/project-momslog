# ═══════════════════════════════════════════════════════════════════════
# recipes/urls.py
# 맘스로그 프로젝트 - 요리레시피 게시판 URL
# ═══════════════════════════════════════════════════════════════════════
# 작성일: 2026-01-06
# ═══════════════════════════════════════════════════════════════════════

from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    # 목록 및 상세
    path('', views.recipe_list, name='recipe_list'),
    path('<int:pk>/', views.recipe_detail, name='recipe_detail'),

    # 글 작성, 수정, 삭제
    path('create/', views.recipe_create, name='recipe_create'),
    path('<int:pk>/update/', views.recipe_update, name='recipe_update'),
    path('<int:pk>/delete/', views.recipe_delete, name='recipe_delete'),

    # 댓글
    path('<int:pk>/comment/create/', views.comment_create, name='comment_create'),
    path('<int:pk>/comment/<int:comment_id>/delete/', views.comment_delete, name='comment_delete'),
    path('<int:pk>/comment/<int:comment_id>/update/', views.comment_update, name='comment_update'),

    # 대댓글
    path('<int:pk>/comment/<int:comment_id>/reply/', views.reply_create, name='reply_create'),
    path('<int:pk>/comment/<int:comment_id>/reply/<int:reply_id>/delete/', views.reply_delete, name='reply_delete'),
    path('<int:pk>/comment/<int:comment_id>/reply/<int:reply_id>/update/', views.reply_update, name='reply_update'),
]
