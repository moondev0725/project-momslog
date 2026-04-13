# 25-12-29 슬기 수정: AJAX 상태 변경 (판매중 → 예약중 → 판매완료)
@login_required(login_url='accounts:login')
def flea_status_update(request, pk):
    item = get_object_or_404(FleaItem, pk=pk)
    
    # 작성자만 상태 변경 가능
    if request.user != item.author:
        return JsonResponse({'success': False, 'error': '작성자만 변경 가능합니다.'}, status=403)
    
    if request.method == 'POST':
        # POST 데이터에서 새로운 상태 받기
        new_status = request.POST.get('status', item.status)
        
        # 유효한 상태 확인
        valid_statuses = ['selling', 'reserved', 'sold']
        if new_status not in valid_statuses:
            return JsonResponse({'success': False, 'error': '유효하지 않은 상태입니다.'}, status=400)
        
        item.status = new_status
        item.save()
        
        # 상태명 맵핑
        status_labels = {
            'selling': '판매중',
            'reserved': '예약중',
            'sold': '판매완료'
        }
        
        return JsonResponse({
            'success': True,
            'new_status': new_status,
            'status_label': status_labels[new_status]
        })
    
    return JsonResponse({'success': False, 'error': 'POST 요청만 가능합니다.'}, status=400)
