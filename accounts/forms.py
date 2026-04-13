# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import User
import re


class SignUpForm(UserCreationForm):
    HAS_CHILDREN_CHOICES = (
        ("0", "자녀 없음"),
        ("1", "자녀 있음"),
    )

    has_children = forms.ChoiceField(
        required=False,
        choices=HAS_CHILDREN_CHOICES,
        initial="0",
        widget=forms.HiddenInput()
    )

    children_stages = forms.MultipleChoiceField(
        required=False,
        choices=User.CHILD_STAGE_CHOICES,
        widget=forms.CheckboxSelectMultiple()
    )

    jumin = forms.CharField(required=True)
    email = forms.EmailField(required=True)

    # ✅ 상세주소 필드 추가 (회원가입 화면에서 name="address_detail"로 넘어오면 저장됨)
    address_detail = forms.CharField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'username',
            'real_name',
            'nickname',
            'jumin',
            'phone',
            'email',
            'address',
            'address_detail',   # ✅ 추가
            'gender',
            'has_children',
            'children_stages',
        )

    def clean_username(self):
        username = (self.cleaned_data.get('username') or '').strip()

        if not re.fullmatch(r"[A-Za-z0-9]+", username):
            raise ValidationError("아이디는 영문과 숫자만 입력 가능합니다.")

        if len(username) < 6 or len(username) > 20:
            raise ValidationError("아이디는 6~20자 사이로 입력해주세요.")

        if not re.search(r"[A-Za-z]", username) or not re.search(r"\d", username):
            raise ValidationError("아이디는 영문과 숫자를 모두 포함해야 합니다.")

        if User.objects.filter(username=username).exists():
            raise ValidationError("이미 사용 중인 아이디입니다.")

        return username

    def clean_nickname(self):
        nickname = (self.cleaned_data.get('nickname') or '').strip()

        if User.objects.filter(nickname=nickname).exists():
            raise ValidationError("이미 사용 중인 닉네임입니다.")

        return nickname

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip()

        if User.objects.filter(email=email).exists():
            raise ValidationError("이미 사용 중인 이메일입니다.")

        return email

    def clean_jumin(self):
        jumin = (self.cleaned_data.get('jumin') or '').strip()

        if not re.fullmatch(r"\d{6}-\d{7}", jumin):
            raise ValidationError("주민등록번호 형식이 올바르지 않습니다. (예: 000000-0000000)")

        return jumin

    def clean_phone(self):
        phone = (self.cleaned_data.get('phone') or '').strip()

        if not re.fullmatch(r"\d{3}-\d{3,4}-\d{4}", phone):
            raise ValidationError("휴대폰 번호 형식이 올바르지 않습니다. (예: 010-0000-0000)")

        return phone

    # ✅ hidden("0"/"1") -> bool 변환
    def clean_has_children(self):
        value = (self.cleaned_data.get('has_children') or "0").strip()
        return value == "1"

    def clean(self):
        cleaned = super().clean()
        has_children = cleaned.get("has_children", False)
        stages = cleaned.get("children_stages") or []

        # ✅ 자녀 있음이면 학령 1개 이상 필수
        if has_children and len(stages) == 0:
            self.add_error("children_stages", "자녀 학령을 최소 1개 선택해 주세요.")

        # ✅ 자녀 없음이면 stages 비움
        if not has_children:
            cleaned["children_stages"] = []

        # ✅ 주소/상세주소 공백 정리(선택)
        if "address" in cleaned:
            cleaned["address"] = (cleaned.get("address") or "").strip()
        if "address_detail" in cleaned:
            cleaned["address_detail"] = (cleaned.get("address_detail") or "").strip()

        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)

        user.has_children = self.cleaned_data.get("has_children", False)
        user.children_stages = self.cleaned_data.get("children_stages") or []

        # ✅ 주소 저장 분리
        user.address = (self.cleaned_data.get("address") or "").strip()
        user.address_detail = (self.cleaned_data.get("address_detail") or "").strip()

        if commit:
            user.save()
            self.save_m2m()
        return user
