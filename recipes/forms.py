# ═══════════════════════════════════════════════════════════════════════
# recipes/forms.py
# 맘스로그 프로젝트 - 요리레시피 게시판 폼
# ═══════════════════════════════════════════════════════════════════════
# 작성일: 2026-01-06
# ═══════════════════════════════════════════════════════════════════════

from django import forms
from .models import RecipePost, RecipeComment


class RecipePostForm(forms.ModelForm):
    """
    요리레시피 게시글 작성 폼
    """
    class Meta:
        model = RecipePost
        fields = ['category', 'title', 'content']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-control',
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '레시피 제목을 입력하세요',
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 15,
                'placeholder': '레시피 내용을 입력하세요\n\n예시:\n재료:\n- 재료1\n- 재료2\n\n조리법:\n1. 단계1\n2. 단계2',
            }),
        }
        labels = {
            'category': '카테고리',
            'title': '제목',
            'content': '내용',
        }


class RecipeCommentForm(forms.ModelForm):
    """
    요리레시피 댓글 작성 폼
    """
    class Meta:
        model = RecipeComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '댓글을 입력하세요',
            }),
        }
        labels = {
            'content': '',
        }
