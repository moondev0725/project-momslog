import csv
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from board.models import FleaItem

class Command(BaseCommand):
    help = "Import FleaItem rows from a CSV file (author auto-filled)."

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str, help="Path to CSV file")
        parser.add_argument("--author", type=str, default="", help="username to use as author (optional)")

    def handle(self, *args, **options):
        csv_path = options["csv_path"]
        author_username = options["author"].strip()

        User = get_user_model()

        # 1) author 결정: --author 있으면 그 유저 / 없으면 첫 유저 / 그것도 없으면 superuser 생성 유도
        author = None
        if author_username:
            author = User.objects.filter(username=author_username).first()
            if not author:
                self.stderr.write(self.style.ERROR(f"User not found: {author_username}"))
                return
        else:
            author = User.objects.order_by("id").first()
            if not author:
                self.stderr.write(self.style.ERROR(
                    "No users in DB. Create a user first (admin or normal), then rerun."
                ))
                return

        created = 0
        skipped = 0

        # 2) CSV 읽기 (UTF-8, BOM 방지용 utf-8-sig)
        with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            required = ["title", "price", "description", "location_address", "latitude", "longitude", "image"]
            missing_cols = [c for c in required if c not in reader.fieldnames]
            if missing_cols:
                self.stderr.write(self.style.ERROR(f"Missing columns: {missing_cols}"))
                self.stderr.write(self.style.ERROR(f"CSV columns are: {reader.fieldnames}"))
                return

            for i, row in enumerate(reader, start=1):
                title = (row.get("title") or "").strip()
                description = (row.get("description") or "").strip()
                image = (row.get("image") or "").strip() or None
                location_address = (row.get("location_address") or "").strip() or None

                # price
                try:
                    price = int(float(row.get("price") or 0))
                except ValueError:
                    skipped += 1
                    continue

                # lat/lng (빈값이면 None)
                def parse_decimal(val):
                    val = (val or "").strip()
                    if not val:
                        return None
                    try:
                        return Decimal(val)
                    except (InvalidOperation, ValueError):
                        return None

                lat = parse_decimal(row.get("latitude"))
                lng = parse_decimal(row.get("longitude"))

                # title 필수 방어
                if not title:
                    title = f"상품 {i}"

                FleaItem.objects.create(
                    title=title,
                    description=description,
                    price=price,
                    location_address=location_address,
                    latitude=lat,
                    longitude=lng,
                    image=image,     # ImageField는 "flea/01.jpg" 같은 경로 문자열도 저장 가능
                    author=author
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Done. created={created}, skipped={skipped}, author={author.username}"))
