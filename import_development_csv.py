import csv
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mompjt.settings")
django.setup()

from accounts.models import User
from board.models import ParentingInfo, ParentingImage

CSV_PATH = os.path.join(os.getcwd(), "development_month_guide.csv")

u = User.objects.first()
if not u:
    u = User.objects.create_user(username="dummy_user", password="1234")

created = 0

with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        post = ParentingInfo.objects.create(
            title=row["title"],
            content=row["content"],
            category="development",
            author=u,
            month_age=int(row["month"]),
            physical_score=int(row["physical_score"]),
            cognitive_score=int(row["cognitive_score"]),
            language_score=int(row["language_score"]),
            social_score=int(row["social_score"]),
        )

        fname = os.path.basename(row["image"])
        ParentingImage.objects.create(
            post=post,
            image=f"parenting/{fname}",
            order=0,
        )

        created += 1

print("DONE:", created)
