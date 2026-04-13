"""
PetCounselPost의 views 필드 데이터 복구 스크립트
잘못된 views 값(날짜 문자열 등)을 0으로 초기화
"""

import os
import django

# Django 설정 초기화
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mompjt.settings')
django.setup()

from board.models import PetCounselPost

def fix_views():
    """views 필드가 잘못된 레코드를 수정"""
    fixed_count = 0
    error_count = 0
    
    posts = PetCounselPost.objects.all()
    print(f"총 {posts.count()}개의 게시글을 검사합니다...")
    
    for post in posts:
        try:
            # views 값이 정수인지 확인
            if isinstance(post.views, int):
                continue
            
            # 문자열이면 정수로 변환 시도
            if isinstance(post.views, str):
                try:
                    views_int = int(post.views)
                    print(f"게시글 #{post.pk}: views='{post.views}' -> {views_int}")
                    post.views = views_int
                    post.save(update_fields=['views'])
                    fixed_count += 1
                except ValueError:
                    # 변환 실패시 0으로 초기화
                    print(f"게시글 #{post.pk}: views='{post.views}' -> 0 (변환 실패)")
                    post.views = 0
                    post.save(update_fields=['views'])
                    fixed_count += 1
            else:
                # 기타 타입은 0으로 초기화
                print(f"게시글 #{post.pk}: views={post.views} (타입: {type(post.views)}) -> 0")
                post.views = 0
                post.save(update_fields=['views'])
                fixed_count += 1
                
        except Exception as e:
            print(f"게시글 #{post.pk} 처리 중 오류: {e}")
            error_count += 1
    
    print("\n" + "="*50)
    print(f"수정 완료: {fixed_count}개")
    print(f"오류 발생: {error_count}개")
    print("="*50)

if __name__ == '__main__':
    fix_views()
