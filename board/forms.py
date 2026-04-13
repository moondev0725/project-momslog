# ═══════════════════════════════════════════════════════════════════════
# board/forms.py
# 맘스로그 프로젝트 - 게시판 폼 정의
# ═══════════════════════════════════════════════════════════════════════
# 작성일: 2025-12-29
# 폼 클래스:
#   1. NoticeForm: 공지사항 작성 폼
#   2. FreePostForm: 자유게시판 작성 폼
#   3. FleaItemForm: 벼룩시장 작성 폼 (이미지 업로드 포함)
#   4. FleaCommentForm: 벼룩시장 댓글 폼 (25-12-29 추가 - 비밀글 비밀번호 검증)
# ═══════════════════════════════════════════════════════════════════════

from django import forms
from .models import Notice, FreePost, FleaItem, FleaComment, FleaReport

class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'style': 'width:100%; padding:10px; border:1px solid #ddd; border-radius:5px;'}),
            'content': forms.Textarea(attrs={'style': 'width:100%; height:300px; padding:10px; border:1px solid #ddd; border-radius:5px;'}),
        }

class FreePostForm(forms.ModelForm):
    class Meta:
        model = FreePost
        fields = ['category', 'title', 'content', 'region', 'district', 'dong']  # 지역 필드 추가
        labels = {
            'category': '카테고리',
            'title': '제목',
            'content': '내용',
            'region': '지역 (시/도)',
            'district': '구/군 (선택)',
            'dong': '동/읍/면 (선택)',
        }
        widgets = {
            'category': forms.Select(attrs={'style': 'width:100%; padding:10px; border:1px solid #ddd; border-radius:5px;'}),
            'title': forms.TextInput(attrs={'style': 'width:100%; padding:10px; border:1px solid #ddd; border-radius:5px;'}),
            'content': forms.Textarea(attrs={'style': 'width:100%; height:300px; padding:10px; border:1px solid #ddd; border-radius:5px;'}),
            'region': forms.Select(attrs={'style': 'width:100%; padding:10px; border:1px solid #ddd; border-radius:5px;'}),
            'district': forms.TextInput(attrs={'style': 'width:100%; padding:8px; border:1px solid #ddd; border-radius:5px;', 'placeholder': '예: 강남구'}),
            'dong': forms.TextInput(attrs={'style': 'width:100%; padding:8px; border:1px solid #ddd; border-radius:5px;', 'placeholder': '예: 역삼동'}),
        }


class FleaItemForm(forms.ModelForm):
    class Meta:
        model = FleaItem
        fields = ['title', 'description', 'price', 'image', 'location_address', 'latitude', 'longitude']
        labels = {
            'title': '제목',
            'description': '내용',
            'price': '가격',
            'image': '이미지',
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': '제목을 입력하세요'}),
            'description': forms.Textarea(attrs={'placeholder': '상품 설명을 입력하세요', 'rows': 6, 'style': 'resize:vertical;'}),
            'price': forms.NumberInput(attrs={'placeholder': '가격을 입력하세요 (원)', 'min': '0'}),
            'location_address': forms.HiddenInput(),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }


class FleaCommentForm(forms.ModelForm):
    class Meta:
        model = FleaComment
        fields = ['title', 'content', 'is_secret', 'password']
        labels = {
            'title': '제목',
            'content': '내용',
            'is_secret': '비밀글로 작성',
            'password': '비밀글 비밀번호',
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': '댓글 제목을 입력하세요'}),
            'content': forms.Textarea(attrs={'placeholder': '댓글 내용을 입력하세요', 'rows': 4, 'style': 'resize:vertical;'}),
            'password': forms.PasswordInput(attrs={'placeholder': '비밀글 비밀번호를 입력하세요'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        is_secret = cleaned_data.get('is_secret')
        password = cleaned_data.get('password')

        if is_secret and not password:
            self.add_error('password', '비밀글 비밀번호를 입력하세요.')
        if not is_secret:
            cleaned_data['password'] = ''
        return cleaned_data


class FleaReportForm(forms.ModelForm):
    class Meta:
        model = FleaReport
        fields = ['reason', 'details']
        labels = {
            'reason': '신고 사유',
            'details': '추가 설명',
        }
        widgets = {
            'reason': forms.Select(attrs={'style': 'width:100%; padding:10px; border:1px solid #ddd; border-radius:5px;'}),
            'details': forms.Textarea(attrs={'placeholder': '필요 시 상세 내용을 입력하세요', 'rows': 4, 'style': 'resize:vertical;'}),
        }
    