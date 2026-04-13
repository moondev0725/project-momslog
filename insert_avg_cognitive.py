"""
인지발달 평균 데이터 삽입 스크립트
python manage.py shell < insert_avg_cognitive.py
"""

from django.contrib.auth.models import User
from board.models import ParentingInfo

# 평균 데이터용 계정 생성 또는 가져오기
avg_user, created = User.objects.get_or_create(
    username='average_data',
    defaults={
        'email': 'average@system.com',
        'is_active': False  # 로그인 불가능하게
    }
)

if created:
    print("평균 데이터용 계정 생성됨: average_data")
else:
    print("기존 평균 데이터용 계정 사용: average_data")

# 기존 평균 인지발달 데이터 삭제
ParentingInfo.objects.filter(
    author=avg_user,
    category='development',
    title__contains='[평균]'
).delete()

# 월령별 인지발달 평균 데이터
cognitive_avg_data = {
    1: (8, "소리와 빛에 반응하며 감각을 통해 세상을 인식합니다"),
    2: (12, "얼굴과 소리를 구분하기 시작합니다"),
    3: (18, "익숙한 사람을 알아보고 자극에 반응합니다"),
    4: (26, "물건을 주의 깊게 바라보고 원인·결과를 탐색합니다"),
    5: (34, "물건을 입에 넣으며 탐색하고 반복 행동에 흥미를 보입니다"),
    6: (42, "숨겨진 물건에 관심을 보이고 주변을 관찰합니다"),
    7: (52, "물건의 기능 차이를 인식하기 시작합니다"),
    8: (60, "간단한 행동을 따라 하며 기억력이 발달합니다"),
    9: (70, "이름을 인식하고 간단한 지시를 이해합니다"),
    10: (80, "문제 해결을 시도하고 목적 있는 행동을 합니다"),
    11: (90, "물건의 용도를 이해하고 선택 행동이 늘어납니다"),
    12: (100, "간단한 말의 의미를 이해하고 사고 능력이 확장됩니다"),
}

# 신체발달 평균 데이터 (기존)
physical_avg_data = {
    1: (10, "팔다리를 반사적으로 움직이고 엎드리면 고개를 잠깐 듭니다"),
    2: (15, "고개 들기가 조금 안정되고 움직임이 부드러워집니다"),
    3: (22, "엎드린 상태에서 팔로 몸을 지탱합니다"),
    4: (30, "목 가누기가 완성되고 손을 뻗어 물건을 잡으려 합니다"),
    5: (38, "뒤집기를 시도하고 몸통 움직임이 활발해집니다"),
    6: (46, "혼자 앉을 수 있어 신체발달의 큰 전환점이 됩니다"),
    7: (55, "기거나 이동을 시작합니다"),
    8: (63, "안정적으로 앉고 이동이 활발해집니다"),
    9: (72, "붙잡고 서며 손가락으로 작은 물건을 집습니다"),
    10: (82, "가구를 잡고 옆으로 이동합니다"),
    11: (90, "잠깐 혼자 서거나 첫 걸음을 시도합니다"),
    12: (100, "혼자 걷기 시작하며 영아기 신체발달 기준에 도달합니다"),
}

# 데이터 삽입
count = 0
for month, (score, desc) in cognitive_avg_data.items():
    physical_score = physical_avg_data.get(month, (0, ""))[0]
    
    ParentingInfo.objects.create(
        author=avg_user,
        category='development',
        title=f'[평균] {month}개월 발달 기준',
        content=f'인지발달: {desc}',
        month_age=month,
        physical_score=physical_score,
        cognitive_score=score,
        language_score=0,  # 추후 추가
        social_score=0,    # 추후 추가
    )
    count += 1
    print(f"{month}개월 평균 데이터 삽입 완료 (인지: {score}점, 신체: {physical_score}점)")

print(f"\n총 {count}개 월령 평균 데이터 삽입 완료!")
print("views.py에서 이 데이터를 사용하도록 수정하세요.")
