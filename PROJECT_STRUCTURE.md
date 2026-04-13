# 맘스로그(MomPjt) 프로젝트 구조

## 📁 프로젝트 개요
육아 커뮤니티 플랫폼 - 맘스로그

---

## 📂 디렉토리 구조

```
mompjt/
│
├── manage.py                    # Django 관리 명령어 실행 파일
├── db.sqlite3                   # 데이터베이스 파일
├── db.sqlite3.backup            # 데이터베이스 백업
│
├── mompjt/                      # 프로젝트 설정 디렉토리
│   ├── settings.py              # Django 설정 파일
│   ├── urls.py                  # 메인 URL 라우팅
│   ├── wsgi.py                  # WSGI 배포 설정
│   └── asgi.py                  # ASGI 배포 설정
│
├── accounts/                    # 회원 관리 앱
│   ├── models.py                # CustomUser, UserProfile 모델
│   ├── views.py                 # 회원가입, 로그인, 프로필 관리
│   ├── forms.py                 # 회원가입, 프로필 수정 폼
│   ├── urls.py                  # accounts/ URL 라우팅
│   ├── tokens.py                # 이메일 인증 토큰 생성
│   ├── points.py                # 포인트 관리 시스템
│   ├── services.py              # 비즈니스 로직 (프로필, 포인트)
│   ├── constants.py             # 상수 정의 (포인트, 활동 타입)
│   └── templates/
│       ├── login.html           # 로그인 페이지
│       ├── signup.html          # 회원가입 페이지
│       ├── profile.html         # 프로필 페이지
│       ├── profile_edit.html    # 프로필 수정 페이지
│       └── activate_*.html      # 계정 활성화 관련
│
├── main/                        # 메인 앱 (홈페이지)
│   ├── models.py                # 메인 페이지 모델
│   ├── views.py                 # 메인 페이지, 검색 뷰
│   ├── forms.py                 # 검색 폼
│   ├── urls.py                  # 메인 URL 라우팅
│   └── templates/
│       ├── base.html            # 기본 템플릿 (네비게이션, 헤더, 푸터)
│       ├── main.html            # 메인 페이지
│       ├── search_result.html   # 검색 결과 페이지
│       └── main/
│           ├── index.html       # 대체 메인 페이지
│           └── map.html         # 지도 페이지
│
├── board/                       # 게시판 앱
│   ├── models.py                # Post, Comment, Like, Category 모델
│   ├── views.py                 # 게시글 CRUD, 댓글, 좋아요
│   ├── forms.py                 # 게시글 작성/수정 폼
│   ├── urls.py                  # board/ URL 라우팅
│   ├── views_temp.py            # 임시 뷰 파일
│   └── templates/
│       ├── board_list.html      # 게시판 목록
│       ├── post_detail.html     # 게시글 상세
│       ├── post_form.html       # 게시글 작성/수정
│       ├── flea_list.html       # 중고거래 목록
│       └── petpost_list.html    # 펫 게시판 목록
│
├── recipes/                     # 레시피 앱
│   ├── models.py                # Recipe, RecipeStep, Ingredient 모델
│   ├── views.py                 # 레시피 목록, 상세, 검색
│   ├── forms.py                 # 레시피 작성 폼
│   ├── urls.py                  # recipes/ URL 라우팅
│   └── templates/
│       ├── recipes_list.html    # 레시피 목록
│       ├── recipe_detail.html   # 레시피 상세 (슬라이더 배너 포함)
│       └── recipe_search.html   # 레시피 검색
│
├── map/                         # 지도 앱 (안심 지도)
│   ├── models.py                # SafetyReport, Location 모델
│   ├── views.py                 # 지도 뷰, 안전 리포트
│   ├── urls.py                  # map/ URL 라우팅
│   └── templates/
│       └── map/
│           └── map.html         # 카카오맵 기반 안심지도
│
├── quests/                      # 퀘스트/미션 앱
│   ├── models.py                # Quest, UserQuest, Reward 모델
│   ├── views.py                 # 퀘스트 목록, 완료, 보상
│   ├── services.py              # 퀘스트 비즈니스 로직
│   ├── context_processors.py   # 전역 컨텍스트 (알림 등)
│   └── urls.py                  # quests/ URL 라우팅
│
├── chatbot/                     # 챗봇 앱
│   ├── models.py                # ChatMessage, FAQ 모델
│   ├── views.py                 # 챗봇 API 뷰
│   ├── urls.py                  # chatbot/ URL 라우팅
│   └── templates/
│       └── chatbot/
│           └── chatbot_widget.html  # 챗봇 위젯
│
├── static/                      # 정적 파일 (개발용)
│   ├── css/
│   │   ├── style.css            # 메인 스타일
│   │   ├── banner.css           # 배너 스타일
│   │   ├── board.css            # 게시판 스타일
│   │   ├── recipes.css          # 레시피 스타일
│   │   ├── map.css              # 지도 스타일
│   │   ├── chatbot.css          # 챗봇 스타일
│   │   ├── form.css             # 폼 스타일
│   │   ├── signup.css           # 회원가입 스타일
│   │   ├── profile.css          # 프로필 스타일
│   │   └── dropdown.css         # 드롭다운 메뉴 스타일
│   ├── images/
│   │   ├── logo.png             # 로고 이미지
│   │   ├── logo2.png            # 대체 로고
│   │   ├── favicon.png          # 파비콘
│   │   ├── image_1.png ~ image_5.png  # 배너 이미지
│   │   ├── ad_banner.png        # 광고 배너
│   │   └── search_icon.png      # 검색 아이콘
│   └── js/
│       └── signup.js            # 회원가입 자바스크립트
│
├── staticfiles/                 # 배포용 정적 파일 (collectstatic)
│
└── media/                       # 사용자 업로드 파일
    ├── profile_pictures/        # 프로필 사진
    ├── post_images/             # 게시글 이미지
    ├── recipe_images/           # 레시피 이미지
    └── recipe_steps/            # 레시피 단계별 이미지
```

---

## 🎯 주요 기능별 파일 위치

### 1. 사용자 인증 & 프로필
- **모델**: `accounts/models.py` - CustomUser, UserProfile
- **뷰**: `accounts/views.py` - signup, login, profile, profile_edit
- **템플릿**: `accounts/templates/`
- **URL**: `/accounts/` 경로

### 2. 메인 페이지 & 네비게이션
- **베이스 템플릿**: `main/templates/base.html` (모든 페이지의 기본 레이아웃)
- **메인 페이지**: `main/templates/main.html`
- **검색 기능**: `main/views.py` - search_view
- **URL**: `/` (홈), `/search/`

### 3. 게시판 (자유게시판, 중고거래, 펫 게시판)
- **모델**: `board/models.py` - Post, Comment, Like, Category
- **뷰**: `board/views.py` - post_list, post_detail, comment_create
- **템플릿**: `board/templates/`
- **URL**: `/board/`, `/board/<id>/`, `/flea/`, `/petpost/`

### 4. 레시피 (육아 레시피)
- **모델**: `recipes/models.py` - Recipe, RecipeStep, Ingredient
- **뷰**: `recipes/views.py` - recipes_list, recipe_detail
- **템플릿**: `recipes/templates/`
  - `recipe_detail.html` - 배너 슬라이더 포함
- **URL**: `/recipes/`, `/recipes/<id>/`

### 5. 안심 지도
- **모델**: `map/models.py` - SafetyReport, Location
- **뷰**: `map/views.py` - map_view
- **템플릿**: `map/templates/map/map.html` (카카오맵 API)
- **URL**: `/map/`

### 6. 퀘스트 시스템
- **모델**: `quests/models.py` - Quest, UserQuest, Reward
- **뷰**: `quests/views.py` - quest_list, complete_quest
- **비즈니스 로직**: `quests/services.py`
- **URL**: `/quests/`

### 7. 챗봇
- **모델**: `chatbot/models.py` - ChatMessage, FAQ
- **뷰**: `chatbot/views.py` - chatbot_response
- **템플릿**: `chatbot/templates/chatbot/chatbot_widget.html`
- **URL**: `/chatbot/api/chat/`

---

## 🔧 설정 파일

### `mompjt/settings.py`
```python
INSTALLED_APPS = [
    'accounts',
    'main',
    'board',
    'recipes',
    'map',
    'quests',
    'chatbot',
    ...
]

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
```

### `mompjt/urls.py`
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('accounts/', include('accounts.urls')),
    path('board/', include('board.urls')),
    path('recipes/', include('recipes.urls')),
    path('map/', include('map.urls')),
    path('quests/', include('quests.urls')),
    path('chatbot/', include('chatbot.urls')),
]
```

---

## 🗄️ 주요 모델 관계

```
CustomUser (accounts)
    ├── UserProfile (1:1) - 프로필 정보
    ├── Post (1:N) - 작성한 게시글
    ├── Comment (1:N) - 작성한 댓글
    ├── Recipe (1:N) - 작성한 레시피
    ├── UserQuest (1:N) - 진행 중인 퀘스트
    └── ChatMessage (1:N) - 챗봇 대화 기록

Post (board)
    ├── Comment (1:N) - 댓글
    ├── Like (1:N) - 좋아요
    └── Category (N:1) - 카테고리

Recipe (recipes)
    ├── RecipeStep (1:N) - 조리 단계
    └── Ingredient (1:N) - 재료

Quest (quests)
    └── UserQuest (1:N) - 사용자별 퀘스트 진행 상황
```

---

## 📱 페이지 URL 맵

| 기능 | URL | 템플릿 | 뷰 |
|------|-----|--------|-----|
| 메인 페이지 | `/` | `main.html` | `main.views.home` |
| 로그인 | `/accounts/login/` | `login.html` | `accounts.views.login_view` |
| 회원가입 | `/accounts/signup/` | `signup.html` | `accounts.views.signup` |
| 프로필 | `/accounts/profile/` | `profile.html` | `accounts.views.profile` |
| 게시판 목록 | `/board/` | `board_list.html` | `board.views.post_list` |
| 게시글 상세 | `/board/<id>/` | `post_detail.html` | `board.views.post_detail` |
| 중고거래 | `/flea/` | `flea_list.html` | `board.views.flea_list` |
| 레시피 목록 | `/recipes/` | `recipes_list.html` | `recipes.views.recipes_list` |
| 레시피 상세 | `/recipes/<id>/` | `recipe_detail.html` | `recipes.views.recipe_detail` |
| 안심 지도 | `/map/` | `map.html` | `map.views.map_view` |
| 퀘스트 | `/quests/` | `quest_list.html` | `quests.views.quest_list` |
| 챗봇 API | `/chatbot/api/chat/` | JSON 응답 | `chatbot.views.chatbot_response` |

---

## 🚀 실행 방법

```bash
# 가상환경 활성화
.venv\Scripts\activate

# 개발 서버 실행
cd c:\workspace\dijango7\d0102\mompjt
python manage.py runserver

# 정적 파일 수집 (배포 시)
python manage.py collectstatic

# 마이그레이션
python manage.py makemigrations
python manage.py migrate
```

---

## 📝 최근 수정 사항

### 2026-01-02
- ✅ `recipe_detail.html` - 배너 슬라이더 추가 (5개 항목, 자동 슬라이드)
- ✅ JavaScript 이벤트 리스너 방식으로 변경 (onclick 제거)
- ✅ 이미지 표시 문제 수정 (flex 레이아웃 최적화)

---

## 🔑 핵심 특징

1. **포인트 시스템** - 활동별 포인트 적립 (`accounts/points.py`)
2. **퀘스트/미션** - 일일 미션, 보상 시스템
3. **커뮤니티** - 게시판, 댓글, 좋아요, 중고거래
4. **레시피 공유** - 단계별 이미지, 재료 관리
5. **안심 지도** - 카카오맵 기반 위치 정보
6. **AI 챗봇** - 육아 상담 챗봇

---

**개발 환경**: Django 5.x, Python 3.x  
**프로젝트명**: 맘스로그 (MomPjt)  
**목적**: 육아 커뮤니티 통합 플랫폼
