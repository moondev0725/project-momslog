from django.db import models
from django.contrib.auth.models import AbstractUser
from .constants import GRADE_CHOICES, GRADE_REQUIREMENTS, GRADE_ORDER


class User(AbstractUser):
    # 기본 정보
    real_name = models.CharField("이름", max_length=30)
    nickname = models.CharField("닉네임", max_length=30, unique=True)
    jumin = models.CharField("주민번호", max_length=20)  # 000000-0000000
    phone = models.CharField("휴대폰 번호", max_length=20)
    email = models.EmailField("이메일", max_length=254)
    address = models.CharField("주소", max_length=200, blank=True, null=True)
    address_detail = models.CharField("상세주소", max_length=200, blank=True, null=True)

    # ✅ 포인트(등급업 기준)
    point = models.PositiveIntegerField("포인트", default=0)

    # ✅ 회원 등급(5단계로 변경)
    grade = models.CharField("회원 등급", max_length=10, choices=GRADE_CHOICES, default="start")

    # 성별
    GENDER_CHOICES = [
        ('M', '남자'),
        ('F', '여자'),
    ]
    gender = models.CharField("성별", max_length=1, choices=GENDER_CHOICES, default='F')

    # 자녀 정보
    has_children = models.BooleanField("자녀 유무", default=False)
    CHILD_STAGE_CHOICES = [
        ("kindergarten", "유치원"),
        ("elementary", "초등학생"),
        ("middle", "중학생"),
        ("high", "고등학생"),
        ("adult", "성인"),
        ("other", "기타"),
    ]
    children_stages = models.JSONField("자녀 학령(복수)", default=list, blank=True)

    # 약관 동의 여부 (DB 저장용)
    terms_agreed = models.BooleanField("약관 동의", default=False)

    def recalc_grade(self, save=True):
        """
        point 기준으로 grade 자동 재계산
        """
        # 높은 등급부터 검사
        for code in reversed(GRADE_ORDER):
            if self.point >= GRADE_REQUIREMENTS[code]:
                self.grade = code
                break
        if save:
            self.save(update_fields=["grade"])

    def __str__(self):
        return f"[{self.get_grade_display()}] {self.real_name}"


class GeneralUser(User):
    class Meta:
        proxy = True
        verbose_name = '일반 회원'
        verbose_name_plural = '1. 일반 회원 관리'


class AdminUser(User):
    class Meta:
        proxy = True
        verbose_name = '관리자'
        verbose_name_plural = '2. 관리자(스태프) 관리'


class SignupBlock(models.Model):
    """탈퇴 후 재가입 제한 정보"""
    username = models.CharField(max_length=150)
    blocked_until = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["username", "blocked_until"])]

    def __str__(self):
        return f"{self.username} 블락 ~ {self.blocked_until}"
