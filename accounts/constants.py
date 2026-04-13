# accounts/constants.py


# 등급 코드(문자열) - 기존 grade 필드 그대로 사용
GRADE_CHOICES = [
    ("start", "🌱 시작"),
    ("join", "✍ 참여"),
    ("talk", "💬 소통"),
    ("empathy", "🤝 공감"),
    ("core", "⭐ 핵심"),
]

# 포인트 기준 (원하면 숫자만 나중에 조정)
GRADE_REQUIREMENTS = {
    "start": 0,
    "join": 50,
    "talk": 150,
    "empathy": 300,
    "core": 600,
}

# 정렬용
GRADE_ORDER = ["start", "join", "talk", "empathy", "core"]
