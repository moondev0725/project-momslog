#!/usr/bin/env python
"""
운영진 고정글 설정 테스트
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mompjt.settings')
django.setup()

from board.models import FreePost
from django.utils import timezone

# 조회수가 가장 많은 게시글을 운영진 고정으로 설정
post = FreePost.objects.filter(views__gt=0).order_by('-views').first()
if post:
    post.is_pinned = True
    post.pinned_at = timezone.now()
    post.save()
    print(f'✓ "{post.title}" 운영진 고정 설정 (views={post.views})')
else:
    print('✗ 게시글을 찾을 수 없습니다.')
