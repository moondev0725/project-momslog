# ═══════════════════════════════════════════════════════════════════════
# board/models.py
# 맘스로그 프로젝트 - 게시판 데이터 모델
# ═══════════════════════════════════════════════════════════════════════
# 작성일: 2025-12-29
# 모델:
#   1. Notice: 공지사항 (제목, 내용, 조회수)
#   2. FreePost: 자유게시판 (제목, 내용, 작성자, 조회수)
#   3. FleaItem: 벼룩시장 (제목, 설명, 가격, 이미지, 작성자, 찜 기능)
#   4. FleaComment: 벼룩시장 댓글 (25-12-29 추가 - 닉네임, 제목, 비밀글, 비밀번호)
# ═══════════════════════════════════════════════════════════════════════

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Notice(models.Model):
    title = models.CharField("제목", max_length=100)
    content = models.TextField("내용")
    created_at = models.DateTimeField("작성일", auto_now_add=True)
    view_count = models.IntegerField("조회수", default=0)

    class Meta:
        verbose_name = '공지사항'
        verbose_name_plural = '공지사항'

    def __str__(self):
        return self.title
    
    # 자유게시판
# 26-01-02 혜은 수정: 카테고리 기능 추가
# 26-01-05 슬기 추가: 지역, 좌표, 인기도 필드
class FreePost(models.Model):
    CATEGORY_CHOICES = [
        ('all', '전체보기'),
        ('mom', '육아수다'),
        ('husband', '남편뒷담화'),
        ('family', '시댁/친정'),
        ('preg', '임신출산'),
    ]
    
    REGION_CHOICES = [
        ('seoul', '서울시'),
        ('gyeonggi', '경기도'),
        ('incheon', '인천시'),
        ('daejeon', '대전시'),
        ('daegu', '대구시'),
        ('busan', '부산시'),
        ('gwangju', '광주시'),
        ('ulsan', '울산시'),
        ('sejong', '세종시'),
        ('other', '기타'),
    ]
    
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='mom',
        verbose_name='카테고리'
    )
    title = models.CharField(max_length=200, verbose_name="제목")
    content = models.TextField(verbose_name="내용")
    
    # ▼▼▼ 여기 수정 (User -> settings.AUTH_USER_MODEL) ▼▼▼
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="작성자")
    # 익명 여부 (엄마 이야기 게시판 익명 표시용)
    is_anonymous = models.BooleanField(default=False, verbose_name="익명 여부")
    
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")
    views = models.IntegerField(default=0, verbose_name="조회수")
    
    # 감정 리액션 카운트 (26-01-02 추가)
    reaction_empathy = models.IntegerField(default=0, verbose_name="공감해요")      # 🤝
    reaction_courage = models.IntegerField(default=0, verbose_name="힘내세요")     # 💪
    reaction_cheer = models.IntegerField(default=0, verbose_name="축하해요")       # 🎉
    reaction_support = models.IntegerField(default=0, verbose_name="응원해요")     # 👏
    reaction_thanks = models.IntegerField(default=0, verbose_name="고마워요")      # 🙏
    
    # 26-01-05 추가: 지역, 좌표, 댓글수, 저장수, 인기도 관련 필드
    region = models.CharField(max_length=20, choices=REGION_CHOICES, null=True, blank=True, verbose_name="지역")
    district = models.CharField(max_length=50, null=True, blank=True, verbose_name="구/군")
    dong = models.CharField(max_length=50, null=True, blank=True, verbose_name="동/읍/면")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="위도")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="경도")
    
    comment_count = models.IntegerField(default=0, verbose_name="댓글수")
    bookmark_count = models.IntegerField(default=0, verbose_name="저장수")
    popularity_score = models.FloatField(default=0, verbose_name="인기도 점수")
    
    
    # 운영진 고정 여부
    is_pinned = models.BooleanField(default=False, verbose_name="운영진 고정")
    pinned_at = models.DateTimeField(null=True, blank=True, verbose_name="고정 시간")

    class Meta:
        verbose_name = '자유게시판'
        verbose_name_plural = '자유게시판'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-is_pinned', '-popularity_score', '-created_at']),
            models.Index(fields=['region', '-popularity_score']),
        ]

    def __str__(self):
        return self.title


# 26-01-02 혜은 추가: 자유게시판 댓글 모델
class FreeComment(models.Model):
    post = models.ForeignKey(FreePost, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "자유게시판 댓글"
        verbose_name_plural = "자유게시판 댓글"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.post_id} - {self.author} - {self.content[:10]}"
    
# 26-01-06 혜은 추가 : 첨부파일 모델
from django.db import models

class FreePostAttachment(models.Model):
    post = models.ForeignKey(
        FreePost,
        on_delete=models.CASCADE,
        related_name="attachments"
    )
    file = models.FileField(upload_to="free_attachments/%Y/%m/%d/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.post_id} - {self.file.name}"
    
    




# 핫딜공유 게시판
# 26-01-02 슬기 추가: 핫딜공유 게시판 모델
# 26-01-05 슬기 추가: 지역, 좌표, 인기도 필드
class HotDeal(models.Model):
    CATEGORY_CHOICES = [
        ('all', '전체보기'),
        ('baby', '육아용품 핫딜'),
        ('life', '생활용품 핫딜'),
        ('event', '이벤트/체험단'),
    ]
    
    REGION_CHOICES = [
        ('seoul', '서울시'),
        ('gyeonggi', '경기도'),
        ('incheon', '인천시'),
        ('daejeon', '대전시'),
        ('daegu', '대구시'),
        ('busan', '부산시'),
        ('gwangju', '광주시'),
        ('ulsan', '울산시'),
        ('sejong', '세종시'),
        ('other', '기타'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="제목")
    content = models.TextField(verbose_name="내용")
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='all', verbose_name="카테고리")
    link = models.URLField(blank=True, null=True, verbose_name="상품 링크")
    price = models.CharField(max_length=50, blank=True, null=True, verbose_name="가격")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="작성자")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")
    views = models.IntegerField(default=0, verbose_name="조회수")
    
    # 26-01-05 추가: 지역, 좌표, 댓글수, 저장수, 인기도 관련 필드
    region = models.CharField(max_length=20, choices=REGION_CHOICES, null=True, blank=True, verbose_name="지역")
    district = models.CharField(max_length=50, null=True, blank=True, verbose_name="구/군")
    dong = models.CharField(max_length=50, null=True, blank=True, verbose_name="동/읍/면")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="위도")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="경도")
    
    comment_count = models.IntegerField(default=0, verbose_name="댓글수")
    bookmark_count = models.IntegerField(default=0, verbose_name="저장수")
    popularity_score = models.FloatField(default=0, verbose_name="인기도 점수")
    
    # 운영진 고정 여부
    is_pinned = models.BooleanField(default=False, verbose_name="운영진 고정")
    pinned_at = models.DateTimeField(null=True, blank=True, verbose_name="고정 시간")

    class Meta:
        verbose_name = '핫딜공유'
        verbose_name_plural = '핫딜공유'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-is_pinned', '-popularity_score', '-created_at']),
            models.Index(fields=['region', '-popularity_score']),
        ]

    def __str__(self):
        return self.title


# 26-01-02 슬기 추가: 육아정보 게시판 모델
# 26-01-05 슬기 추가: 지역, 좌표, 인기도 필드
class ParentingInfo(models.Model):
    CATEGORY_CHOICES = [
        ('all', '전체보기'),
        ('development', '월령별 발달'),
        ('sleep', '수면교육'),
        ('discipline', '훈육 노하우'),
    ]
    
    REGION_CHOICES = [
        ('seoul', '서울시'),
        ('gyeonggi', '경기도'),
        ('incheon', '인천시'),
        ('daejeon', '대전시'),
        ('daegu', '대구시'),
        ('busan', '부산시'),
        ('gwangju', '광주시'),
        ('ulsan', '울산시'),
        ('sejong', '세종시'),
        ('other', '기타'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="제목")
    content = models.TextField(verbose_name="내용")
    category = models.CharField(max_length=15, choices=CATEGORY_CHOICES, default='all', verbose_name="카테고리")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="작성자")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")
    views = models.IntegerField(default=0, verbose_name="조회수")
    
    # 26-01-02 슬기 추가: 월령별 발달 차트용 필드
    month_age = models.IntegerField(null=True, blank=True, verbose_name="월령(개월)")
    physical_score = models.IntegerField(null=True, blank=True, verbose_name="신체발달(0-100)")
    cognitive_score = models.IntegerField(null=True, blank=True, verbose_name="인지발달(0-100)")
    language_score = models.IntegerField(null=True, blank=True, verbose_name="언어발달(0-100)")
    social_score = models.IntegerField(null=True, blank=True, verbose_name="사회성발달(0-100)")
    # 26-01-04 추가: 키와 몸무게
    height = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, verbose_name="키(cm)")
    weight = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, verbose_name="몸무게(kg)")
    
    # 26-01-05 추가: 지역, 좌표, 댓글수, 저장수, 인기도 관련 필드
    region = models.CharField(max_length=20, choices=REGION_CHOICES, null=True, blank=True, verbose_name="지역")
    district = models.CharField(max_length=50, null=True, blank=True, verbose_name="구/군")
    dong = models.CharField(max_length=50, null=True, blank=True, verbose_name="동/읍/면")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="위도")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="경도")
    
    comment_count = models.IntegerField(default=0, verbose_name="댓글수")
    bookmark_count = models.IntegerField(default=0, verbose_name="저장수")
    popularity_score = models.FloatField(default=0, verbose_name="인기도 점수")
    
    # 운영진 고정 여부
    is_pinned = models.BooleanField(default=False, verbose_name="운영진 고정")
    pinned_at = models.DateTimeField(null=True, blank=True, verbose_name="고정 시간")

    class Meta:
        verbose_name = '육아정보'
        verbose_name_plural = '육아정보'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-is_pinned', '-popularity_score', '-created_at']),
            models.Index(fields=['region', '-popularity_score']),
        ]

    def __str__(self):
        return self.title


class ParentingComment(models.Model):
    post = models.ForeignKey(
        ParentingInfo,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='게시글'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='작성자'
    )
    content = models.TextField(verbose_name='댓글 내용')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    # 26-01-08 이미지 업로드 추가 (최대 10장)
    images = models.JSONField(default=list, blank=True, verbose_name='첨부 이미지')

    class Meta:
        verbose_name = '육아정보 댓글'
        verbose_name_plural = '육아정보 댓글'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.author} - {self.content[:20]}"


class ParentingImage(models.Model):
    """육아정보 게시글의 이미지 (최대 10개)"""
    post = models.ForeignKey(
        ParentingInfo,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='게시글'
    )
    image = models.ImageField(
        upload_to='parenting/',
        verbose_name='이미지'
    )
    order = models.PositiveIntegerField(default=0, verbose_name='순서')

    class Meta:
        verbose_name = '육아정보 이미지'
        verbose_name_plural = '육아정보 이미지'
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.post.title} - 이미지 {self.order + 1}"


class FleaItem(models.Model):
    # 25-12-29 슬기 수정: 거래 상태 필드 추가
    STATUS_CHOICES = [
        ('selling', '판매중'),
        ('reserved', '예약중'),
        ('sold', '판매완료'),
        ('share', '나눔'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="제목")
    description = models.TextField(verbose_name="내용")
    price = models.IntegerField(verbose_name="가격(원)")
    # ✅ 동네마켓(지도 연동) - 위치 정보 (선택)
    location_address = models.CharField(max_length=255, null=True, blank=True, verbose_name="거래 희망 위치(주소)")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="위도")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="경도")

    image = models.ImageField(upload_to='flea/', null=True, blank=True, verbose_name="이미지")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="작성자")
    liked_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_flea_items', blank=True, verbose_name="찜한 사용자")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='selling', verbose_name="거래 상태")
    views = models.IntegerField(default=0, verbose_name="조회수")  # 26-01-02 슬기 추가: 조회수 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        verbose_name = '벼룩시장'
        verbose_name_plural = '벼룩시장'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


# 25-12-29 슬기 수정: 벼룩시장 댓글 모델 추가 (닉네임, 제목, 내용, 비밀글, 비밀번호)
class FleaComment(models.Model):
    flea_item = models.ForeignKey(FleaItem, on_delete=models.CASCADE, related_name='comments', verbose_name='상품')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='작성자')
    nickname = models.CharField(max_length=50, verbose_name='닉네임')
    title = models.CharField(max_length=200, verbose_name='제목')
    content = models.TextField(verbose_name='내용')
    is_secret = models.BooleanField(default=False, verbose_name='비밀글')
    password = models.CharField(max_length=128, blank=True, verbose_name='비밀글 비밀번호')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        verbose_name = '벼룩시장 댓글'
        verbose_name_plural = '벼룩시장 댓글'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class FleaReport(models.Model):
    REASON_CHOICES = [
        ('spam', '광고/스팸'),
        ('fraud', '사기 의심'),
        ('abuse', '욕설/비방'),
        ('wrong', '잘못된 정보/분류'),
        ('other', '기타'),
    ]

    STATUS_CHOICES = [
        ('pending', '접수'),
        ('in_progress', '확인중'),
        ('resolved', '처리완료'),
    ]

    flea_item = models.ForeignKey(FleaItem, on_delete=models.CASCADE, related_name='reports', verbose_name='신고 대상')
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='flea_reports', verbose_name='신고자')
    reason = models.CharField(max_length=30, choices=REASON_CHOICES, verbose_name='신고 사유')
    details = models.TextField(blank=True, verbose_name='상세 내용')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='처리 상태')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='신고 일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정 일시')
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name='처리 일시')

    class Meta:
        verbose_name = '벼룩시장 신고'
        verbose_name_plural = '벼룩시장 신고'

    def __str__(self):
        return f"{self.flea_item.title} - {self.get_reason_display()}"


# 25-12-30 민혁 추가 : 반려동물 게시판 모델
class PetPost(models.Model):
    title = models.CharField(max_length=200, verbose_name="제목")
    content = models.TextField(verbose_name="내용")

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="작성자"
    )

    views = models.IntegerField(default=0, verbose_name="조회수")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        verbose_name = '반려동물 게시판'
        verbose_name_plural = '반려동물 게시판'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class PetImage(models.Model):
    """반려동물 게시글의 이미지 (최대 10개)"""
    post = models.ForeignKey(
        PetPost,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="게시글"
    )
    image = models.ImageField(
        upload_to='pet/',
        verbose_name="이미지"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="순서"
    )

    class Meta:
        verbose_name = '반려동물 이미지'
        verbose_name_plural = '반려동물 이미지'
        ordering = ['order']

    def __str__(self):
        return f"{self.post.title} - 이미지 {self.order + 1}"

    
  # 25-12-31 민혁 추가 : 반려동물 게시판 댓글 모델 (대댓글 지원)
class PetComment(models.Model):
    post = models.ForeignKey(
        PetPost,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='게시글'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='작성자'
    )
    content = models.TextField(verbose_name='내용')

    # ⭐️ 대댓글용 부모 댓글 (이 줄이 추가됨)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies',
        verbose_name='부모 댓글'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        verbose_name = '반려동물 댓글'
        verbose_name_plural = '반려동물 댓글'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.author} - {self.content[:20]}"

    # (선택) 부모 댓글 여부 확인용
    def is_reply(self):
        return self.parent is not None


# ═══════════════════════════════════════════════════════════════════════
# 🐾 반려동물 건강 팁 게시판 (26-01-08 민혁 추가)
# ═══════════════════════════════════════════════════════════════════════
class PetHealthPost(models.Model):
    title = models.CharField(max_length=200, verbose_name="제목")
    content = models.TextField(verbose_name="내용")

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="작성자"
    )

    views = models.IntegerField(default=0, verbose_name="조회수")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")

    class Meta:
        verbose_name = "반려동물 건강 팁"
        verbose_name_plural = "반려동물 건강 팁"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
    
# ═══════════════════════════════════════════════════════════════════════
# 🐾 반려동물 고민상담 게시판 (26-01-10 민혁 추가)
# ═══════════════════════════════════════════════════════════════════════
class PetCounselPost(models.Model):
    title = models.CharField(max_length=200, verbose_name="제목")
    content = models.TextField(verbose_name="내용")

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="작성자"
    )

    views = models.PositiveIntegerField(default=0, verbose_name="조회수")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        verbose_name = "반려동물 고민상담"
        verbose_name_plural = "반려동물 고민상담"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
    
# 26-01-09 민혁 추가: 반려동물 건강 팁 이미지 모델
class PetHealthImage(models.Model):
    post = models.ForeignKey(
        PetHealthPost,
        related_name='images',
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to='pet_health/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

# 26-01-10 민혁 추가: 반려동물 건강 팁 댓글 모델
class PetHealthComment(models.Model):
    post = models.ForeignKey(
        PetHealthPost,
        related_name='comments',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.post.title} 댓글'
    
# 26-01-10 민혁 추가: 반려동물 고민상담 이미지 모델
class PetCounselImage(models.Model):
    post = models.ForeignKey(
        PetCounselPost,
        related_name='images',
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to='pet_counsel/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"상담이미지 #{self.id}"


class PetCounselComment(models.Model):
    post = models.ForeignKey(
        "PetCounselPost",
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="고민상담 게시글"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="작성자"
    )
    content = models.TextField(verbose_name="댓글 내용")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")

    class Meta:
        ordering = ["created_at"]
        verbose_name = "반려동물 고민상담 댓글"
        verbose_name_plural = "반려동물 고민상담 댓글"

    def __str__(self):
        return f"{self.author} - {self.content[:20]}"


# ═══════════════════════════════════════════════════════════════════════
# 알림 모델 (25-12-29 슬기 추가)
# ═══════════════════════════════════════════════════════════════════════
class Notification(models.Model):
    """사용자 알림 모델"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="받는 사용자"
    )
    # 여러 타입의 게시글을 지원하기 위한 필드들
    free_post = models.ForeignKey(
        'FreePost',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="자유게시판 글"
    )
    pet_post = models.ForeignKey(
        'PetPost',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="반려동물 게시글"
    )
    flea_item = models.ForeignKey(
        'FleaItem',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="중고장터 아이템"
    )
    parenting_post = models.ForeignKey(
        'ParentingInfo',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="육아정보 게시글"
    )
    hotdeal_post = models.ForeignKey(
        'HotDeal',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="핫딜공유 게시글"
    )
    # ★ 26-01-06 추가: 요리레시피 게시글
    recipe_post = models.ForeignKey(
        'recipes.RecipePost',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="요리레시피 게시글"
    )
    message = models.CharField(
        max_length=255,
        verbose_name="알림 메시지"
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name="읽음 여부"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="생성일"
    )

    class Meta:
        verbose_name = '알림'
        verbose_name_plural = '알림'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.nickname} - {self.message[:30]}"
    
    def get_related_post(self):
        """관련된 게시글 반환"""
        if self.free_post:
            return self.free_post
        elif self.pet_post:
            return self.pet_post
        elif self.flea_item:
            return self.flea_item
        elif self.parenting_post:
            return self.parenting_post
        elif self.hotdeal_post:
            return self.hotdeal_post
        elif self.recipe_post:
            return self.recipe_post
        return None
    
    def get_post_url(self):
        """게시글 URL 반환"""
        from django.urls import reverse
        if self.free_post:
            return reverse('board:free_detail', args=[self.free_post.pk])
        elif self.pet_post:
            return reverse('board:pet_detail', args=[self.pet_post.pk])
        elif self.flea_item:
            return reverse('board:flea_detail', args=[self.flea_item.pk])
        elif self.parenting_post:
            return reverse('board:parenting_detail', args=[self.parenting_post.pk])
        elif self.hotdeal_post:
            return reverse('board:hotdeal_detail', args=[self.hotdeal_post.pk])
        elif self.recipe_post:
            return reverse('recipes:recipe_detail', args=[self.recipe_post.pk])
        return '#'


# 감정 리액션 모델 (26-01-02 추가)
# 사용자가 어떤 감정 리액션을 했는지 추적
class FreePostReaction(models.Model):
    REACTION_TYPES = [
        ('empathy', '공감해요 🤝'),
        ('courage', '힘내세요 💪'),
        ('cheer', '축하해요 🎉'),
        ('support', '응원해요 👏'),
        ('thanks', '고마워요 🙏'),
    ]
    
    post = models.ForeignKey(FreePost, on_delete=models.CASCADE, related_name='reactions', verbose_name="게시글")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="사용자")
    reaction_type = models.CharField(max_length=20, choices=REACTION_TYPES, verbose_name="리액션 타입")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")
    
    class Meta:
        verbose_name = '자유게시판 감정리액션'
        verbose_name_plural = '자유게시판 감정리액션'
        unique_together = ('post', 'user', 'reaction_type')  # 같은 글, 같은 사용자, 같은 리액션 타입은 1개만
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.post.title} - {self.user.username} ({self.reaction_type})"


# ★ 엄마 마음 케어 일기장 (26-01-02 추가 - 자유게시판 하위)
class MomDiary(models.Model):
    """엄마들의 감정과 일상을 기록하는 일기장"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mom_diary')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "엄마 마음 일기장"
    
    def __str__(self):
        return f"{self.user.username}의 일기장"


class DiaryEntry(models.Model):
    """일기 항목"""
    MOOD_CHOICES = [
        ('happy', '😊 행복해요'),
        ('peaceful', '😌 평온해요'),
        ('tired', '😫 피곤해요'),
        ('stressed', '😰 스트레스받아요'),
        ('sad', '😢 슬퍼요'),
        ('angry', '😠 화나요'),
        ('confused', '😕 혼란스러워요'),
    ]
    
    diary = models.ForeignKey(MomDiary, on_delete=models.CASCADE, related_name='entries')
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES, default='peaceful')
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    
    # AI 케어 응답
    ai_care_response = models.TextField(blank=True, null=True, help_text="AI가 생성한 공감 및 조언")
    ai_response_generated = models.BooleanField(default=False)
    
    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_secret = models.BooleanField(default=True, help_text="비공개 일기 여부 (기본값: True)")
    is_anonymous = models.BooleanField(default=False, help_text="대나무숲 공유 (익명 공개)")
    tags = models.CharField(max_length=500, blank=True, help_text="쉼표로 구분 (육아, 부부관계, 취업, ...)")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "일기 항목"
    
    def __str__(self):
        return f"{self.diary.user.username} - {self.created_at.strftime('%Y-%m-%d')}"

