# quests/context_processors.py

from quests.services import get_or_create_today_quest
from accounts.services import get_grade_progress


def today_quest(request):
    """
    전역 context processor
    - today_quest: 오늘의 퀘스트
    - grade_progress: 포인트 / 등급 진행바 정보
    """

    # 비로그인 상태
    if not request.user.is_authenticated:
        return {
            "today_quest": None,
            "grade_progress": None,
        }

    user = request.user

    # 오늘의 퀘스트
    quest = get_or_create_today_quest(user)

    # 등급 진행 정보(services에서 계산)
    grade_progress = get_grade_progress(user)

    return {
        "today_quest": quest,
        "grade_progress": grade_progress,
    }
