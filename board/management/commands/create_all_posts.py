from django.core.management.base import BaseCommand
from board.models import FreePost, HotDeal, ParentingInfo, Notice, FleaItem
from accounts.models import User
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = '모든 게시판에 샘플 데이터 20개씩 생성합니다'

    def handle(self, *args, **options):
        # 기본 사용자 생성
        try:
            user = User.objects.first()
            if not user:
                user = User.objects.create_user(username='sample_user', password='1234')
        except:
            user = User.objects.first()

        self.stdout.write("=" * 60)
        self.stdout.write("게시판별 샘플 데이터 생성 시작")
        self.stdout.write("=" * 60)

        # 1. 자유게시판 (FreePost) - 추가 20개
        self.create_free_posts(user)

        # 2. 핫딜공유 (HotDeal) - 20개
        self.create_hotdeal_posts(user)

        # 3. 육아정보 (ParentingInfo) - 20개
        self.create_parenting_posts(user)

        # 4. 공지사항 (Notice) - 20개
        self.create_notice_posts(user)

        # 5. 벼룩시장 (FleaItem) - 20개
        self.create_flea_items(user)

        self.stdout.write(self.style.SUCCESS("\n✓ 모든 게시판에 샘플 데이터 생성 완료!"))

    def create_free_posts(self, user):
        """자유게시판 20개"""
        titles = [
            "우리 아이 처음 기저귀 갈았을 때 이상했어요",
            "신생아 수유 팁 공유합니다",
            "아기 피부 관리 정말 힘들어요",
            "이유식 시작하려는데 언제부터?",
            "아이 옷 크기 측정 방법",
            "분유 선택 기준이 뭐예요?",
            "수면 교육 성공 후기",
            "아이 돌 촬영 어디서 했어요?",
            "예방접종 스케줄 정리했어요",
            "아기 떼쓰기 대처 방법",
            "퇴근 후 아이와 놀이 시간",
            "어린이집 입학 준비 물품",
            "아이 간식 뭘 주고 있나요?",
            "말 늦는 아이 언어치료",
            "형제 싸움 중재 방법",
            "아이 생일 파티 아이디어",
            "육아 관련 추천 도서 있나요?",
            "남편과 육아 분담 방법",
            "할머니와 육아 방식 충돌",
            "우리 아이 특이한 습관 있어요"
        ]

        contents = [
            "정말 난감했는데 다른 분들은 어떻게 하세요?",
            "저희 아이한테 잘 맞아서 공유합니다.",
            "이 방법을 쓴 후로 훨씬 나아졌어요.",
            "누구 경험 있으신가요? 참고하고 싶어요.",
            "저도 이 방법 써봤는데 효과 좋더라고요.",
            "혹시 같은 경험 있으신 분 있나요?",
            "이렇게 하니까 정말 잘 자더라고요.",
            "사진 결과가 너무 예뻤어요.",
            "정리해봤으니 참고하세요.",
            "이렇게 대처하니까 효과가 있었어요.",
            "이 시간이 정말 소중하네요.",
            "체크리스트 만들어봤어요.",
            "요즘 아이들은 뭘 좋아하나요?",
            "전문가 도움을 받았어요.",
            "이렇게 풀었어요.",
            "정말 즐거웠어요.",
            "추천 받은 책들이 도움 많이 됐어요.",
            "이렇게 분담하니까 잘 되네요.",
            "대화로 풀었어요.",
            "혹시 정상인가 싶기도 해요."
        ]

        self.stdout.write("\n[1] 자유게시판 생성 중...")
        for i in range(20):
            post = FreePost(
                title=titles[i % len(titles)],
                content=contents[i % len(contents)],
                author=user,
                category='육아 수다',
                views=random.randint(50, 500),
                comment_count=random.randint(5, 50),
                bookmark_count=random.randint(2, 30),
                reaction_empathy=random.randint(10, 100),
                reaction_thanks=random.randint(5, 50),
                reaction_courage=random.randint(3, 30),
                reaction_support=random.randint(2, 20),
                reaction_cheer=random.randint(2, 20),
                is_anonymous=False,
                created_at=timezone.now() - timedelta(hours=random.randint(1, 480)),
            )
            post.popularity_score = (
                post.comment_count * 5 + post.views + 
                post.bookmark_count * 3 + post.reaction_empathy * 2
            )
            post.save()
            self.stdout.write(f"  ✓ {i+1}. {post.title[:30]}")

    def create_hotdeal_posts(self, user):
        """핫딜공유 20개"""
        titles = [
            "아기 침대 40% 할인 중이에요",
            "유모차 신모델 출시 예정",
            "기저귀 구독 서비스 비교",
            "분유 가격 인상 전에 구매하세요",
            "육아용품 세트 할인 정보",
            "온라인 쇼핑몰 쿠폰 코드",
            "백화점 유아용품 세일",
            "중고 육아용품 거래 팁",
            "아기 옷 브랜드 세일 정보",
            "예방접종 비용 지원 프로그램",
            "육아용품 렌탈 서비스",
            "아기 장난감 추천 가성비 제품",
            "신생아 용품 필수 리스트",
            "분유 샘플 받는 방법",
            "유아 학원 수강료 할인",
            "아기 사진 촬영 쿠폰",
            "육아 관련 보험 상품",
            "영유아 건강검진 무료 지원",
            "베이비페어 개최 안내",
            "아기 옷 사이즈 교환 정책"
        ]

        contents = [
            "지금 구매하면 정말 싼 가격이에요.",
            "이 가격은 놓치면 안 돼요.",
            "이 서비스 정말 추천합니다.",
            "얼른 구매하세요.",
            "같은 제품 더 싼 곳 찾았어요.",
            "이 쿠폰 코드 유효해요.",
            "세일 기간 짧으니까 서두르세요.",
            "상태 정말 좋아요.",
            "이 브랜드 진짜 좋네요.",
            "지원금 신청하세요.",
            "렌탈이 훨씬 저렴해요.",
            "가격 대비 정말 좋은 제품이에요.",
            "처음 구매할 때 참고하세요.",
            "무료로 받을 수 있어요.",
            "등록금 할인받으세요.",
            "할인 쿠폰 있어요.",
            "가입 시 특별 혜택 받으세요.",
            "놓치지 마세요.",
            "일정 확인하고 가세요.",
            "교환 정책 괜찮아요."
        ]

        self.stdout.write("\n[2] 핫딜공유 생성 중...")
        for i in range(20):
            post = HotDeal(
                title=titles[i % len(titles)],
                content=contents[i % len(contents)],
                author=user,
                category='deal',
                views=random.randint(100, 800),
                comment_count=random.randint(10, 100),
                bookmark_count=random.randint(20, 200),
                reaction_cheer=random.randint(50, 300),
                is_anonymous=False,
                created_at=timezone.now() - timedelta(hours=random.randint(1, 480)),
            )
            post.popularity_score = (
                post.comment_count * 5 + post.views + 
                post.bookmark_count * 3 + post.reaction_cheer * 2
            )
            post.save()
            self.stdout.write(f"  ✓ {i+1}. {post.title[:30]}")

    def create_parenting_posts(self, user):
        """육아정보 20개"""
        titles = [
            "월령별 발달 체크리스트 (0~36개월)",
            "2026년 필수 예방접종 일정",
            "어린이집/유치원 준비물 완벽 정리",
            "아기 첫 이유식 단계별 가이드",
            "신생아 피부 관리 완벽 가이드",
            "아이 수면 교육 효과적인 방법",
            "육아용품 필수 물품 순위",
            "아기 목욕 올바른 방법",
            "신생아 기저귀 교환 횟수",
            "유아 영양 관리 기본",
            "아이 안전 교육 가이드",
            "돌잔치 준비 단계별 계획",
            "아기 수유 자세와 방법",
            "유아기 언어 발달 촉진법",
            "아이 미세먼지 대처 방법",
            "계절별 아이 옷 준비 팁",
            "아이 놀이의 중요성과 실천법",
            "돌까지 예방접종 필수 일정",
            "신생아 울음 해석 가이드",
            "육아휴직 제도 완벽 정리"
        ]

        contents = [
            "우리 아이가 정상적으로 발달하고 있는지 확인하세요.",
            "놓치면 안 되는 필수 예방접종을 정리했습니다.",
            "체크리스트 하나로 모든 준비물을 확인하세요.",
            "초기부터 완료기까지 단계별로 정리했어요.",
            "신생아 피부 특성을 이해하고 관리하세요.",
            "과학적 근거를 바탕으로 정리한 방법입니다.",
            "우선순위를 정해서 구매하세요.",
            "아기와 부모 모두 편안한 방법을 배우세요.",
            "월령별 적절한 횟수를 알아두세요.",
            "성장기 아이에게 필요한 영양소를 공급하세요.",
            "아이를 위험으로부터 보호하는 방법입니다.",
            "단계별로 계획하면 스트레스가 줄어들어요.",
            "올바른 자세로 모유수유하세요.",
            "아이의 말 발달을 촉진하는 활동들입니다.",
            "봄철 미세먼지 대처법을 알아두세요.",
            "계절에 따라 적절한 옷을 준비하세요.",
            "아이의 정서 발달에 중요해요.",
            "빠진 예방접종이 없는지 확인하세요.",
            "울음의 원인을 파악하면 대처가 쉬워져요.",
            "직장 복귀 계획을 미리 세우세요."
        ]

        self.stdout.write("\n[3] 육아정보 생성 중...")
        for i in range(20):
            post = ParentingInfo(
                title=titles[i % len(titles)],
                content=contents[i % len(contents)],
                author=user,
                views=random.randint(200, 1000),
                comment_count=random.randint(20, 150),
                bookmark_count=random.randint(50, 300),
                is_anonymous=False,
                created_at=timezone.now() - timedelta(hours=random.randint(1, 480)),
            )
            post.popularity_score = (
                post.comment_count * 5 + post.views + 
                post.bookmark_count * 3
            )
            post.save()
            self.stdout.write(f"  ✓ {i+1}. {post.title[:30]}")

    def create_notice_posts(self, user):
        """공지사항 20개"""
        titles = [
            "사이트 정기 점검 안내",
            "새로운 기능 업데이트",
            "이용약관 개정 안내",
            "개인정보 처리방침 변경",
            "앱 버전 업데이트 공지",
            "시스템 유지보수 안내",
            "보안 업데이트 공지",
            "신규 카테고리 오픈",
            "이벤트 당첨자 발표",
            "정기 서버 점검",
            "모바일 앱 업데이트",
            "커뮤니티 가이드라인 공시",
            "신기능 사용 방법 안내",
            "버그 수정 공지",
            "통합 검색 기능 추가",
            "보안 강화 공지",
            "서비스 이용 재개 안내",
            "정책 변경 공지",
            "시스템 성능 개선",
            "이용자 설문조사 참여 안내"
        ]

        contents = [
            "정기 점검으로 인해 서비스가 일시적으로 중단될 수 있습니다.",
            "더 나은 서비스를 위해 업데이트되었습니다.",
            "변경된 내용을 확인해주세요.",
            "새로운 정책을 적용합니다.",
            "최신 버전으로 업데이트해주세요.",
            "서비스 점검 중 이용이 불가능합니다.",
            "보안을 강화했습니다.",
            "새로운 카테고리가 추가되었습니다.",
            "당첨된 분들을 축하드립니다.",
            "정기 점검을 진행합니다.",
            "새로운 기능이 추가되었습니다.",
            "커뮤니티 이용 시 준수해주세요.",
            "새 기능 사용 방법을 안내합니다.",
            "버그가 수정되었습니다.",
            "통합 검색으로 더 편하게 찾으세요.",
            "보안이 강화되었습니다.",
            "서비스가 정상 복구되었습니다.",
            "서비스 정책이 변경되었습니다.",
            "시스템 성능이 개선되었습니다.",
            "더 나은 서비스를 위해 의견을 주세요."
        ]

        self.stdout.write("\n[4] 공지사항 생성 중...")
        for i in range(20):
            post = Notice(
                title=titles[i % len(titles)],
                content=contents[i % len(contents)],
                author=user,
                views=random.randint(300, 2000),
                comment_count=random.randint(5, 50),
                is_anonymous=False,
                created_at=timezone.now() - timedelta(hours=random.randint(1, 480)),
            )
            post.popularity_score = post.views + post.comment_count * 5
            post.save()
            self.stdout.write(f"  ✓ {i+1}. {post.title[:30]}")

    def create_flea_items(self, user):
        """벼룩시장 20개"""
        titles = [
            "신생아 옷 한 박스 팝니다",
            "아기 침대 미사용 판매",
            "유모차 깨끗한 상태",
            "기저귀 갈이대 팝니다",
            "아기 장난감 일괄 판매",
            "아기 포대기 + 쿠션",
            "수유 쿠션 3개 세트",
            "아기 모니터 팝니다",
            "아기 싱크대 의자 팝니다",
            "신발 정리용 보관함",
            "아기 카시트 판매",
            "속싸개 여러 장",
            "신생아 선물 세트",
            "육아용품 대량 판매",
            "아기 외출용품 세트",
            "아기 띠 여러 개",
            "고주파 치료기 팝니다",
            "아기 베개 판매",
            "육아용품 물려받습니다",
            "애착 인형 여러 개"
        ]

        prices = [
            "₩5,000", "₩15,000", "₩8,000", "₩12,000", "₩20,000",
            "₩3,000", "₩7,000", "₩25,000", "₩10,000", "₩4,000",
            "₩30,000", "₩2,000", "₩35,000", "₩50,000", "₩18,000",
            "₩1,500", "₩40,000", "₩6,000", "₩22,000", "₩9,000"
        ]

        self.stdout.write("\n[5] 벼룩시장 생성 중...")
        for i in range(20):
            item = FleaItem(
                title=titles[i % len(titles)],
                content=f"{prices[i]}에 팝니다. 상태 좋습니다.",
                author=user,
                item_price=prices[i],
                views=random.randint(50, 300),
                comment_count=random.randint(2, 20),
                bookmark_count=random.randint(1, 15),
                created_at=timezone.now() - timedelta(hours=random.randint(1, 480)),
            )
            item.save()
            self.stdout.write(f"  ✓ {i+1}. {item.title[:30]}")
