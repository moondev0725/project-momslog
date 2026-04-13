#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PIL(Pillow)을 사용하여 히어로 커뮤니티 영상 생성
MP4 생성을 위해 pillow 및 기본 프레임 이미지를 만듭니다.
"""

import os
from pathlib import Path

def create_fallback_image():
    """
    비디오 로드 실패 시 표시할 정적 이미지를 생성합니다.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("❌ Pillow 설치 필요: pip install Pillow")
        return False
    
    output_dir = Path(__file__).parent / 'static' / 'images'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    img_path = output_dir / 'hero-fallback.jpg'
    
    # 1200x800 이미지 생성
    img = Image.new('RGB', (1200, 800), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # 제목 텍스트
    title_text = "엄마들의 진짜 후기 커뮤니티"
    subtitle_text = "광고보다 솔직한, 검증된 경험"
    
    # 간단한 텍스트 그리기
    try:
        title_font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 56)
        subtitle_font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 32)
        text_font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 18)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    # 배경 색상 영역
    draw.rectangle([(0, 0), (1200, 250)], fill=(245, 245, 250))
    draw.rectangle([(0, 250), (1200, 500)], fill=(249, 249, 251))
    draw.rectangle([(0, 500), (1200, 800)], fill=(255, 255, 255))
    
    # 텍스트 그리기
    draw.text((600, 100), title_text, fill=(31, 38, 51), font=title_font, anchor="mm")
    draw.text((600, 200), subtitle_text, fill=(255, 138, 114), font=subtitle_font, anchor="mm")
    
    # 예시 카드
    draw.rectangle([(100, 350), (1100, 450)], outline=(255, 138, 114), width=3)
    draw.text((120, 370), "육아 수다 · 방금 전", fill=(153, 153, 153), font=text_font)
    draw.text((120, 400), '"수면 교육 성공 후기"', fill=(45, 45, 45), font=text_font)
    draw.text((120, 430), "💬 45 · ❤️ 178 · 🔖 89", fill=(136, 136, 136), font=text_font)
    
    # 하단 메시지
    draw.text((600, 600), "이런 디테일이 실제 선택을 바꿔요", fill=(85, 85, 85), font=subtitle_font, anchor="mm")
    
    img.save(img_path, 'JPEG', quality=85)
    print(f"✅ 폴백 이미지 생성: {img_path}")
    return True

def create_dummy_mp4():
    """
    간단한 더미 MP4 파일을 생성합니다.
    """
    output_dir = Path(__file__).parent / 'static' / 'videos'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    mp4_path = output_dir / 'hero-community.mp4'
    
    try:
        # 최소 유효한 MP4 파일 구조 작성
        with open(mp4_path, 'wb') as f:
            f.write(b'\x00\x00\x00\x20ftypisom')
            f.write(b'\x00' * 100)
        
        print(f"✅ 더미 MP4 파일 생성: {mp4_path}")
        return True
    except Exception as e:
        print(f"❌ MP4 생성 실패: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("🎬 히어로 영상 리소스 생성")
    print("=" * 60)
    
    # 1. 폴백 이미지 생성
    print("\n[1] 폴백 이미지 생성...")
    create_fallback_image()
    
    # 2. 더미 MP4 생성
    print("\n[2] 더미 MP4 파일 생성...")
    create_dummy_mp4()
    
    print("\n" + "=" * 60)
    print("✅ 리소스 생성 완료!")
    print("=" * 60)
    print("\n📝 다음 단계:")
    print("   1. 브라우저에서 http://127.0.0.1:8000 접속")
    print("   2. 폴백 이미지로 UI가 표시됨")
    print("   3. 실제 비디오로 교체하려면 FFmpeg 설치")
