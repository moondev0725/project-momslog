# ═══════════════════════════════════════════════════════════════════════
# recipes/admin.py
# 맘스로그 프로젝트 - 요리레시피 게시판 관리자 페이지
# ═══════════════════════════════════════════════════════════════════════
# 작성일: 2026-01-06
# ═══════════════════════════════════════════════════════════════════════

from django.contrib import admin
from .models import RecipePost, RecipeImage, RecipeComment


class RecipeImageInline(admin.TabularInline):
    """
    레시피 이미지 인라인 편집
    """
    model = RecipeImage
    extra = 1
    fields = ('image', 'order')


@admin.register(RecipePost)
class RecipePostAdmin(admin.ModelAdmin):
    """
    요리레시피 게시글 관리
    """
    list_display = ('id', 'title', 'category', 'author', 'views', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    readonly_fields = ('views', 'created_at', 'updated_at')
    inlines = [RecipeImageInline]
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('author', 'category', 'title', 'content')
        }),
        ('메타 정보', {
            'fields': ('views', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RecipeImage)
class RecipeImageAdmin(admin.ModelAdmin):
    """
    레시피 이미지 관리
    """
    list_display = ('id', 'post', 'order', 'image')
    list_filter = ('post',)
    ordering = ('post', 'order')


@admin.register(RecipeComment)
class RecipeCommentAdmin(admin.ModelAdmin):
    """
    레시피 댓글 관리
    """
    list_display = ('id', 'post', 'author', 'content_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username', 'post__title')
    readonly_fields = ('created_at', 'updated_at')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '댓글 내용'
