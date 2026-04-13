# ═══════════════════════════════════════════════════════════════════════
# chat/views.py
# 맘스로그 프로젝트 - 실시간 채팅 뷰
# ═══════════════════════════════════════════════════════════════════════
# 작성일: 2026-01-02
# ═══════════════════════════════════════════════════════════════════════

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count
from .models import ChatRoom, ChatMessage, ChatRoomMember
import json
from django.utils import timezone


@login_required(login_url='accounts:login')
def chat_lobby(request):
    """
    채팅 로비: 모든 채팅방 목록
    """
    # 카테고리 필터링
    category = request.GET.get('category', 'general')
    
    # 채팅방 목록 조회
    if category == 'all':
        rooms = ChatRoom.objects.filter(is_active=True).annotate(
            member_count=Count('members')
        )
    else:
        rooms = ChatRoom.objects.filter(
            category=category,
            is_active=True
        ).annotate(member_count=Count('members'))
    
    # 사용자가 참여한 채팅방
    joined_rooms = request.user.joined_chatrooms.all()

    # 임베디드/팝업 모드는 제거됨
    
    context = {
        'rooms': rooms,
        'joined_rooms': joined_rooms,
        'selected_category': category,
    }
    return render(request, 'chat/chat_lobby.html', context)


@login_required(login_url='accounts:login')
def chat_room(request, room_id):
    """
    채팅방 상세: 메시지 목록과 입력 폼
    """
    room = get_object_or_404(ChatRoom, pk=room_id)
    
    # 현재 사용자가 채팅방 멤버인지 확인
    is_member = room.members.filter(pk=request.user.pk).exists()
    
    # 멤버가 아니면 자동 입장
    if not is_member:
        ChatRoomMember.objects.get_or_create(room=room, user=request.user)
        room.members.add(request.user)
    
    # 마지막 읽은 시간 업데이트
    member_obj = ChatRoomMember.objects.get(room=room, user=request.user)
    member_obj.last_read_at = timezone.now()
    member_obj.save()
    
    # 메시지 조회
    messages = room.messages.all().order_by('created_at')
    
    # ★ 26-01-02 수정: 마지막 메시지 ID를 context에 전달
    # 템플릿에서 Django 템플릿 필터로 처리 불가능하므로 view에서 계산
    # (기존: {% if messages %}{{ messages|last|dict_lookup:"id" }} -> 불가능)
    # (수정: context의 last_message_id 사용)
    last_message_id = messages.last().id if messages.exists() else 0
    
    context = {
        'room': room,
        'messages': messages,
        'is_member': is_member,
        'last_message_id': last_message_id,  # ★ 26-01-02 추가
    }
    return render(request, 'chat/chat_room.html', context)



@login_required(login_url='accounts:login')
@require_http_methods(["POST"])
def send_message(request, room_id):
    """
    메시지 전송 (AJAX)
    """
    room = get_object_or_404(ChatRoom, pk=room_id)
    
    # 멤버 확인
    if not room.members.filter(pk=request.user.pk).exists():
        return JsonResponse({'error': '이 채팅방의 멤버가 아닙니다.'}, status=403)
    
    content = request.POST.get('content', '').strip()
    
    if not content:
        return JsonResponse({'error': '메시지를 입력하세요.'}, status=400)
    
    # 메시지 생성
    message = ChatMessage.objects.create(
        room=room,
        user=request.user,
        content=content
    )
    
    # 사용자 닉네임 조회
    try:
        user_nickname = request.user.userprofile.nickname
    except:
        user_nickname = request.user.username
    
    return JsonResponse({
        'success': True,
        'message': {
            'id': message.id,
            'user': message.user.username,
            'user_nickname': user_nickname,
            'content': message.content,
            'created_at': message.created_at.strftime('%H:%M:%S'),
        }
    })


@login_required(login_url='accounts:login')
def fetch_messages(request, room_id):
    """
    새로운 메시지 조회 (AJAX Polling)
    """
    room = get_object_or_404(ChatRoom, pk=room_id)
    
    # 멤버 확인
    if not room.members.filter(pk=request.user.pk).exists():
        return JsonResponse({'error': '이 채팅방의 멤버가 아닙니다.'}, status=403)
    
    # 마지막 메시지 ID 이후의 메시지 조회
    last_message_id = request.GET.get('last_message_id', 0)
    
    messages = room.messages.filter(id__gt=last_message_id).order_by('created_at')
    
    message_list = []
    for msg in messages:
        try:
            user_nickname = msg.user.userprofile.nickname
        except:
            user_nickname = msg.user.username
        
        message_list.append({
            'id': msg.id,
            'user': msg.user.username,
            'user_nickname': user_nickname,
            'content': msg.content,
            'created_at': msg.created_at.strftime('%H:%M:%S'),
            'is_own': msg.user == request.user,
        })
    
    return JsonResponse({
        'messages': message_list,
    })


@login_required(login_url='accounts:login')
def leave_room(request, room_id):
    """
    채팅방 나가기
    ★ 26-01-06 수정: 나가기 시 해당 사용자의 메시지 삭제
    """
    room = get_object_or_404(ChatRoom, pk=room_id)
    
    # ★ 26-01-06 추가: 해당 사용자의 메시지 삭제
    ChatMessage.objects.filter(room=room, user=request.user).delete()
    
    # 멤버 제거
    room.members.remove(request.user)
    ChatRoomMember.objects.filter(room=room, user=request.user).delete()
    
    return redirect('chat:chat_lobby')


# ═══════════════════════════════════════════════════════════════════════
# 🌙 새벽 2시의 수다 (Midnight Chat) - WebSocket 기반
# ═══════════════════════════════════════════════════════════════════════

@login_required(login_url='accounts:login')
def midnight_chat(request):
    """
    새벽 2시의 수다 페이지
    
    특징:
    - 익명 채팅 (사용자 정보 노출 안 함)
    - 시간 제한: 밤 12시(00:00) ~ 새벽 5시(05:00)만 이용 가능
    - WebSocket 기반 실시간 양방향 통신 (Channels)
    - 자동 닉네임 생성 (엄마#1234 형식)
    
    context:
    - is_midnight_hours: 현재 시간이 운영 시간인지 여부
    - can_chat: 사용자가 채팅 가능한지 여부
    """
    from .models import MidnightChatRoom, MidnightChatMessage
    
    # 시간 제한 확인
    is_midnight_hours = MidnightChatRoom.is_midnight_hours()
    
    # 새벽 채팅방 초기화 (singleton)
    midnight_room = MidnightChatRoom.get_or_create_midnight_room()
    
    # 최근 메시지 로드 (페이지 로드 시 과거 메시지 표시)
    recent_messages = MidnightChatMessage.objects.filter(
        room=midnight_room
    ).order_by('-created_at')[:50]  # 최근 50개 메시지
    recent_messages = list(reversed(recent_messages))  # 시간순 정렬
    
    context = {
        'is_midnight_hours': is_midnight_hours,
        'can_chat': is_midnight_hours,  # 운영 시간에만 채팅 가능
        'recent_messages': recent_messages,
        'ws_url': 'ws://localhost:8000/ws/midnight/',  # WebSocket 연결 URL
    }
    
    return render(request, 'chat/chat_midnight.html', context)


# ======================================================
# Popup Widget: API (Ajax)
# ======================================================
@login_required(login_url='accounts:login')
@require_http_methods(["GET"])
def api_rooms(request):
    """채팅방 목록(JSON) - 참여중/전체 목록 제공"""
    category = request.GET.get('category')
    qs = ChatRoom.objects.filter(is_active=True)
    if category and category != 'all':
        qs = qs.filter(category=category)
    qs = qs.annotate(member_count=Count('members'))

    def serialize_room(r):
        return {
            'id': r.id,
            'title': r.title,
            'description': r.description or '',
            'category': r.category,
            'member_count': getattr(r, 'member_count', r.members.count()),
        }

    joined_rooms = request.user.joined_chatrooms.all().annotate(member_count=Count('members'))
    return JsonResponse({
        'rooms': [serialize_room(r) for r in qs],
        'joined_rooms': [serialize_room(r) for r in joined_rooms],
    })


@login_required(login_url='accounts:login')
@require_http_methods(["POST"])
def api_join_room(request, room_id):
    """해당 방 참여 보장 후 OK 반환"""
    room = get_object_or_404(ChatRoom, pk=room_id, is_active=True)
    if not room.members.filter(pk=request.user.pk).exists():
        ChatRoomMember.objects.get_or_create(room=room, user=request.user)
        room.members.add(request.user)
    return JsonResponse({'ok': True})


@login_required(login_url='accounts:login')
@require_http_methods(["GET"])
def api_member_info(request, room_id):
    """현재 사용자 정보 (닉네임 등) 반환"""
    user_nickname = request.user.nickname if hasattr(request.user, 'nickname') and request.user.nickname else request.user.username
    return JsonResponse({
        'user': request.user.username,
        'user_nickname': user_nickname,
    })


@login_required(login_url='accounts:login')
@require_http_methods(["POST"])
def leave_room_popup(request, room_id):
    """채팅방 나가기 (팝업용) - JSON 응답
    멤버 제거하여 참여중 목록에서 제거
    """
    room = get_object_or_404(ChatRoom, pk=room_id)
    
    # 멤버 제거
    room.members.remove(request.user)
    ChatRoomMember.objects.filter(room=room, user=request.user).delete()
    
    return JsonResponse({'success': True})


@login_required(login_url='accounts:login')
@require_http_methods(["POST"])
def clear_room_messages(request, room_id):
    """채팅방의 모든 메시지 삭제 (팝업용)"""
    room = get_object_or_404(ChatRoom, pk=room_id)
    
    # 멤버 확인
    if not room.members.filter(pk=request.user.pk).exists():
        return JsonResponse({'error': '이 채팅방의 멤버가 아닙니다.'}, status=403)
    
    # 해당 채팅방의 모든 메시지 삭제
    deleted_count = room.messages.all().delete()[0]
    
    return JsonResponse({
        'success': True,
        'deleted_count': deleted_count
    })
