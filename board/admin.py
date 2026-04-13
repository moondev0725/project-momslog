# -*- coding: utf-8 -*-
# ══════════════════════════════════════════════════════════════════════
# board/admin.py
# 맘스로그 프로젝트 - Django Admin 커스터마이징
# ══════════════════════════════════════════════════════════════════════
# 작성일: 2025-12-29
# Admin 클래스:
#   1. NoticeAdmin: 공지사항 관리
#   2. FreePostAdmin: 자유게시판 관리
#   3. FleaItemAdmin: 벼룩시장 관리 (25-12-29 수정 - 찜 개수, 거래 상태 표시)
#   4. FleaCommentAdmin: 벼룩시장 댓글 관리 (25-12-29 추가 - 초 단위 시간 표시)
#   5. NotificationAdmin: 알림 관리 (25-12-29 추가)
# ══════════════════════════════════════════════════════════════════════

from django.contrib import admin
from .models import Notice, FreePost, FleaItem, FleaComment, FleaReport, Notification, HotDeal, ParentingInfo, PetPost, PetComment, PetImage, MomDiary, DiaryEntry  # 26-01-06 추가: PetImage

class NoticeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at', 'view_count')
    search_fields = ('title',)

admin.site.register(Notice, NoticeAdmin)

# FreePost Admin 등록
@admin.register(FreePost)
class FreePostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'popularity_score', 'views', 'comment_count', 'is_pinned', 'created_at')
    list_filter = ('is_pinned', 'region', 'created_at', 'author')
    search_fields = ('title', 'content', 'author__username')
    readonly_fields = ('created_at', 'views', 'popularity_score')
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'content', 'author', 'category')
        }),
        ('지역 정보', {
            'fields': ('region', 'district', 'dong', 'latitude', 'longitude')
        }),
        ('상호작용', {
            'fields': ('views', 'comment_count', 'bookmark_count', 'reaction_empathy', 'reaction_courage', 'reaction_cheer', 'reaction_support', 'reaction_thanks')
        }),
        ('운영진 옵션', {
            'fields': ('is_pinned', 'pinned_at', 'popularity_score'),
            'classes': ('collapse',)
        }),
        ('시스템', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

# HotDeal Admin 등록
# 26-01-02 슬기 추가: 핫딜공유 관리자 페이지
# 26-01-05 슬기 수정: 지역, 인기도, 운영진 고정 필드 추가
@admin.register(HotDeal)
class HotDealAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'price', 'popularity_score', 'views', 'is_pinned', 'created_at')
    list_filter = ('is_pinned', 'category', 'region', 'created_at', 'author')
    search_fields = ('title', 'content', 'author__username')
    readonly_fields = ('created_at', 'views', 'popularity_score')
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'content', 'category', 'price', 'link', 'author')
        }),
        ('지역 정보', {
            'fields': ('region', 'district', 'dong', 'latitude', 'longitude')
        }),
        ('상호작용', {
            'fields': ('views', 'comment_count', 'bookmark_count')
        }),
        ('운영진 옵션', {
            'fields': ('is_pinned', 'pinned_at', 'popularity_score'),
            'classes': ('collapse',)
        }),
        ('시스템', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


# 26-01-02 슬기 추가: 육아정보 관리자 페이지
# 26-01-05 슬기 수정: 지역, 인기도, 운영진 고정 필드 추가
@admin.register(ParentingInfo)
class ParentingInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'popularity_score', 'views', 'is_pinned', 'created_at')
    list_filter = ('is_pinned', 'category', 'region', 'created_at', 'author')
    search_fields = ('title', 'content', 'author__username')
    readonly_fields = ('created_at', 'views', 'popularity_score')
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'content', 'category', 'author')
        }),
        ('발달 지표', {
            'fields': ('month_age', 'physical_score', 'cognitive_score', 'language_score', 'social_score', 'height', 'weight'),
            'classes': ('collapse',)
        }),
        ('지역 정보', {
            'fields': ('region', 'district', 'dong', 'latitude', 'longitude')
        }),
        ('상호작용', {
            'fields': ('views', 'comment_count', 'bookmark_count')
        }),
        ('운영진 옵션', {
            'fields': ('is_pinned', 'pinned_at', 'popularity_score'),
            'classes': ('collapse',)
        }),
        ('시스템', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

# 25-12-29 슬기 수정: 찜하기 기능, 찜 수 표시, 거래 상태 추가
@admin.register(FleaItem)
class FleaItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price_display', 'status', 'like_count', 'author', 'created_at')
    list_display_links = ('title',)
    list_filter = ('created_at', 'author', 'status')
    search_fields = ('title', 'description', 'author__username')
    readonly_fields = ('created_at', 'updated_at', 'author')
    
    fieldsets = (
        ('상품 정보', {
            'fields': ('title', 'price', 'description', 'image', 'status')
        }),
        ('기타 정보', {
            'fields': ('author', 'liked_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # 신규 작성 시 author 자동 설정
            obj.author = request.user
        super().save_model(request, obj, form, change)
    
    def price_display(self, obj):
        return f"{obj.price:,.0f}원"
    price_display.short_description = '가격'

    def like_count(self, obj):
        return obj.liked_by.count()
    like_count.short_description = '찜 수'


# 25-12-29 슬기 수정: 댓글 관리 (비밀글, 작성자, 작성일시 초단위 표시)
@admin.register(FleaComment)
class FleaCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'nickname', 'flea_item', 'is_secret', 'author', 'created_at_display')
    list_filter = ('is_secret', 'created_at')
    search_fields = ('title', 'content', 'nickname', 'author__username', 'flea_item__title')
    readonly_fields = ('created_at', 'updated_at', 'author', 'flea_item')
    
    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
    created_at_display.short_description = '작성일시'


@admin.register(FleaReport)
class FleaReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'flea_item', 'reporter', 'reason', 'status', 'created_at')
    list_filter = ('status', 'reason', 'created_at')
    search_fields = ('flea_item__title', 'reporter__username', 'details')
    readonly_fields = ('flea_item', 'reporter', 'created_at', 'updated_at')
    

# 25-12-29 슬기 수정: 알림 관리
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('message', 'user__username')
    readonly_fields = ('created_at', 'user', 'free_post', 'pet_post', 'flea_item')


# 25-12-30 민혁 추가: 반려동물 게시판 관리
class PetImageInline(admin.TabularInline):
    model = PetImage
    extra = 1
    fields = ('image', 'order')
    ordering = ['order']


class PetPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'views', 'created_at')
    list_display_links = ('title',)
    list_filter = ('created_at', 'author')
    search_fields = ('title', 'content', 'author__username', 'author__nickname')
    readonly_fields = ('created_at', 'updated_at', 'views')
    inlines = [PetImageInline]
    
    fieldsets = (
        ('게시글 정보', {
            'fields': ('title', 'content', 'author')
        }),
        ('통계 및 기타', {
            'fields': ('views', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


admin.site.register(PetPost, PetPostAdmin)


# 25-12-31 민혁 추가: 반려동물 댓글 관리
@admin.register(PetComment)
class PetCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'author', 'content_preview', 'parent', 'created_at')
    list_display_links = ('content_preview',)
    list_filter = ('created_at', 'author')
    search_fields = ('content', 'author__username', 'author__nickname', 'post__title')
    readonly_fields = ('created_at', 'updated_at', 'post', 'author', 'parent')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '댓글 내용'


# 26-01-08 민혁 추가: 반려동물 건강 팁 및 고민상담 관리자 페이지
from .models import PetHealthPost, PetCounselPost

@admin.register(PetHealthPost)
class PetHealthPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'views', 'created_at')
    search_fields = ('title', 'content')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'views')

@admin.register(PetCounselPost)
class PetCounselPostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "views", "created_at")
    list_filter = ("created_at",)
    search_fields = ("title", "content")
    ordering = ("-created_at",)
    readonly_fields = ('created_at', 'updated_at', 'views')
