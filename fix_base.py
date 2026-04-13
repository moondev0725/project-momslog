# 임시 스크립트: base.html에서 브랜드 배너 섹션 완전 삭제
import re

file_path = r'c:\workspace\d0107\mompjt\main\templates\base.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 브랜드 배너 섹션 전체를 찾아서 삭제
# <section class="brand-banner"부터 </section>까지 모두 삭제
pattern = r'<section class="brand-banner".*?</section>'
content = re.sub(pattern, '', content, flags=re.DOTALL)

# 주석도 삭제
content = content.replace('        <!-- 브랜드 선언형 배너: 광고가 아닌 서비스 철학 섹션 -->\n', '')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("브랜드 배너 섹션 삭제 완료!")
