from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from .models import MomDiary, DiaryEntry
import google.generativeai as genai
from django.conf import settings
import json

# Gemini API 설정
genai.configure(api_key=settings.GOOGLE_API_KEY)


# ★ 지도 페이지
def map_view(request):
    return render(request, 'map/map.html')


# ★ 일기장 리스트
@login_required
def diary_list(request):
    """엄마 마음 케어 일기장 리스트"""
    diary, created = MomDiary.objects.get_or_create(user=request.user)
    entries = diary.entries.all()
    
    # 필터링
    mood_filter = request.GET.get('mood', '')
    search_query = request.GET.get('q', '')
    
    if mood_filter:
        entries = entries.filter(mood=mood_filter)
    if search_query:
        entries = entries.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))
    
    context = {
        'diary': diary,
        'entries': entries,
        'mood_filter': mood_filter,
        'search_query': search_query,
        'mood_choices': DiaryEntry.MOOD_CHOICES,
    }
    return render(request, 'map/diary_list.html', context)


# ★ 일기 작성
@login_required
def diary_create(request):
    """새 일기 작성"""
    diary, created = MomDiary.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        mood = request.POST.get('mood', 'peaceful')
        title = request.POST.get('title', '')
        content = request.POST.get('content', '')
        is_secret = request.POST.get('is_secret', False) == 'on'
        tags = request.POST.get('tags', '')
        
        entry = DiaryEntry.objects.create(
            diary=diary,
            mood=mood,
            title=title,
            content=content,
            is_secret=is_secret,
            tags=tags
        )
        
        # AI 케어 응답 생성
        generate_ai_care_response(entry)
        
        return redirect('diary_detail', pk=entry.pk)
    
    context = {
        'diary': diary,
        'mood_choices': DiaryEntry.MOOD_CHOICES,
    }
    return render(request, 'map/diary_create.html', context)


# ★ 일기 상세 보기
@login_required
def diary_detail(request, pk):
    """일기 상세 페이지"""
    entry = get_object_or_404(DiaryEntry, pk=pk, diary__user=request.user)
    
    context = {
        'entry': entry,
        'mood_label': dict(DiaryEntry.MOOD_CHOICES).get(entry.mood, ''),
    }
    return render(request, 'map/diary_detail.html', context)


# ★ 일기 수정
@login_required
def diary_edit(request, pk):
    """일기 수정"""
    entry = get_object_or_404(DiaryEntry, pk=pk, diary__user=request.user)
    
    if request.method == 'POST':
        entry.mood = request.POST.get('mood', entry.mood)
        entry.title = request.POST.get('title', entry.title)
        entry.content = request.POST.get('content', entry.content)
        entry.is_secret = request.POST.get('is_secret', False) == 'on'
        entry.tags = request.POST.get('tags', entry.tags)
        entry.save()
        
        # AI 응답 재생성 여부
        if request.POST.get('regenerate_ai'):
            generate_ai_care_response(entry)
        
        return redirect('diary_detail', pk=entry.pk)
    
    context = {
        'entry': entry,
        'mood_choices': DiaryEntry.MOOD_CHOICES,
    }
    return render(request, 'map/diary_edit.html', context)


# ★ 일기 삭제
@login_required
@require_http_methods(["POST"])
def diary_delete(request, pk):
    """일기 삭제"""
    entry = get_object_or_404(DiaryEntry, pk=pk, diary__user=request.user)
    entry.delete()
    return redirect('diary_list')


# ★ AI 케어 응답 생성
def generate_ai_care_response(entry):
    """
    Gemini API를 사용해 공감과 조언을 담은 AI 응답 생성
    프롬프트 엔지니어링으로 따뜻하고 실질적인 조언 제공
    """
    try:
        mood_label = dict(DiaryEntry.MOOD_CHOICES).get(entry.mood, '')
        
        # 프롬프트 엔지니어링
        prompt = f"""당신은 따뜻하고 경험 많은 육아 전문가이자 감정 상담가입니다.
한 명의 엄마가 일기에 적은 감정과 일상을 읽고, 깊은 공감과 실질적인 조언을 해주세요.

【엄마의 현재 기분】: {mood_label}

【엄마가 적은 내용】:
{entry.content}

【요청사항】:
1. 먼저 엄마의 감정을 깊게 이해하고 공감해주세요 (2-3문장)
2. 엄마가 겪는 상황이 얼마나 어려운지 인정해주세요
3. 구체적이고 실천 가능한 조언을 3가지 제시하세요
4. 마지막으로 힘내라는 따뜻한 격려 말씀을 해주세요

【톤】: 친한 선배 엄마처럼 따뜻하고 다정하게, 판단하지 않으면서도 실질적으로

답변은 한국어로, 3-4단락으로 구성해주세요."""

        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        
        if response.text:
            entry.ai_care_response = response.text
            entry.ai_response_generated = True
            entry.save()
            return True
    
    except Exception as e:
        print(f"AI 응답 생성 오류: {str(e)}")
        return False
    
    return False


# ★ API: 빠른 감정 저장
@login_required
@require_http_methods(["POST"])
def quick_mood_save(request):
    """빠른 감정 기록 (AJAX)"""
    try:
        diary, created = MomDiary.objects.get_or_create(user=request.user)
        
        data = json.loads(request.body)
        mood = data.get('mood', 'peaceful')
        content = data.get('content', '')
        
        if content:
            entry = DiaryEntry.objects.create(
                diary=diary,
                mood=mood,
                content=content
            )
            
            # 백그라운드에서 AI 응답 생성
            generate_ai_care_response(entry)
            
            return JsonResponse({
                'success': True,
                'entry_id': entry.id,
                'message': '감정이 저장되었습니다'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': '내용을 입력해주세요'
            }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

