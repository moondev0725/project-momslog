import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mompjt.settings")
django.setup()

from accounts.models import User

def run():
    # address_detail이 있고, address와 완전히 같은 경우만 비움 (버전1로 복사된 케이스)
    qs = User.objects.exclude(address_detail__isnull=True).exclude(address_detail="")

    updated = 0
    for u in qs:
        if (u.address or "").strip() == (u.address_detail or "").strip():
            u.address_detail = ""
            u.save(update_fields=["address_detail"])
            updated += 1

    print(f"✅ 완료: address_detail 비운 유저 수 = {updated}")

if __name__ == "__main__":
    run()
