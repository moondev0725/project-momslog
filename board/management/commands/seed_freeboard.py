import csv
from pathlib import Path

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from board.models import FreePost, FreeComment


class Command(BaseCommand):
    help = "Seed FreePost/FreeComment from Mockaroo CSV"

    def add_arguments(self, parser):
        parser.add_argument("--posts", type=str, default="posts.csv")
        parser.add_argument("--comments", type=str, default="comments.csv")

    def handle(self, *args, **options):
        posts_csv = Path(options["posts"])
        comments_csv = Path(options["comments"])

        if not posts_csv.exists():
            self.stderr.write(self.style.ERROR(f"posts csv not found: {posts_csv.resolve()}"))
            return
        if not comments_csv.exists():
            self.stderr.write(self.style.ERROR(f"comments csv not found: {comments_csv.resolve()}"))
            return

        User = get_user_model()

        # 유저 2명 확보 (nickname UNIQUE 대응)
        User = get_user_model()

        def ensure_user(username: str, email: str, nickname: str):
            # 1) username으로 먼저 찾고
            u = User.objects.filter(username=username).first()
            if u:
                # nickname 비어있으면 채워주기 (혹시 이전 데이터가 이상한 경우)
                if hasattr(u, "nickname") and (not getattr(u, "nickname", None)):
                    u.nickname = nickname
                    u.save(update_fields=["nickname"])
                if not u.has_usable_password():
                    u.set_password("1234")
                    u.save()
                return u

            # 2) 없으면 nickname 충돌 피해서 생성 (이미 누가 쓰고 있으면 뒤에 숫자 붙임)
            final_nick = nickname
            if hasattr(User, "nickname"):
                i = 2
                while User.objects.filter(nickname=final_nick).exists():
                    final_nick = f"{nickname}{i}"
                    i += 1

            create_kwargs = {"username": username, "email": email}
            if hasattr(User, "nickname"):
                create_kwargs["nickname"] = final_nick

            u = User.objects.create(**create_kwargs)
            u.set_password("1234")
            u.save()
            return u

        u1 = ensure_user("user1", "user1@test.com", "유저1")
        u2 = ensure_user("user2", "user2@test.com", "유저2")

        user_map = {1: u1, 2: u2}


        # 게시글 생성
        created_posts = 0
        with posts_csv.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                author_id = int((row.get("author_id") or "1").strip() or "1")

                FreePost.objects.create(
                    category=(row.get("category") or "mom").strip(),
                    title=(row.get("title") or "").strip()[:200],
                    content=(row.get("content") or "").strip(),
                    author=user_map.get(author_id, u1),
                    is_anonymous=str(row.get("is_anonymous", "")).lower() in ["true", "1", "yes", "y"],
                    views=int(float(row.get("views", 0) or 0)),
                )
                created_posts += 1

        # 댓글 생성: 모든 글에 최소 1개씩 + 남는 건 랜덤 분배
        created_comments = 0

        posts = list(FreePost.objects.all())
        if not posts:
            self.stdout.write(self.style.WARNING("⚠️ No posts found. Skip creating comments."))
        else:
            import random

            # comments.csv에서 content만 뽑아 리스트로 만들기
            comment_texts = []
            with comments_csv.open("r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    txt = (row.get("content") or "").strip()
                    if txt:
                        comment_texts.append((int((row.get("author_id") or "1").strip() or "1"), txt))

            if not comment_texts:
                self.stdout.write(self.style.WARNING("⚠️ No comment texts in CSV."))
            else:
                # 1) 모든 글에 1개씩 (가능한 범위 내)
                random.shuffle(posts)
                for i, post in enumerate(posts):
                    if i >= len(comment_texts):
                        break
                    author_id, txt = comment_texts[i]
                    FreeComment.objects.create(
                        post=post,
                        author=user_map.get(author_id, u1),
                        content=txt,
                    )
                    created_comments += 1

                # 2) 남은 댓글 텍스트는 랜덤 글에 추가
                for author_id, txt in comment_texts[len(posts):]:
                    post = random.choice(posts)
                    FreeComment.objects.create(
                        post=post,
                        author=user_map.get(author_id, u1),
                        content=txt,
                    )
                    created_comments += 1



        self.stdout.write(self.style.SUCCESS(f"✅ posts created: {created_posts}"))
        self.stdout.write(self.style.SUCCESS(f"✅ comments created: {created_comments}"))
        self.stdout.write(self.style.SUCCESS("✅ done"))
