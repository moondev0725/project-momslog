import os
import django
import re

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mompjt.settings")
django.setup()

from accounts.models import User

def run():
    qs = User.objects.exclude(address__isnull=True).exclude(address="") \
                     .exclude(address_detail__isnull=True).exclude(address_detail="")

    updated = 0
    for u in qs:
        base = (u.address or "").strip()
        detail = (u.address_detail or "").strip()
        if not base or not detail:
            continue

        cleaned = re.sub(rf"[\s,/-]*\(?{re.escape(detail)}\)?\s*$", "", base).strip()
        if cleaned != base:
            u.address = cleaned
            u.save(update_fields=["address"])
            updated += 1

    print(f"✅ 완료: address 정리 유저 수 = {updated}")

if __name__ == "__main__":
    run()
