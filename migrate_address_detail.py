import os
import django

# 🔽 settings.py 위치 지정 (지금 네 프로젝트 구조 기준)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mompjt.settings")
django.setup()

from accounts.models import User

def run():
    users = User.objects.exclude(address__isnull=True).exclude(address="")

    updated = 0
    skipped = 0

    for u in users:
        # 이미 상세주소가 있는 유저는 건너뜀
        if u.address_detail:
            skipped += 1
            continue

        # 기존 address 값을 그대로 복사
        u.address_detail = u.address
        u.save(update_fields=["address_detail"])
        updated += 1

    print("===== 결과 =====")
    print("상세주소 채운 유저:", updated)
    print("이미 있던 유저:", skipped)
    print("총 검사 유저:", users.count())

if __name__ == "__main__":
    run()
