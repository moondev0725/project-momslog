from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ✅ 중복 확인 (AJAX) - 회원가입용 기존 유지
    path('check-id/', views.check_id, name='check_id'),
    path('check-nickname/', views.check_nickname, name='check_nickname'),
    path('check-email/', views.check_email, name='check_email'),

    # ✅ 이메일 인증번호 방식 (회원가입 페이지 내부) - 기존 유지
    path("email/send-code/", views.send_email_code, name="send_email_code"),
    path("email/verify-code/", views.verify_email_code, name="verify_email_code"),

    # ✅ 아이디/비번 찾기
    path('find-id/', views.find_id, name='find_id'),
    path('find-pw/', views.find_pw, name='find_pw'),

    # 0105 성훈=======================================================================================
    # ✅ 마이페이지 진입 전 비번 확인(기존 유지)
    path('profile/auth/', views.profile_auth, name='profile_auth'),

    # ✅ 기존 profile/ 은 안 깨지게 유지하되 새 마이페이지로 보내기
    path('profile/', views.profile, name='profile'),

    # ✅ (신규) 마이페이지 구조
    path('mypage/', views.mypage_home, name='mypage_home'),
    path('mypage/profile/', views.mypage_profile, name='mypage_profile'),
    path('mypage/my-posts/', views.mypage_my_posts, name='mypage_my_posts'),
    path('mypage/grade-exp/', views.mypage_grade_exp, name='mypage_grade_exp'),
    path('mypage/account/password/', views.mypage_password_change, name='mypage_password_change'),
    path('mypage/account/password/check/', views.mypage_password_check, name='mypage_password_check'),
    path('mypage/account/delete/', views.mypage_account_delete, name='mypage_account_delete'),

    # ✅ 관리자 대시보드
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/report/<int:report_id>/resolve/', views.resolve_flea_report, name='resolve_flea_report'),
    path('admin/report/<int:report_id>/<str:status>/', views.update_flea_report_status, name='update_flea_report_status'),

    # ✅ (신규) 마이페이지 - 닉네임 실시간 중복확인(본인 제외)
    path('mypage/check-nickname/', views.mypage_check_nickname, name='mypage_check_nickname'),

    # ✅ (신규) 마이페이지 - 이메일 변경 인증(본인 제외 중복체크)
    path('mypage/email/send-code/', views.mypage_send_email_code, name='mypage_send_email_code'),
    path('mypage/email/verify-code/', views.mypage_verify_email_code, name='mypage_verify_email_code'),
    # 0105 성훈=======================================================================================
]
