from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .services import get_or_create_today_quest, calculate_streak
from accounts.points import add_point
from accounts.services import get_grade_progress


@login_required
@require_POST
def complete_today(request):
    quest = get_or_create_today_quest(request.user)

    if quest.completed or quest.skipped:
        return JsonResponse({"status": "already_done"})

    # ✅ 변경 전 등급/라벨 저장(중요!)
    prev_grade = request.user.grade
    prev_gp = get_grade_progress(request.user)
    prev_label = prev_gp["current_label"]

    quest.completed = True
    quest.streak = calculate_streak(request.user)
    quest.save(update_fields=["completed", "streak"])

    add_point(request.user, "quest_complete")
    

    # 🔥 streak 보너스 (선택)
    if quest.streak in (3, 7, 14):
        add_point(request.user, 10)

    # ✅ 최신값 다시 로드
    request.user.refresh_from_db()

    gp = get_grade_progress(request.user)

    # ✅ 문구(템플릿과 동일)
    if gp["is_max"]:
        remaining_text = "최고 등급이에요 ⭐"
    else:
        remaining_text = f'다음 {gp["next_label"]}까지 <b>{gp["remaining"]}</b>P 남았어요'

    # ✅ 등급 업 감지
    leveled_up = (prev_grade != request.user.grade)

    return JsonResponse({
        "status": "ok",
        "point": gp["point"],
        "grade": request.user.grade,
        "streak": quest.streak,
        "progress_percent": gp["progress_percent"],
        "remaining_text": remaining_text,

        # 🔥 등급업 연출용
        "leveled_up": leveled_up,
        "prev_grade": prev_grade,
        "prev_label": prev_label,
        "new_label": gp["current_label"],
    })


@login_required
def skip_today(request):
    if request.method != "POST":
        return redirect(request.META.get("HTTP_REFERER", "/"))

    quest = get_or_create_today_quest(request.user)

    if quest.completed or quest.skipped:
        return redirect(request.META.get("HTTP_REFERER", "/"))

    quest.skipped = True
    quest.save(update_fields=["skipped"])
    return redirect(request.META.get("HTTP_REFERER", "/"))
