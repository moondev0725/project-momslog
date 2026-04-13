from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from board.models import ParentingInfo
from accounts.models import User


class Command(BaseCommand):
    help = "육아가이드 > 월령별 발달 더미 데이터 생성 (static 이미지 경로 사용)"

    def handle(self, *args, **options):
        COUNT = 100

        # 작성자
        user = User.objects.first()
        if not user:
            user = User.objects.create_user(username="dummy_user", password="1234")

        # 내용 문장 풀
        contents_pool = [
            "요즘 목을 조금씩 가누기 시작했어요",
            "소리가 나면 고개를 돌려 찾으려고 해요",
            "손을 쥐었다 폈다 하면서 움직임이 많아졌어요",
            "사람 얼굴을 유심히 바라보는 시간이 늘었어요",
            "옹알이가 많아지고 반응도 다양해졌어요",
            "장난감을 잡으려고 손을 뻗는 모습이 보여요",
            "배밀이를 시도하면서 움직이려는 의지가 생겼어요",
            "뒤집기를 하려고 몸을 옆으로 돌리려 해요",
            "앉으려고 상체에 힘을 주는 모습이 보이네요",
            "낯선 사람을 보면 잠깐 멈칫하는 반응이 있어요",
            "익숙한 목소리에 웃거나 소리로 반응해요",
            "손에 잡힌 물건을 입으로 가져가 탐색해요",
            "두 손을 함께 쓰는 동작이 점점 자연스러워져요",
            "손뼉 치는 흉내를 내거나 따라 하려는 모습이 있어요",
            "안돼 같은 말에 멈칫하는 반응이 나타나요",
            "원하는 것을 손짓이나 몸짓으로 표현하려고 해요",
            "기어다니며 주변을 탐색하려는 행동이 늘었어요",
            "간단한 놀이에 흥미를 보이며 집중 시간이 길어졌어요",
            "감정 표현이 다양해지고 웃음이 많아졌어요",
            "주변 환경에 대한 호기심이 눈에 띄게 늘었어요",
        ]

        # static 이미지 경로 풀
        image_pool = [
            "images/dev/01.jpg",
            "images/dev/02.jpg",
            "images/dev/03.jpg",
            "images/dev/04.jpg",
            "images/dev/05.jpg",
            "images/dev/06.jpg",
            "images/dev/07.jpg",
            "images/dev/08.jpg",
            "images/dev/09.jpg",
            "images/dev/10.jpg",
        ]

        for _ in range(COUNT):
            month = random.randint(1, 12)

            ParentingInfo.objects.create(
                title=f"{month}개월 아기에요",
                content=random.choice(contents_pool),
                category="development",
                author=user,
                created_at=timezone.now() - timedelta(days=random.randint(0, 120)),
                views=random.randint(10, 1500),

                month_age=month,
                physical_score=random.randint(1, 100),
                cognitive_score=random.randint(1, 100),
                language_score=random.randint(1, 100),
                social_score=random.randint(1, 100),

                image=random.choice(image_pool),  # ⭐ 핵심
            )

        self.stdout.write(self.style.SUCCESS("✅ 월령별 발달 게시글 100개 생성 완료"))
