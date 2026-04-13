# ═══════════════════════════════════════════════════════════════════════
# recipes/models.py
# 맘스로그 프로젝트 - 요리레시피 게시판 모델
# ═══════════════════════════════════════════════════════════════════════
# 작성일: 2026-01-06
# 최종수정일: 2026-01-09
# 모델:
#   1. RecipePost: 레시피 게시글 (제목, 내용, 카테고리, 작성자)
#   2. RecipeImage: 레시피 이미지 (최대 10개)
#   3. RecipeComment: 레시피 댓글
# ═══════════════════════════════════════════════════════════════════════

from django.db import models
from django.conf import settings


class RecipePost(models.Model):
    """
    요리레시피 게시글 모델
    """
    CATEGORY_CHOICES = [
        ('korean', '한식'),
        ('chinese', '중식'),
        ('japanese', '일식'),
        ('western', '양식'),
        ('snack', '간식/디저트'),
        ('baby', '아기 이유식'),
        ('diet', '다이어트'),
        ('simple', '간단요리'),
    ]

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="작성자")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='korean', verbose_name="카테고리")
    title = models.CharField(max_length=200, verbose_name="제목")
    content = models.TextField(verbose_name="내용")

    # 메타 정보
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")
    views = models.IntegerField(default=0, verbose_name="조회수")

    class Meta:
        verbose_name = '요리레시피'
        verbose_name_plural = '요리레시피'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_category_display_name(self):
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category)


class RecipeImage(models.Model):
    """
    요리레시피 이미지 모델 (최대 10개)
    """
    post = models.ForeignKey(RecipePost, on_delete=models.CASCADE, related_name='images', verbose_name="게시글")
    image = models.ImageField(upload_to='recipes/%Y/%m/%d/', verbose_name="이미지")
    order = models.PositiveIntegerField(default=0, verbose_name="순서")

    class Meta:
        verbose_name = '레시피 이미지'
        verbose_name_plural = '레시피 이미지'
        ordering = ['order']

    def __str__(self):
        return f"{self.post.title} - 이미지 {self.order}"


class RecipeComment(models.Model):
    """
    요리레시피 댓글 모델
    """
    post = models.ForeignKey(RecipePost, on_delete=models.CASCADE, related_name='comments', verbose_name="게시글")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="작성자")
    content = models.TextField(verbose_name="댓글 내용")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    class Meta:
        verbose_name = '레시피 댓글'
        verbose_name_plural = '레시피 댓글'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.post.title} - {self.author.username}의 댓글"
