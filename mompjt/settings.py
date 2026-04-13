from pathlib import Path
import os

# ==================== 프로젝트 기본 경로 설정 ====================
BASE_DIR = Path(__file__).resolve().parent.parent  # 프로젝트 루트 디렉토리


# ==================== 보안 설정 ====================
SECRET_KEY = 'django-insecure-j)!mbyhg)gd@vm!+5m2a2xz(s)eso+nnzdx=b4f(3b6g-u(#iz'  # SECRET KEY (운영환경에서는 변경 필수)
DEBUG = True  # 개발 모드 (운영환경에서는 False로 변경)
ALLOWED_HOSTS = []  # 허용할 호스트명 (운영환경에서 설정 필요)


# ==================== Django 앱 등록 ====================
INSTALLED_APPS = [
    # Django 기본 앱
    'django.contrib.admin',         # 관리자 페이지
    'django.contrib.auth',          # 인증 시스템
    'django.contrib.contenttypes',  # 캔텐츠 타입
    'django.contrib.sessions',      # 세션 관리
    'django.contrib.messages',      # 메시지 시스템
    'django.contrib.staticfiles',   # 정적 파일 관리
    'django.contrib.humanize',      # 템플릿 필터 (숫자 포매팅 등)
    
    # 커스터 앱
    'main',        # 메인 페이지
    'accounts',    # 회원 인증
    'map',         # 지도 기능
    'board',       # 게시판 (공지, 자유게시판, 벼룩시장, 댓글)
    'chatbot',     # 챗봇
    'quests',                       # �에스트 앱
    'recipes',                       # 레시피 앱
    'chat.apps.ChatConfig',         # ★ 26-01-02 추가: 실시간 채팅 앱 (AppConfig 경로로 등록해야 Django가 인식)
]

# ==================== Django Channels 설정 ====================
# ★ 26-01-02 중요 주의사항:
# 'daphne'는 Django 앱이 아니라 ASGI 서버입니다!
# INSTALLED_APPS에 등록하면 runserver가 실패합니다.
# 대신 다음과 같이 사용합니다:
#   - 개발 서버: python manage.py runserver (WSGI, 일반 HTTP만 지원)
#   - WebSocket: daphne -b 0.0.0.0 -p 8000 mompjt.asgi:application

# ==================== 미들웨어 설정 ====================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',         # 보안
    'django.contrib.sessions.middleware.SessionMiddleware',   # 세션
    'django.middleware.common.CommonMiddleware',              # 공통
    'django.middleware.csrf.CsrfViewMiddleware',              # CSRF 보호
    'django.contrib.auth.middleware.AuthenticationMiddleware', # 인증
    'django.contrib.messages.middleware.MessageMiddleware',   # 메시지
    'django.middleware.clickjacking.XFrameOptionsMiddleware', # 클릭재킹 방지
]

ROOT_URLCONF = 'mompjt.urls'  # 메인 URL 설정 파일

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # ✅ 성훈 1231추가
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # 성훈 1231 추가-------------------------------------------
                'quests.context_processors.today_quest',
                # 성훈 1231 추가-------------------------------------------
            ],
        },
    },
]

# ==================== ASGI/WSGI 애플리케이션 설정 ====================
# ASGI: Django Channels (WebSocket, 비동기 지원)
# WSGI: 기존 WSGI 서버 호환성
ASGI_APPLICATION = 'mompjt.asgi.application'  # ★ 26-01-02 추가: Daphne 또는 다른 ASGI 서버에서 사용
WSGI_APPLICATION = 'mompjt.wsgi.application'  # WSGI 애플리케이션 (runserver에서 사용)


# ==================== Django Channels 설정 ====================
# ★ 26-01-02 추가: WebSocket 통신을 위한 채널 레이어 설정
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'  # 개발용 in-memory
        # 운영 환경에서는 Redis 사용 권장:
        # 'BACKEND': 'channels_redis.core.RedisChannelLayer',
        # 'CONFIG': {
        #     'hosts': [('127.0.0.1', 6379)],
        # },
    }
}


# ==================== 데이터베이스 설정 ====================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # SQLite 사용 (개발용)
        'NAME': BASE_DIR / 'db.sqlite3',         # DB 파일 위치
    }
}


# ==================== 비밀번호 검증 규칙 ====================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ==================== 국제화 & 시간대 설정 ====================
LANGUAGE_CODE = 'ko-kr'    # 한국어
TIME_ZONE = 'Asia/Seoul'   # 한국 시간대
USE_I18N = True            # 다국어 지원
USE_TZ = True              # 타임존 인식


# ==================== 정적 파일 (CSS, JS, Image) 설정 ====================
STATIC_URL = 'static/'  # 정적 파일 URL
STATIC_ROOT = BASE_DIR / 'staticfiles'  # collectstatic 결과물 저장 경로 (운영환경)
STATICFILES_DIRS = [    # 프로젝트 루트의 static 폴더 인식
    BASE_DIR / 'static',
]

# ==================== 사용자 업로드 파일 (Media) 설정 ====================
MEDIA_URL = '/media/'           # 미디어 파일 URL
MEDIA_ROOT = BASE_DIR / 'media' # 미디어 파일 저장 경로 (상품 이미지 등)

# ==================== 기본 설정 ====================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'  # 기본 primary key 타입
AUTH_USER_MODEL = 'accounts.User'  # 커스터 사용자 모델

# ==================== Google Generative AI (Gemini) 설정 ====================
# 환경 변수 또는 여기에 API 키를 설정하세요
GOOGLE_API_KEY = 'AIzaSyB95Bobxucs-59ipHySfb2634JCrLM6Dj4'  # Google Gemini API 키
if not GOOGLE_API_KEY:
    print("⚠️  경고: GOOGLE_API_KEY가 설정되지 않았습니다!")
    print("   환경 변수 GOOGLE_API_KEY를 설정하거나 settings.py에서 직접 입력해주세요.")

# ==================== 캐싱 설정 (성능 최적화) ====================
# Django 캐시 프레임워크 설정
# 메모리 캐시를 사용하여 데이터베이스 쿼리 부하 감소
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',  # 로컬 메모리 캐시 (개발/테스트용)
        'LOCATION': 'unique-snowflake',  # 캐시 이름
        'OPTIONS': {
            'MAX_ENTRIES': 1000  # 최대 저장 항목 수
        },
        'TIMEOUT': 300  # 기본 TTL: 5분
    }
    # 운영 환경에서는 Redis 사용 권장:
    # 'default': {
    #     'BACKEND': 'django_redis.cache.RedisCache',
    #     'LOCATION': 'redis://127.0.0.1:6379/1',
    #     'OPTIONS': {
    #         'CLIENT_CLASS': 'django_redis.client.DefaultClient',
    #     }
    # }
}

# ==================== 이메일 설정 (Gmail SMTP) ====================
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # SMTP 백엔드
# EMAIL_HOST = 'smtp.gmail.com'                                  # Gmail SMTP 서버
# EMAIL_PORT = 587                                               # SMTP 포트
# EMAIL_USE_TLS = True                                           # TLS 암호화
# EMAIL_HOST_USER = 'your-email@gmail.com'                       # 발신 이메일 (수정 필요)
# EMAIL_HOST_PASSWORD = 'your-app-password'                      # Gmail 앱 비밀번호 (수정 필요)
# DEFAULT_FROM_EMAIL = EMAIL_HOST_USER                           # 기본 발신자

# ==================== 이메일 설정 (개발용: 콘솔 출력) ====================
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "no-reply@momslog.local"