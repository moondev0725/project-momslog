# 📁 맘스로그 프로젝트 파일 구조 완전 가이드 (초보자용)

> 이 문서는 Django 초보자가 프로젝트의 모든 파일과 폴더를 이해할 수 있도록 작성되었습니다.
> 각 파일의 역할, 연결 관계, 그리고 왜 필요한지를 상세히 설명합니다.

---

## 📂 전체 프로젝트 구조 (트리 뷰)

```
mompjt/                                 ← 프로젝트 최상위 폴더 (루트)
│
├── 📄 manage.py                        ← Django 명령어 실행 파일 (서버 시작, 마이그레이션 등)
├── 📄 db.sqlite3                       ← 데이터베이스 파일 (개발용 SQLite)
├── 📄 START_HERE.txt                   ← 프로젝트 시작 안내 문서
├── 📄 PROJECT_STRUCTURE_DETAIL.md      ← 기능별 상세 설명 문서
├── 📄 FILE_STRUCTURE_GUIDE.md          ← 이 파일! 파일 구조 완전 가이드
│
├── 📁 mompjt/                          ← Django 프로젝트 설정 폴더 (프로젝트 이름과 동일)
│   ├── 📄 __init__.py                  ← 이 폴더를 Python 패키지로 인식시키는 파일
│   ├── 📄 settings.py                  ← 프로젝트 전체 설정 파일 (데이터베이스, 앱, 미들웨어 등)
│   ├── 📄 urls.py                      ← 프로젝트 최상위 URL 라우팅 (각 앱 URLs 연결)
│   ├── 📄 wsgi.py                      ← 배포용 웹서버 연동 파일 (WSGI)
│   ├── 📄 asgi.py                      ← 비동기 웹서버 연동 파일 (ASGI)
│   └── 📁 __pycache__/                 ← Python 컴파일 캐시 (자동생성, 무시해도 됨)
│
├── 📁 main/                            ← 메인 앱 (홈, 검색, 성장기록 등 핵심 기능)
│   ├── 📄 __init__.py                  ← Python 패키지 선언 파일
│   ├── 📄 apps.py                      ← 앱 설정 파일 (앱 이름, 기본 설정)
│   ├── 📄 models.py                    ← 데이터 모델 정의 (GrowthRecord 등)
│   ├── 📄 views.py                     ← 뷰 함수 (URL 요청을 처리하는 로직)
│   ├── 📄 urls.py                      ← main 앱 URL 라우팅
│   ├── 📄 forms.py                     ← 폼 정의 (GrowthRecordForm 등)
│   ├── 📄 admin.py                     ← Django 관리자 페이지 설정
│   ├── 📄 tests.py                     ← 테스트 코드 작성 파일
│   ├── 📁 migrations/                  ← 데이터베이스 마이그레이션 파일들 (자동생성)
│   │   ├── 📄 __init__.py
│   │   ├── 📄 0001_initial.py          ← 첫 번째 마이그레이션 (테이블 생성)
│   │   └── 📄 0002_initial.py          ← 두 번째 마이그레이션 (필드 추가 등)
│   ├── 📁 templates/                   ← HTML 템플릿 폴더
│   │   ├── 📄 base.html                ← 공통 레이아웃 (헤더, 네비, 푸터 포함)
│   │   ├── 📄 main.html                ← 메인 페이지 (사용되지 않을 수 있음)
│   │   └── 📁 main/                    ← main 앱 전용 템플릿 폴더
│   │       ├── 📄 index.html           ← 홈 화면 (메인 페이지)
│   │       ├── 📄 search_result.html   ← 검색 결과 페이지
│   │       ├── 📄 growth_chart.html    ← 성장 그래프 페이지 (Chart.js 사용)
│   │       └── 📄 map.html             ← 지도 페이지 (Naver Maps 연동)
│   └── 📁 __pycache__/                 ← Python 컴파일 캐시
│
├── 📁 accounts/                        ← 회원 관리 앱 (회원가입, 로그인, 프로필 등)
│   ├── 📄 __init__.py
│   ├── 📄 apps.py
│   ├── 📄 models.py                    ← User 모델 확장 (닉네임, 주소, 자녀정보 등)
│   ├── 📄 views.py                     ← 회원가입, 로그인, 프로필 수정 등 뷰
│   ├── 📄 urls.py                      ← accounts 앱 URL 라우팅
│   ├── 📄 forms.py                     ← 회원가입 폼, 프로필 수정 폼 등
│   ├── 📄 admin.py                     ← 관리자 페이지 User 등록
│   ├── 📄 tests.py
│   ├── 📁 migrations/
│   ├── 📁 templates/accounts/          ← accounts 앱 템플릿
│   │   ├── 📁 login/
│   │   │   └── 📄 login.html           ← 로그인 페이지
│   │   ├── 📁 signup/
│   │   │   └── 📄 signup.html          ← 회원가입 페이지
│   │   ├── 📄 profile.html             ← 프로필 조회/수정 페이지
│   │   ├── 📄 profile_auth.html        ← 프로필 접근 전 비밀번호 인증
│   │   ├── 📄 find_id.html             ← 아이디 찾기 페이지
│   │   └── 📄 find_pw.html             ← 비밀번호 찾기 페이지
│   └── 📁 __pycache__/
│
├── 📁 board/                           ← 게시판 앱 (공지사항, 자유게시판, 벼룩시장 등)
│   ├── 📄 __init__.py
│   ├── 📄 apps.py
│   ├── 📄 models.py                    ← Post, Comment, FleaItem, Notification 등 모델
│   ├── 📄 views.py                     ← 게시판 CRUD, 댓글, 벼룩시장 등 뷰
│   ├── 📄 views_temp.py                ← 임시 뷰 파일 (백업 또는 테스트용)
│   ├── 📄 urls.py                      ← board 앱 URL 라우팅
│   ├── 📄 forms.py                     ← 게시글 작성 폼, 댓글 폼 등
│   ├── 📄 admin.py                     ← 관리자 페이지 게시글 관리
│   ├── 📄 tests.py
│   ├── 📁 migrations/
│   ├── 📁 templates/board/             ← board 앱 템플릿
│   │   ├── 📄 notice_list.html         ← 공지사항 목록
│   │   ├── 📄 notice_detail.html       ← 공지사항 상세
│   │   ├── 📄 notice_write.html        ← 공지사항 작성 (관리자 전용)
│   │   ├── 📄 free_list.html           ← 자유게시판 목록
│   │   ├── 📄 free_write.html          ← 자유게시판 글쓰기
│   │   ├── 📄 flea_list.html           ← 벼룩시장 목록
│   │   ├── 📄 flea_detail.html         ← 벼룩시장 상세 페이지
│   │   ├── 📄 flea_detail_new.html     ← 벼룩시장 상세 (새 버전)
│   │   ├── 📄 flea_write.html          ← 벼룩시장 글쓰기
│   │   ├── 📄 flea_delete.html         ← 벼룩시장 삭제 확인
│   │   ├── 📄 flea_comment_form.html   ← 벼룩시장 댓글 작성
│   │   ├── 📄 flea_comment_delete.html ← 벼룩시장 댓글 삭제
│   │   └── 📄 notification_list.html   ← 알림 목록 페이지
│   └── 📁 __pycache__/
│
├── 📁 chatbot/                         ← 챗봇 앱 (AI 챗봇 위젯)
│   ├── 📄 __init__.py
│   ├── 📄 apps.py
│   ├── 📄 models.py                    ← 챗봇 메시지 모델 (필요시)
│   ├── 📄 views.py                     ← 챗봇 메시지 처리 뷰
│   ├── 📄 urls.py                      ← chatbot 앱 URL 라우팅
│   ├── 📄 admin.py
│   ├── 📄 tests.py
│   ├── 📁 migrations/
│   ├── 📁 templates/chatbot/
│   │   └── 📄 chatbot_widget.html      ← 챗봇 위젯 (우측 하단에 표시되는 UI)
│   └── 📁 __pycache__/
│
├── 📁 map/                             ← 지도 앱 (지역별 지도 표시)
│   ├── 📄 __init__.py
│   ├── 📄 apps.py
│   ├── 📄 models.py                    ← 지역 정보 모델 (필요시)
│   ├── 📄 views.py                     ← 지도 페이지 뷰
│   ├── 📄 urls.py                      ← map 앱 URL 라우팅
│   ├── 📄 admin.py
│   ├── 📄 tests.py
│   ├── 📁 migrations/
│   ├── 📁 templates/map/
│   │   └── 📄 map.html                 ← 지도 페이지 (Naver Maps API)
│   └── 📁 __pycache__/
│
├── 📁 static/                          ← 정적 파일 (CSS, JavaScript, 이미지 등)
│   ├── 📁 css/                         ← 스타일시트 폴더
│   │   ├── 📄 style.css                ← 전역 스타일 (헤더, 푸터, 버튼, 폰트 등)
│   │   ├── 📄 board.css                ← 게시판 스타일
│   │   ├── 📄 signup.css               ← 회원가입 페이지 스타일
│   │   ├── 📄 form.css                 ← 폼 공통 스타일
│   │   ├── 📄 dropdown.css             ← 드롭다운 메뉴 스타일
│   │   ├── 📄 flea_list.css            ← 벼룩시장 목록 스타일
│   │   ├── 📄 profile.css              ← 프로필 페이지 스타일
│   │   ├── 📄 profile_additional.css   ← 프로필 추가 스타일
│   │   ├── 📄 banner.css               ← 배너 스타일
│   │   ├── 📄 search.css               ← 검색 스타일
│   │   ├── 📄 search_result.css        ← 검색 결과 스타일
│   │   ├── 📄 map.css                  ← 지도 페이지 스타일
│   │   └── 📄 chatbot.css              ← 챗봇 위젯 스타일
│   │
│   └── 📁 images/                      ← 이미지 파일 폴더
│       ├── 📄 logo.png                 ← 사이트 로고 (구버전)
│       ├── 📄 logo2.png                ← 사이트 로고 (신버전, 현재 사용 중)
│       ├── 📄 favicon.png              ← 파비콘 (브라우저 탭 아이콘)
│       ├── 📄 ad_banner.png            ← 광고 배너 이미지
│       ├── 📄 image_1.png              ← 콘텐츠 이미지 1
│       ├── 📄 image_3.png              ← 콘텐츠 이미지 3
│       ├── 📄 image_4.png              ← 콘텐츠 이미지 4
│       ├── 📄 image_5.png              ← 콘텐츠 이미지 5
│       ├── 📄 miage_2.png              ← 콘텐츠 이미지 2 (오타 있음)
│       ├── 📄 nav_notice.png           ← 네비게이션 공지 아이콘
│       └── 📄 search_icon.png          ← 검색 아이콘
│
└── 📁 media/                           ← 사용자 업로드 파일 저장 폴더
    └── (사용자가 업로드한 이미지, 파일 등이 여기 저장됨)
```

---

## 🔍 핵심 파일 상세 설명

### 1️⃣ **manage.py** - Django 명령어 실행기

```python
# 역할: Django 프로젝트의 모든 명령어를 실행하는 진입점
# 사용 예시:
#   - python manage.py runserver          ← 개발 서버 시작
#   - python manage.py makemigrations     ← 모델 변경사항을 마이그레이션 파일로 생성
#   - python manage.py migrate            ← 데이터베이스에 마이그레이션 적용
#   - python manage.py createsuperuser    ← 관리자 계정 생성
```

**초보자 팁**: 이 파일은 직접 수정하지 않습니다. 명령어를 실행할 때만 사용합니다.

---

### 2️⃣ **mompjt/settings.py** - 프로젝트 전체 설정

```python
# 주요 설정 항목:

# 1. INSTALLED_APPS - 사용하는 앱 목록
INSTALLED_APPS = [
    'django.contrib.admin',      # 관리자 페이지
    'django.contrib.auth',       # 인증 시스템
    'main',                      # 메인 앱
    'accounts',                  # 회원 관리 앱
    'board',                     # 게시판 앱
    'chatbot',                   # 챗봇 앱
    'map',                       # 지도 앱
]

# 2. DATABASES - 데이터베이스 설정
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 3. STATIC_URL - 정적 파일 경로
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# 4. MEDIA_URL - 업로드 파일 경로
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

**초보자 팁**: 새로운 앱을 만들면 여기 `INSTALLED_APPS`에 추가해야 합니다.

---

### 3️⃣ **mompjt/urls.py** - 최상위 URL 라우팅

```python
# 역할: 각 앱의 URL을 연결하는 중앙 허브

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),           # 관리자 페이지
    path('', include('main.urls')),            # main 앱 (메인 홈)
    path('accounts/', include('accounts.urls')),  # accounts 앱 (로그인, 회원가입)
    path('board/', include('board.urls')),     # board 앱 (게시판)
    path('chatbot/', include('chatbot.urls')), # chatbot 앱
    path('map/', include('map.urls')),         # map 앱
]
```

**URL 구조 예시**:
- `http://localhost:8000/` → main 앱의 index 페이지
- `http://localhost:8000/accounts/login/` → accounts 앱의 로그인 페이지
- `http://localhost:8000/board/notice/` → board 앱의 공지사항 목록

---

### 4️⃣ **main/models.py** - 데이터 모델 정의

```python
# 역할: 데이터베이스 테이블 구조를 정의

from django.db import models
from django.contrib.auth.models import User

class GrowthRecord(models.Model):
    """성장 기록 모델 (아이의 키와 몸무게 기록)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    record_date = models.DateField()      # 기록 날짜
    height_cm = models.FloatField()       # 키 (cm)
    weight_kg = models.FloatField()       # 몸무게 (kg)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'record_date')  # 같은 날짜에 중복 기록 방지
```

**데이터베이스 테이블**: `main_growthrecord`

**초보자 팁**: 모델을 변경하면 `makemigrations` → `migrate` 명령어를 실행해야 데이터베이스에 반영됩니다.

---

### 5️⃣ **main/views.py** - 뷰 함수 (로직 처리)

```python
# 역할: URL 요청을 받아서 처리하고 템플릿에 데이터를 전달

from django.shortcuts import render
from .models import GrowthRecord
from .forms import GrowthRecordForm

def growth_chart(request):
    """성장 그래프 페이지"""
    if request.method == 'POST':
        form = GrowthRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.user = request.user
            record.save()
    
    # 사용자의 모든 기록 가져오기
    records = GrowthRecord.objects.filter(user=request.user).order_by('record_date')
    
    # 그래프용 데이터 준비
    labels = [rec.record_date.strftime('%Y-%m-%d') for rec in records]
    heights = [rec.height_cm for rec in records]
    weights = [rec.weight_kg for rec in records]
    
    return render(request, 'main/growth_chart.html', {
        'form': GrowthRecordForm(),
        'records': records,
        'labels': labels,
        'heights': heights,
        'weights': weights,
    })
```

**흐름**:
1. 사용자가 URL 접속 → Django가 해당 뷰 함수 실행
2. 뷰 함수가 데이터베이스에서 데이터 조회
3. 데이터를 템플릿에 전달
4. 템플릿이 HTML 렌더링

---

### 6️⃣ **main/urls.py** - main 앱 URL 라우팅

```python
# 역할: main 앱의 URL 패턴 정의

from django.urls import path
from . import views

app_name = 'main'  # 네임스페이스 (템플릿에서 {% url 'main:index' %} 형태로 사용)

urlpatterns = [
    path('', views.index, name='index'),                    # 홈 화면
    path('search/', views.search, name='search'),           # 검색
    path('growth/', views.growth_chart, name='growth_chart'),  # 성장 그래프
]
```

**URL 예시**:
- `/` → `views.index` 실행
- `/search/` → `views.search` 실행
- `/growth/` → `views.growth_chart` 실행

---

### 7️⃣ **main/forms.py** - 폼 정의

```python
# 역할: HTML 폼을 자동으로 생성하고 유효성 검사

from django import forms
from .models import GrowthRecord

class GrowthRecordForm(forms.ModelForm):
    """성장 기록 입력 폼"""
    class Meta:
        model = GrowthRecord
        fields = ['record_date', 'height_cm', 'weight_kg']
        widgets = {
            'record_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean(self):
        """커스텀 유효성 검사"""
        cleaned = super().clean()
        height = cleaned.get('height_cm')
        weight = cleaned.get('weight_kg')
        
        if height and height <= 0:
            self.add_error('height_cm', '키는 0보다 커야 합니다.')
        if weight and weight <= 0:
            self.add_error('weight_kg', '몸무게는 0보다 커야 합니다.')
        
        return cleaned
```

**사용 예시 (템플릿)**:
```html
<form method="post">
    {% csrf_token %}
    {{ form.record_date }}
    {{ form.height_cm }}
    {{ form.weight_kg }}
    <button type="submit">저장</button>
</form>
```

---

### 8️⃣ **main/templates/base.html** - 공통 레이아웃

```django
<!-- 역할: 모든 페이지가 상속받는 기본 레이아웃 -->

<!DOCTYPE html>
<html>
<head>
    <title>맘스로그</title>
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
</head>
<body>
    <header>
        <!-- 헤더: 로고, 검색창, 로그인/로그아웃 버튼 -->
    </header>
    
    <nav>
        <!-- 네비게이션: 공지사항, 자유게시판, 벼룩시장 등 -->
    </nav>
    
    <main>
        {% block content %}
        <!-- 각 페이지의 고유 콘텐츠가 여기 들어감 -->
        {% endblock %}
    </main>
    
    <footer>
        <!-- 푸터: 저작권 정보 -->
    </footer>
</body>
</html>
```

**자식 템플릿 예시**:
```django
{% extends 'base.html' %}

{% block content %}
<h1>내 페이지 제목</h1>
<p>내 페이지 내용</p>
{% endblock %}
```

---

### 9️⃣ **main/templates/main/growth_chart.html** - 성장 그래프 페이지

```django
<!-- 역할: 성장 기록 입력 폼 + Chart.js 그래프 시각화 -->

{% extends 'base.html' %}
{% load static %}

{% block content %}
<style>
    /* 페이지 전용 CSS (그래디언트 배경, 카드 레이아웃 등) */
</style>

<div class="growth-wrapper">
    <!-- 제목 -->
    <h2>우리 아이 성장 그래프</h2>
    
    <!-- 그래프 영역 -->
    <div class="chart-card">
        <canvas id="growthChart"></canvas>
    </div>
    
    <!-- 입력 폼 -->
    <div class="form-card">
        <form method="post">
            {% csrf_token %}
            {{ form.record_date }}
            {{ form.height_cm }}
            {{ form.weight_kg }}
            <button type="submit">추가하기</button>
        </form>
    </div>
    
    <!-- 기록 목록 테이블 -->
    <table>
        {% for record in records %}
        <tr>
            <td>{{ record.record_date }}</td>
            <td>{{ record.height_cm }}</td>
            <td>{{ record.weight_kg }}</td>
        </tr>
        {% endfor %}
    </table>
</div>

<!-- Chart.js 라이브러리 -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
    // 그래프 데이터 (뷰에서 전달받은 데이터)
    const labels = {{ labels_json|safe }};
    const heights = {{ heights_json|safe }};
    const weights = {{ weights_json|safe }};
    
    // Chart.js로 그래프 생성
    new Chart(document.getElementById('growthChart'), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: '키 (cm)',
                    data: heights,
                    borderColor: '#5b8def',
                },
                {
                    label: '몸무게 (kg)',
                    data: weights,
                    borderColor: '#ff9a7a',
                }
            ]
        }
    });
</script>
{% endblock %}
```

---

### 🔟 **static/css/style.css** - 전역 스타일

```css
/* 역할: 전체 사이트에 적용되는 공통 스타일 */

/* 폰트 설정 */
@import url('프리텐다드 폰트 CDN');

body {
    font-family: "Pretendard", sans-serif;
    background-color: #f4f6f8;
    margin: 0;
    padding: 0;
}

/* 헤더 스타일 */
header {
    background: white;
    padding: 15px 0;
    border-bottom: 1px solid #eee;
}

/* 버튼 스타일 */
.btn-login {
    background: linear-gradient(135deg, #ff9a9e, #ff6b6b);
    color: white;
    padding: 16px;
    border-radius: 12px;
}

/* 카드 스타일 */
.card {
    background: white;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.06);
    padding: 30px;
}
```

---

## 🔗 파일 간 연결 관계

### 예시: 성장 그래프 기능이 작동하는 흐름

```
1. 사용자가 브라우저에서 http://localhost:8000/growth/ 접속
   ↓
2. mompjt/urls.py → main 앱의 URLs로 라우팅
   ↓
3. main/urls.py → views.growth_chart 함수 실행
   ↓
4. main/views.py
   - GrowthRecord 모델에서 데이터 조회
   - GrowthRecordForm으로 폼 생성
   - 템플릿에 데이터 전달
   ↓
5. main/templates/main/growth_chart.html
   - base.html을 상속받아 헤더/푸터 자동 포함
   - 폼과 그래프 렌더링
   - Chart.js로 시각화
   ↓
6. static/css/style.css + growth_chart.html 내부 CSS
   - 페이지 스타일 적용
   ↓
7. 사용자가 폼 제출
   ↓
8. views.growth_chart (POST 요청 처리)
   - forms.py의 GrowthRecordForm으로 유효성 검사
   - models.py의 GrowthRecord에 데이터 저장
   - 페이지 새로고침
```

---

## 📚 초보자가 알아야 할 Django 용어

| 용어 | 설명 |
|------|------|
| **앱 (App)** | Django 프로젝트의 기능 단위 (main, accounts, board 등) |
| **모델 (Model)** | 데이터베이스 테이블을 정의하는 클래스 (models.py) |
| **뷰 (View)** | URL 요청을 처리하는 함수 또는 클래스 (views.py) |
| **템플릿 (Template)** | HTML 파일 (Django 템플릿 언어 사용) |
| **URL 라우팅** | URL과 뷰를 연결하는 설정 (urls.py) |
| **폼 (Form)** | 사용자 입력을 받는 HTML 폼과 유효성 검사 (forms.py) |
| **마이그레이션** | 모델 변경사항을 데이터베이스에 반영하는 파일 (migrations/) |
| **정적 파일** | CSS, JavaScript, 이미지 등 변하지 않는 파일 (static/) |
| **미디어 파일** | 사용자가 업로드한 파일 (media/) |

---

## 🚀 프로젝트 시작 방법 (초보자용)

### 1. 개발 서버 시작
```bash
python manage.py runserver
```
→ 브라우저에서 `http://localhost:8000/` 접속

### 2. 모델 변경 시 마이그레이션
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. 관리자 계정 생성
```bash
python manage.py createsuperuser
```
→ `http://localhost:8000/admin/` 에서 관리자 페이지 접속

### 4. 새로운 앱 생성
```bash
python manage.py startapp 앱이름
```
→ `settings.py`의 `INSTALLED_APPS`에 추가 필수!

---

## 💡 파일 수정 시 주의사항

### ✅ 자주 수정하는 파일
- `views.py` - 기능 추가/수정
- `models.py` - 데이터 구조 변경 (마이그레이션 필수)
- `urls.py` - URL 패턴 추가
- `templates/*.html` - 화면 디자인 수정
- `static/css/*.css` - 스타일 수정

### ❌ 건드리지 말아야 할 파일
- `__init__.py` - 자동 생성 파일
- `__pycache__/` - 자동 캐시 폴더
- `migrations/` - 직접 수정 금지 (명령어로만 생성)
- `manage.py` - Django 진입점 (수정 불필요)

---

## 🆘 문제 해결 가이드

### 문제 1: "Module not found" 에러
→ `settings.py`의 `INSTALLED_APPS`에 앱 추가했는지 확인

### 문제 2: 템플릿이 안 보임
→ 템플릿 경로가 `앱이름/templates/앱이름/파일명.html` 형식인지 확인

### 문제 3: CSS가 적용 안 됨
→ `{% load static %}` 추가했는지 확인  
→ `<link href="{% static 'css/파일명.css' %}">` 형식 사용

### 문제 4: 모델 변경이 반영 안 됨
→ `makemigrations` → `migrate` 실행 확인

### 문제 5: 관리자 페이지에 모델이 안 보임
→ `admin.py`에 `admin.site.register(모델명)` 추가

---

## 📞 추가 학습 자료

- **Django 공식 문서**: https://docs.djangoproject.com/
- **Django 튜토리얼**: https://docs.djangoproject.com/ko/5.0/intro/tutorial01/
- **Bootstrap 문서**: https://getbootstrap.com/
- **Chart.js 문서**: https://www.chartjs.org/

---

**문서 작성일**: 2025-12-29  
**대상**: Django 초보자  
**목적**: 프로젝트의 모든 파일과 폴더를 이해하고 자신있게 개발할 수 있도록 돕기
