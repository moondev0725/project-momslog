# accounts/services.py
from .constants import GRADE_ORDER, GRADE_REQUIREMENTS, GRADE_CHOICES


def _clean_label(s: str) -> str:
    # 줄바꿈/탭/연속공백을 전부 1칸 공백으로 정리
    return " ".join((s or "").split())


def get_grade_progress(user):
    """
    user 기반으로 grade_progress dict 반환
    (context_processor / AJAX 모두에서 재사용)
    """
    grade_label_map = dict(GRADE_CHOICES)

    current_grade = user.grade
    point = user.point or 0

    current_idx = GRADE_ORDER.index(current_grade)

    next_grade = (
        GRADE_ORDER[current_idx + 1]
        if current_idx < len(GRADE_ORDER) - 1
        else None
    )

    current_need = GRADE_REQUIREMENTS[current_grade]
    next_need = GRADE_REQUIREMENTS[next_grade] if next_grade else current_need

    span = max(1, next_need - current_need)
    progress_percent = int(min(100, max(0, (point - current_need) / span * 100)))

    remaining = max(0, next_need - point) if next_grade else 0

    current_label = _clean_label(grade_label_map.get(current_grade, current_grade))
    next_label = _clean_label(grade_label_map.get(next_grade, next_grade)) if next_grade else None

    return {
        "point": point,
        "current_label": current_label,
        "next_label": next_label,
        "progress_percent": progress_percent,
        "remaining": remaining,
        "is_max": next_grade is None,
    }
