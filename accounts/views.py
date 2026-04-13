from datetime import timedelta
import random

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from urllib.parse import urlencode
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count
from django.db.models.functions import TruncDate

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .forms import SignUpForm
from board.models import FleaReport
from .models import User, SignupBlock


# =========================
# ✅ 이메일 인증번호 발송/검증 (회원가입 페이지 내부)
# =========================

@require_POST
def send_email_code(request):
    email = (request.POST.get("email") or "").strip()

    if not email:
        return JsonResponse({"ok": False, "error": "이메일을 입력해 주세요."})

    # ✅ 중복 체크
    if User.objects.filter(email=email).exists():
        return JsonResponse({"ok": False, "error": "이미 사용 중인 이메일입니다."})

    code = f"{random.randint(0, 999999):06d}"

    request.session["email_verify_code"] = code
    request.session["email_verify_target"] = email
    request.session["email_verify_tries"] = 0
    request.session["email_verify_sent_at"] = int(timezone.now().timestamp())
    request.session.pop("verified_email", None)  # 이메일 바뀌면 인증 초기화

    subject = "[맘스로그] 이메일 인증번호"
    message = f"인증번호: {code}\n\n5분 이내에 입력해 주세요."

    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
    except Exception as e:
        print("send_email_code mail error:", e)
        return JsonResponse({"ok": False, "error": "메일 발송에 실패했습니다."})

    return JsonResponse({"ok": True})


@require_POST
def verify_email_code(request):
    email = (request.POST.get("email") or "").strip()
    code = (request.POST.get("code") or "").strip()

    if not email or not code:
        return JsonResponse({"ok": False, "error": "이메일과 인증번호를 입력해 주세요."})

    target = request.session.get("email_verify_target")
    saved = request.session.get("email_verify_code")
    tries = int(request.session.get("email_verify_tries") or 0)
    sent_at = int(request.session.get("email_verify_sent_at") or 0)

    if not target or not saved or target != email:
        return JsonResponse({"ok": False, "error": "인증번호를 다시 요청해 주세요."})

    # ✅ 5분(300초) 만료
    now_ts = int(timezone.now().timestamp())
    if now_ts - sent_at > 300:
        return JsonResponse({"ok": False, "error": "인증번호가 만료되었습니다. 다시 요청해 주세요."})

    # ✅ 최대 5회
    if tries >= 5:
        return JsonResponse({"ok": False, "error": "시도 횟수를 초과했습니다. 다시 요청해 주세요."})

    if code != saved:
        request.session["email_verify_tries"] = tries + 1
        return JsonResponse({"ok": False, "error": "인증번호가 올바르지 않습니다."})

    # ✅ 성공
    request.session["verified_email"] = email
    return JsonResponse({"ok": True})


# =========================
# 1. 회원가입
# =========================
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        terms_agreed = request.POST.get('terms_agreed')
        if not terms_agreed:
            messages.error(request, "이용약관 및 개인정보 처리방침에 동의해 주세요.")

        if terms_agreed and form.is_valid():
            # ✅ 탈퇴 후 15일 재가입 제한
            username = form.cleaned_data.get("username")
            now = timezone.now()
            if username and SignupBlock.objects.filter(username=username, blocked_until__gt=now).exists():
                messages.error(request, "최근 탈퇴한 아이디는 15일간 재가입이 제한됩니다.")
                return render(request, 'accounts/signup/signup.html', {'form': form})

            # ✅ 이메일 인증 완료 체크(세션)
            verified_email = (request.session.get("verified_email") or "").strip()
            form_email = (form.cleaned_data.get("email") or "").strip()

            if not verified_email or verified_email != form_email:
                messages.error(request, "이메일 인증을 먼저 완료해 주세요.")
                return render(request, 'accounts/signup/signup.html', {'form': form})

            user = form.save(commit=False)
            user.terms_agreed = True

            # ✅ 인증번호 인증 통과 → 바로 활성
            user.is_active = True
            user.save()
            form.save_m2m()

            # ✅ 가입 완료 후 로그인
            login(request, user)

            # ✅ 인증 세션 정리(선택)
            request.session.pop("email_verify_code", None)
            request.session.pop("email_verify_target", None)
            request.session.pop("email_verify_tries", None)
            request.session.pop("email_verify_sent_at", None)
            request.session.pop("verified_email", None)

            messages.success(request, "가입이 완료되었습니다. 로그인 되었습니다!")
            return redirect('/')

        if form.errors:
            print("회원가입 실패:", form.errors)

    else:
        form = SignUpForm()

    return render(request, 'accounts/signup/signup.html', {'form': form})


# =========================
# 2. 로그인
# =========================
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, "로그인 되었습니다.")
            return redirect('/')
        else:
            error = "아이디 또는 비밀번호가 일치하지 않습니다."
            return render(request, 'accounts/login/login.html', {'form': form, 'error': error})
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login/login.html', {'form': form})


# =========================
# 3. 로그아웃
# =========================
def logout_view(request):
    logout(request)
    return redirect('/')


# =========================
# 4. 아이디 중복 확인 (AJAX)
# =========================
@require_GET
def check_id(request):
    username = (request.GET.get('username') or '').strip()
    UserModel = get_user_model()

    if not username:
        return JsonResponse({'exists': True})

    try:
        exists = UserModel.objects.filter(username=username).exists()
        return JsonResponse({'exists': exists})
    except Exception as e:
        print(f"ID Check Error: {e}")
        return JsonResponse({'exists': True})


# =========================
# 5. 닉네임 중복 확인 (AJAX)
# =========================
@require_GET
def check_nickname(request):
    nickname = (request.GET.get('nickname') or '').strip()
    UserModel = get_user_model()

    if not nickname:
        return JsonResponse({'exists': True})

    try:
        exists = UserModel.objects.filter(nickname=nickname).exists()
        return JsonResponse({'exists': exists})
    except Exception as e:
        print(f"Nickname Check Error: {e}")
        return JsonResponse({'exists': True})


# =========================
# 6. 이메일 중복 확인 (AJAX)
# =========================
@require_GET
def check_email(request):
    email = (request.GET.get('email') or '').strip()
    exists = False
    if email:
        exists = User.objects.filter(email=email).exists()
    return JsonResponse({'exists': exists})


# =========================
# 7. 비밀번호 찾기
# =========================
def find_pw(request):
    context = {}
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')

        try:
            UserModel = get_user_model()
            user = UserModel.objects.get(username=username, email=email)

            import string
            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

            user.set_password(temp_password)
            user.save()

            subject = '[맘스로그] 임시 비밀번호 발급 안내'
            message = f'''
안녕하세요, {user.real_name}님

임시 비밀번호가 발급되었습니다.

아이디: {user.username}
임시 비밀번호: {temp_password}

로그인 후 반드시 비밀번호를 변경해 주세요.

감사합니다.
맘스로그 드림
            '''

            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                context['found'] = True
            except Exception as e:
                print(f"이메일 발송 실패: {e}")
                context['error'] = f"임시 비밀번호 생성에는 성공했으나 이메일 발송에 실패했습니다. 관리자에게 문의하세요. (임시 비밀번호: {temp_password})"

        except User.DoesNotExist:
            context['error'] = "입력하신 아이디와 이메일이 일치하는 회원 정보를 찾을 수 없습니다."

    return render(request, 'accounts/find_pw.html', context)


# =========================
# 8. 아이디 찾기
# =========================
def find_id(request):
    context = {}
    if request.method == 'POST':
        real_name = request.POST.get('real_name')
        email = request.POST.get('email')

        try:
            UserModel = get_user_model()
            user = UserModel.objects.get(real_name=real_name, email=email)
            context['found_id'] = user.username
        except UserModel.DoesNotExist:
            context['error'] = "일치하는 회원 정보를 찾을 수 없습니다."

    return render(request, 'accounts/find_id.html', context)


# =========================
# 9. 비밀번호 확인 (검문소)  ✅ (추가)
# =========================
@login_required
def profile_auth(request):
    """
    /accounts/profile/auth/
    보호 페이지 진입 전 비밀번호 재확인(검문소)
    - next 파라미터가 있으면 인증 성공 후 그 페이지로 이동
    """
    next_url = (request.POST.get("next") or request.GET.get("next") or "").strip()

    if request.method == 'POST':
        password = request.POST.get('password')

        if request.user.check_password(password):
            request.session['is_verified'] = True

            # ✅ next가 안전한(동일 호스트) URL일 때만 이동
            if next_url and url_has_allowed_host_and_scheme(
                url=next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)

            return redirect('accounts:mypage_home')
        else:
            messages.error(request, '비밀번호가 일치하지 않습니다.')

    return render(request, 'accounts/profile_auth.html', {"next": next_url})


# =========================
# 10. 기존 profile URL 유지용 ✅ (추가)
# =========================
@login_required
def profile(request):
    """
    기존 /accounts/profile/ URL을 깨지지 않게 유지하면서
    새 마이페이지 개인정보로 보냄
    """
    return redirect('accounts:mypage_profile')


# 0105 성훈=======================================================================================
@login_required
def mypage_home(request):
    return render(request, 'accounts/mypage/home.html')


@login_required
def mypage_profile(request):
    # ✅ 비밀번호 재확인 세션 체크 (기존 흐름 유지)
    if not request.session.get('is_verified'):
        return redirect(f"{reverse('accounts:profile_auth')}?{urlencode({'next': request.get_full_path()})}")

    user = request.user
    UserModel = get_user_model()

    if request.method == "POST":
        # ---- 닉네임 변경: 실시간 체크는 프론트, 저장 시 서버에서도 한번 더 안전검사 ----
        new_nickname = (request.POST.get("nickname") or "").strip()
        if new_nickname and new_nickname != getattr(user, "nickname", ""):
            if UserModel.objects.exclude(pk=user.pk).filter(nickname=new_nickname).exists():
                messages.error(request, "이미 사용 중인 닉네임입니다.")
                return redirect("accounts:mypage_profile")
            user.nickname = new_nickname

        # ---- 이메일 변경: '변경 시'에만 인증 필수 ----
        new_email = (request.POST.get("email") or "").strip()
        current_email = (user.email or "").strip()

        if new_email != current_email:
            # 변경하려면 인증 완료된 이메일이어야 함
            verified_email = (request.session.get("verified_email_change") or "").strip()
            if not verified_email or verified_email != new_email:
                messages.error(request, "이메일 변경은 인증 완료 후 저장할 수 있습니다.")
                return redirect("accounts:mypage_profile")

            # 본인 제외 중복검사(세션 위변조 대비)
            if UserModel.objects.exclude(pk=user.pk).filter(email=new_email).exists():
                messages.error(request, "이미 사용 중인 이메일입니다.")
                return redirect("accounts:mypage_profile")

            user.email = new_email
            request.session.pop("verified_email_change", None)

        # ---- 추가 정보: 깔끔하게(있으면 보여주고, 없으면 건드리지 않음) ----
        # address 필드가 있는 경우만 수정 가능하게
        address = (request.POST.get("address") or "").strip()
        if hasattr(user, "address"):
            user.address = address
            
        address_detail = (request.POST.get("address_detail") or "").strip()
        if hasattr(user, "address_detail"):
            user.address_detail = address_detail
            
        # ✅ 저장 시 자동 정리: address 끝에 상세주소가 붙어있으면 제거(구분자 포함 robust)
        if hasattr(user, "address") and hasattr(user, "address_detail"):
            import re
            base = (user.address or "").strip()
            detail = (user.address_detail or "").strip()

            if base and detail:
                # 끝에 " 1111gh" / ",1111gh" / " (1111gh)" 같은 케이스까지 제거
                base = re.sub(rf"[\s,/-]*\(?{re.escape(detail)}\)?\s*$", "", base).strip()
                user.address = base

    
        user.save()
        messages.success(request, "개인정보가 저장되었습니다.")
        return redirect("accounts:mypage_profile")

    return render(request, "accounts/mypage/profile.html")


@login_required
def mypage_password_change(request):
    """마이페이지 비밀번호 변경."""
    # ✅ 비밀번호 재확인 세션 체크 (기존 흐름 유지)
    if not request.session.get('is_verified'):
        return redirect(f"{reverse('accounts:profile_auth')}?{urlencode({'next': request.get_full_path()})}")

    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # 비번 변경 후 세션 유지
            messages.success(request, "비밀번호가 변경되었습니다.")
            return redirect("accounts:mypage_password_change")
        else:
            messages.error(request, "비밀번호 변경에 실패했습니다. 입력값을 다시 확인해 주세요.")
    else:
        form = PasswordChangeForm(user=request.user)

    # 입력칸 스타일 클래스 부여
    form.fields["old_password"].widget.attrs.update({
        "class": "field__input input--lg",
        "autocomplete": "current-password",
    })
    form.fields["new_password1"].widget.attrs.update({
        "class": "field__input input--lg",
        "autocomplete": "new-password",
    })
    form.fields["new_password2"].widget.attrs.update({
        "class": "field__input input--lg",
        "autocomplete": "new-password",
    })

    return render(request, "accounts/mypage/password_change.html", {"form": form})


@login_required
def mypage_account_delete(request):
    """마이페이지 회원 탈퇴."""
    if not request.session.get('is_verified'):
        return redirect(f"{reverse('accounts:profile_auth')}?{urlencode({'next': request.get_full_path()})}")

    if request.method == 'POST':
        pw = (request.POST.get('old_password') or '').strip()
        agree = (request.POST.get('agree') or '').strip()

        if not agree:
            messages.error(request, '탈퇴 안내에 동의해 주세요.')
            return redirect('accounts:mypage_account_delete')

        if not pw or not request.user.check_password(pw):
            messages.error(request, '현재 비밀번호가 올바르지 않습니다.')
            return redirect('accounts:mypage_account_delete')

        user = request.user

        # ✅ 15일 재가입 제한 기록
        blocked_until = timezone.now() + timedelta(days=15)
        SignupBlock.objects.create(username=user.username, blocked_until=blocked_until)

        logout(request)  # 세션 정리
        user.delete()

        messages.success(request, '회원 탈퇴가 완료되었습니다.')
        return redirect('main:index')

    return render(request, 'accounts/mypage/account_delete.html')


@require_POST
@login_required
def mypage_password_check(request):
    """비밀번호 확인 AJAX."""
    if not request.session.get('is_verified'):
        return JsonResponse({"ok": False, "matched": False, "error": "auth_required"})

    pw = (request.POST.get("old_password") or "").strip()
    if not pw:
        return JsonResponse({"ok": True, "matched": False})

    matched = request.user.check_password(pw)
    return JsonResponse({"ok": True, "matched": matched})


@require_GET
@login_required
def mypage_check_nickname(request):
    nickname = (request.GET.get('nickname') or '').strip()
    UserModel = get_user_model()

    if not nickname:
        return JsonResponse({'ok': True, 'available': False, 'msg': ''})

    # 본인 닉네임이면 OK
    if nickname == getattr(request.user, "nickname", ""):
        return JsonResponse({'ok': True, 'available': True, 'msg': '현재 사용 중인 닉네임입니다.'})

    exists = UserModel.objects.exclude(pk=request.user.pk).filter(nickname=nickname).exists()
    if exists:
        return JsonResponse({'ok': True, 'available': False, 'msg': '이미 사용 중인 닉네임입니다.'})
    return JsonResponse({'ok': True, 'available': True, 'msg': '사용 가능한 닉네임입니다.'})


@require_POST
@login_required
def mypage_send_email_code(request):
    email = (request.POST.get("email") or "").strip()
    if not email:
        return JsonResponse({"ok": False, "error": "이메일을 입력해 주세요."})

    UserModel = get_user_model()

    # 현재 이메일이면 인증 생략 가능(저장해도 변경 없으니까)
    if email == (request.user.email or "").strip():
        return JsonResponse({"ok": True, "same": True})

    # 본인 제외 중복 체크
    if UserModel.objects.exclude(pk=request.user.pk).filter(email=email).exists():
        return JsonResponse({"ok": False, "error": "이미 사용 중인 이메일입니다."})

    code = f"{random.randint(0, 999999):06d}"

    request.session["email_change_code"] = code
    request.session["email_change_target"] = email
    request.session["email_change_tries"] = 0
    request.session["email_change_sent_at"] = int(timezone.now().timestamp())

    subject = "[mompjt] 이메일 변경 인증번호"
    message = f"인증번호는 {code} 입니다."

    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
    except Exception as e:
        print("mypage_send_email_code mail error:", e)
        return JsonResponse({"ok": False, "error": "메일 발송에 실패했습니다."})

    return JsonResponse({"ok": True})


@require_POST
@login_required
def mypage_verify_email_code(request):
    email = (request.POST.get("email") or "").strip()
    code = (request.POST.get("code") or "").strip()

    if not email or not code:
        return JsonResponse({"ok": False, "error": "이메일과 인증번호를 입력해 주세요."})

    target = (request.session.get("email_change_target") or "").strip()
    saved = (request.session.get("email_change_code") or "").strip()
    tries = int(request.session.get("email_change_tries") or 0)

    if tries >= 5:
        return JsonResponse({"ok": False, "error": "인증 시도 횟수를 초과했습니다. 다시 인증번호를 발급해 주세요."})

    if email != target:
        request.session["email_change_tries"] = tries + 1
        return JsonResponse({"ok": False, "error": "인증 대상 이메일이 일치하지 않습니다. 다시 발급해 주세요."})

    if code != saved:
        request.session["email_change_tries"] = tries + 1
        return JsonResponse({"ok": False, "error": "인증번호가 올바르지 않습니다."})

    # ✅ 인증 완료: 저장 시 이 값과 email 입력이 같아야 실제 반영
    request.session["verified_email_change"] = email
    return JsonResponse({"ok": True})


@login_required
def mypage_my_posts(request):
    """사용자가 작성한 글 목록 조회"""
    # ✅ 비밀번호 재확인 세션 체크
    if not request.session.get('is_verified'):
        return redirect(f"{reverse('accounts:profile_auth')}?{urlencode({'next': request.get_full_path()})}")
    
    user = request.user
    
    # 자유게시판 글, 요리레시피 글 조회
    from board.models import FreePost
    from recipes.models import RecipePost
    
    free_posts = FreePost.objects.filter(author=user).order_by('-created_at')
    recipes = RecipePost.objects.filter(author=user).order_by('-created_at')
    
    context = {
        'free_posts': free_posts,
        'recipes': recipes,
    }
    
    return render(request, 'accounts/mypage/my_posts.html', context)


@login_required
def mypage_grade_exp(request):
    """사용자의 등급/경험치 정보 표시"""
    from .constants import GRADE_REQUIREMENTS, GRADE_ORDER
    
    user = request.user
    current_exp = user.point
    current_grade_idx = GRADE_ORDER.index(user.grade)
    
    # 다음 등급 정보 계산
    if current_grade_idx < len(GRADE_ORDER) - 1:
        next_grade = GRADE_ORDER[current_grade_idx + 1]
        next_grade_exp = GRADE_REQUIREMENTS[next_grade]
        exp_to_next = max(0, next_grade_exp - current_exp)
        progress_percent = (current_exp - GRADE_REQUIREMENTS[user.grade]) / (next_grade_exp - GRADE_REQUIREMENTS[user.grade]) * 100
    else:
        # 최고 등급인 경우
        next_grade = None
        next_grade_exp = None
        exp_to_next = 0
        progress_percent = 100
    
    # 전체 사용자 수와 현재 사용자의 랭킹
    from django.db.models import Count, Q
    total_users = User.objects.filter(is_active=True).count()
    
    # 현재 등급 사용자의 순위 (같은 등급 내에서 경험치 순)
    same_grade_users = User.objects.filter(grade=user.grade, is_active=True).order_by('-point')
    user_rank_in_grade = list(same_grade_users.values_list('id', flat=True)).index(user.id) + 1
    
    # 전체 등급별 사용자 수
    grade_stats = {}
    grade_display_names = {
        'start': '시작 (Starter)',
        'join': '참여 (Participant)',
        'talk': '소통 (Communicator)',
        'empathy': '공감 (Empath)',
        'core': '핵심 (Core Member)',
    }
    
    grade_list = []
    for grade_code in GRADE_ORDER:
        count = User.objects.filter(grade=grade_code, is_active=True).count()
        grade_stats[grade_code] = count
        grade_list.append({
            'code': grade_code,
            'name': grade_display_names[grade_code],
            'exp_required': GRADE_REQUIREMENTS[grade_code],
            'user_count': count,
            'is_current': grade_code == user.grade,
        })
    
    context = {
        'current_exp': current_exp,
        'current_grade': user.grade,
        'next_grade': next_grade,
        'next_grade_exp': next_grade_exp,
        'exp_to_next': exp_to_next,
        'progress_percent': progress_percent,
        'total_users': total_users,
        'user_rank_in_grade': user_rank_in_grade,
        'grade_stats': grade_stats,
        'grade_list': grade_list,
    }
    
    return render(request, 'accounts/mypage/grade_exp.html', context)


@staff_member_required
def admin_dashboard(request):
    """관리자 통계 대시보드"""
    today = timezone.localdate()

    # 기간 필터
    range_param = request.GET.get('range', '7')
    start_date = today - timedelta(days=6)
    end_date = today

    if range_param == 'today':
        start_date = end_date = today
    elif range_param == '30':
        start_date = today - timedelta(days=29)
    elif range_param == 'custom':
        # YYYY-MM-DD 입력값 처리
        try:
            start_str = request.GET.get('start')
            end_str = request.GET.get('end')
            if start_str:
                start_date = timezone.datetime.strptime(start_str, '%Y-%m-%d').date()
            if end_str:
                end_date = timezone.datetime.strptime(end_str, '%Y-%m-%d').date()
            if start_date > end_date:
                start_date, end_date = end_date, start_date
        except Exception:
            start_date = today - timedelta(days=6)
            end_date = today

    date_range = (start_date, end_date)
    days_count = (end_date - start_date).days + 1
    prev_end = start_date - timedelta(days=1)
    prev_start = prev_end - timedelta(days=days_count - 1)
    prev_range = (prev_start, prev_end)

    def pct_change(curr, prev):
        if prev == 0:
            return None if curr == 0 else 100.0
        return ((curr - prev) / prev) * 100.0

    # 데이터 소스
    from board.models import FreePost, FleaItem, FleaReport
    from recipes.models import RecipePost

    # KPI
    new_signups_today = User.objects.filter(date_joined__date=today).count()
    new_signups_prev = User.objects.filter(date_joined__date=today - timedelta(days=1)).count()
    signups_today_list = list(
        User.objects.filter(date_joined__date=today)
        .order_by('-date_joined')
        .values('id', 'username', 'nickname', 'email', 'date_joined')
    )
    active_signups = User.objects.filter(date_joined__date__range=date_range).count()
    active_signups_prev = User.objects.filter(date_joined__date__range=prev_range).count()
    signups_range_list = list(
        User.objects.filter(date_joined__date__range=date_range)
        .order_by('-date_joined')
        .values('id', 'username', 'nickname', 'email', 'date_joined')
    )

    free_posts_today = FreePost.objects.filter(created_at__date=today).count()
    recipe_posts_today = RecipePost.objects.filter(created_at__date=today).count()
    total_posts_range = FreePost.objects.filter(created_at__date__range=date_range).count() + RecipePost.objects.filter(created_at__date__range=date_range).count()
    total_posts_prev = FreePost.objects.filter(created_at__date__range=prev_range).count() + RecipePost.objects.filter(created_at__date__range=prev_range).count()

    # 상세 리스트 데이터
    free_posts_today_list = list(
        FreePost.objects.select_related('author')
        .filter(created_at__date=today)
        .order_by('-created_at')
    )
    recipe_posts_today_list = list(
        RecipePost.objects.select_related('author')
        .filter(created_at__date=today)
        .order_by('-created_at')
    )
    # 기간 내 자유/레시피 게시글 합산 리스트 (작성일 역순)
    free_range = list(
        FreePost.objects.select_related('author')
        .filter(created_at__date__range=date_range)
        .order_by('-created_at')
    )
    for p in free_range:
        p.board_type = 'free'
    recipe_range = list(
        RecipePost.objects.select_related('author')
        .filter(created_at__date__range=date_range)
        .order_by('-created_at')
    )
    for p in recipe_range:
        p.board_type = 'recipe'
    total_posts_range_list = sorted(free_range + recipe_range, key=lambda x: x.created_at, reverse=True)

    fleas_range = FleaItem.objects.filter(created_at__date__range=date_range)
    fleas_prev = FleaItem.objects.filter(created_at__date__range=prev_range)
    status_counts_raw = fleas_range.values('status').annotate(c=Count('id'))
    status_counts = {item['status']: item['c'] for item in status_counts_raw}
    pending_count = status_counts.get('selling', 0)
    in_progress_count = status_counts.get('reserved', 0)
    done_count = status_counts.get('sold', 0)

    done_count_prev = fleas_prev.filter(status='sold').count()

    reports_range = FleaReport.objects.filter(created_at__date__range=date_range)
    reports_prev = FleaReport.objects.filter(created_at__date__range=prev_range)
    reports_today = FleaReport.objects.filter(created_at__date=today).count()
    flea_reports_today_list = list(
        FleaReport.objects.select_related('flea_item', 'reporter')
        .filter(created_at__date=today)
        .order_by('-created_at')
    )
    reports_pending = reports_range.filter(status='pending').count()
    reports_resolved = reports_range.filter(status='resolved').count()
    reports_total_range = reports_range.count()
    reports_total_prev = reports_prev.count()

    # 벼룩시장 상태 리스트 (상태명 매핑)
    status_map = {'selling': 'pending', 'reserved': 'in_progress', 'sold': 'done'}
    hotdeal_raw = list(
        fleas_range.select_related('author')
        .order_by('-created_at')
    )
    hotdeal_list = []
    for item in hotdeal_raw:
        mapped = status_map.get(item.status, item.status)
        item.status = mapped
        hotdeal_list.append(item)

    # 일자별 추이
    signups_daily = (
        User.objects.filter(date_joined__date__range=date_range)
        .annotate(day=TruncDate('date_joined'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    free_daily = (
        FreePost.objects.filter(created_at__date__range=date_range)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    recipe_daily = (
        RecipePost.objects.filter(created_at__date__range=date_range)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    done_daily = (
        FleaItem.objects.filter(created_at__date__range=date_range, status='sold')
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    report_daily = (
        FleaReport.objects.filter(created_at__date__range=date_range)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    def max_min(series):
        if not series:
            return {'max': None, 'min': None}
        values = [row['count'] for row in series]
        return {'max': max(values), 'min': min(values)}

    # 최신 목록
    latest_free = FreePost.objects.order_by('-created_at')[:20]
    latest_recipe = RecipePost.objects.order_by('-created_at')[:20]
    latest_reports = FleaReport.objects.select_related('flea_item', 'reporter').order_by('-created_at')[:20]

    # 상태 분포(막대/도넛용 데이터)
    status_distribution = [
        {'label': '판매중', 'value': pending_count},
        {'label': '예약중', 'value': in_progress_count},
        {'label': '판매완료', 'value': done_count},
    ]

    context = {
        'today': today,
        'start_date': start_date,
        'end_date': end_date,
        'range_param': range_param,
        'kpi': {
            'new_signups_today': new_signups_today,
            'new_signups_prev': new_signups_prev,
            'new_signups_change': pct_change(new_signups_today, new_signups_prev),
            'active_signups': active_signups,
            'active_signups_prev': active_signups_prev,
            'active_signups_change': pct_change(active_signups, active_signups_prev),
            'free_posts_today': free_posts_today,
            'recipe_posts_today': recipe_posts_today,
            'total_posts_range': total_posts_range,
            'total_posts_prev': total_posts_prev,
            'total_posts_change': pct_change(total_posts_range, total_posts_prev),
            'pending_count': pending_count,
            'in_progress_count': in_progress_count,
            'done_count': done_count,
            'done_prev': done_count_prev,
            'done_change': pct_change(done_count, done_count_prev),
            'reports_today': reports_today,
            'reports_range': reports_total_range,
            'reports_change': pct_change(reports_total_range, reports_total_prev),
            'reports_pending': reports_pending,
            'reports_resolved': reports_resolved,
        },
        'signups_today_list': signups_today_list,
        'signups_range_list': signups_range_list,
        'free_posts_today_list': free_posts_today_list,
        'recipe_posts_today_list': recipe_posts_today_list,
        'total_posts_range_list': total_posts_range_list,
        'flea_reports_today_list': flea_reports_today_list,
        'hotdeal_list': hotdeal_list,
        'charts': {
            'signups_daily': list(signups_daily),
            'free_daily': list(free_daily),
            'recipe_daily': list(recipe_daily),
            'done_daily': list(done_daily),
            'report_daily': list(report_daily),
            'status_distribution': status_distribution,
            'maxmin': {
                'signups': max_min(list(signups_daily)),
                'free': max_min(list(free_daily)),
                'recipe': max_min(list(recipe_daily)),
                'done': max_min(list(done_daily)),
                'report': max_min(list(report_daily)),
            },
        },
        'latest_free': latest_free,
        'latest_recipe': latest_recipe,
        'latest_reports': latest_reports,
    }

    return render(request, 'accounts/admin_dashboard.html', context)


@staff_member_required
@require_POST
def resolve_flea_report(request, report_id):
    report = get_object_or_404(FleaReport, pk=report_id)
    report.status = 'resolved'
    report.resolved_at = timezone.now()
    report.save(update_fields=['status', 'resolved_at', 'updated_at'])
    return redirect('accounts:admin_dashboard')


@staff_member_required
@require_POST
def update_flea_report_status(request, report_id, status):
    report = get_object_or_404(FleaReport, pk=report_id)
    valid_status = ['pending', 'in_progress', 'resolved']
    if status not in valid_status:
        return redirect('accounts:admin_dashboard')

    report.status = status
    report.resolved_at = timezone.now() if status == 'resolved' else None
    report.save(update_fields=['status', 'resolved_at', 'updated_at'])
    return redirect('accounts:admin_dashboard')


# 0105 성훈=======================================================================================
