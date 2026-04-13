# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, GeneralUser, AdminUser
from .constants import GRADE_REQUIREMENTS


# ✅ 자녀 학령 표시(관리자 목록에서 보기 좋게)
def children_stages_display(obj):
    label_map = {
        "kindergarten": "유치원",
        "elementary": "초등학생",
        "middle": "중학생",
        "high": "고등학생",
        "adult": "성인",
        "other": "기타",
    }
    return ", ".join(label_map.get(x, x) for x in (obj.children_stages or []))

children_stages_display.short_description = "자녀 학령"


# --- 프록시 모델용 폼 정의 (필수) ---
class GeneralUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = GeneralUser


class GeneralUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = GeneralUser


class AdminUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = AdminUser
        fields = ("username", "nickname")

    def clean_nickname(self):
        nick = self.cleaned_data.get("nickname") or self.cleaned_data.get("username")
        if User.objects.filter(nickname=nick).exists():
            raise forms.ValidationError("이미 사용 중인 닉네임입니다.")
        return nick

    def save(self, commit=True):
        user = super().save(commit=False)
        if not getattr(user, "nickname", None):
            user.nickname = user.username
        user.is_staff = True
        if commit:
            user.save()
        return user


class AdminUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = AdminUser
# -------------------------------------


# =========================
# 1. 일반 회원 관리
# =========================
class GeneralUserAdmin(UserAdmin):
    form = GeneralUserChangeForm
    add_form = GeneralUserCreationForm

    # ✅ child_school 제거 + children_stages_display 추가
    list_display = (
        'username',
        'real_name',
        'grade',
        'gender',
        'has_children',
        children_stages_display,
        'date_joined',
    )
    list_filter = ('grade', 'gender', 'has_children')
    search_fields = ('username', 'real_name', 'nickname', 'phone')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_staff=False)

    # ✅ 수정 화면 필드 (child_school 제거)
    fieldsets = (
        ('계정 정보', {'fields': ('username', 'password', 'grade')}),
        ('개인 정보', {'fields': ('real_name', 'nickname', 'jumin', 'phone', 'email', 'address')}),
        ('자녀 정보', {'fields': ('has_children', 'children_stages')}),
        ('상세 정보', {'fields': ('gender', 'terms_agreed')}),
        ('권한', {'fields': ('is_active',)}),
    )

    # ✅ 추가 화면 필드
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        ('필수 개인 정보', {
            'classes': ('wide',),
            'fields': ('real_name', 'nickname', 'jumin', 'phone', 'email', 'address'),
        }),
        ('회원 등급 및 상세', {
            'classes': ('wide',),
            'fields': ('grade', 'gender', 'has_children', 'children_stages', 'terms_agreed'),
        }),
    )

    # ✅ 핵심: 관리자에서 grade를 변경하면 point도 그 등급 시작점으로 맞춤
    def save_model(self, request, obj, form, change):
        if change and "grade" in form.changed_data:
            obj.point = GRADE_REQUIREMENTS.get(obj.grade, obj.point or 0)
        super().save_model(request, obj, form, change)


# =========================
# 2. 관리자 관리
# =========================
class AdminUserAdmin(UserAdmin):
    form = AdminUserChangeForm
    add_form = AdminUserCreationForm
    list_display = ('username', 'real_name', 'is_superuser')

    fieldsets = (
        ('계정 정보', {'fields': ('username', 'password')}),
        ('개인 정보', {'fields': ('real_name', 'nickname', 'email')}),
        ('권한', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'nickname', 'password1', 'password2'),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_staff=True)


admin.site.register(GeneralUser, GeneralUserAdmin)
admin.site.register(AdminUser, AdminUserAdmin)
