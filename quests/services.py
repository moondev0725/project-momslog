import random
from datetime import date
from datetime import timedelta
from django.utils import timezone
from .models import DailyQuest

QUEST_POOL = [
    "아이에게 질문 하나 해보기",
    "오늘 나를 위해 5분 쉬어보기",
    "게시글 하나 읽고 공감 눌러보기",
    "따뜻한 물 한 잔 마시기",
    "아이 사진 한 장 정리하기",
]

def get_or_create_today_quest(user):
    today = date.today()
    quest, created = DailyQuest.objects.get_or_create(
        user=user,
        date=today,
        defaults={"content": random.choice(QUEST_POOL)}
    )
    return quest

def calculate_streak(user):
    today = timezone.localdate()
    streak = 0

    day = today
    while True:
        q = DailyQuest.objects.filter(
            user=user,
            date=day,
            completed=True
        ).first()

        if not q:
            break

        streak += 1
        day -= timedelta(days=1)

    return streak