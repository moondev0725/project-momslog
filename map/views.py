from django.shortcuts import render

# ★ 지도 페이지
def map_view(request):
    return render(request, 'map/map.html')

# 26-01-02: 일기장 기능이 board 앱으로 이동되었습니다.
# board.views.diary_list, diary_create, diary_detail, diary_edit, diary_delete를 사용하세요.
# URL: /board/free/diary/
