from django.shortcuts import render
from django.http import JsonResponse
import google.generativeai as genai
import json
import os

# API 키를 환경 변수에서 가져오기 (또는 settings.py에서)
# 환경 변수가 없으면 settings.py의 GOOGLE_API_KEY 사용
try:
    from django.conf import settings
    GOOGLE_API_KEY = getattr(settings, 'GOOGLE_API_KEY', os.getenv('GOOGLE_API_KEY', ''))
except:
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')

if not GOOGLE_API_KEY:
    print("⚠️  경고: GOOGLE_API_KEY가 설정되지 않았습니다!")
    print("   settings.py에 GOOGLE_API_KEY를 추가하거나 환경 변수를 설정해주세요.")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    print("❌ Google API 키가 없어서 챗봇이 작동하지 않습니다.")

def chatbot_view(request):
    if request.method == 'POST':
        try:
            # 데이터 받기
            data = json.loads(request.body)
            user_message = data.get('message', '')
            print(f"▶ 사용자 질문: {user_message}")

            # ★ 26-01-02 추가: 이유식/레시피 키워드 감지
            recipe_keywords = ['이유식', '레시피', '밥', '죽', '음식', '먹이', '재료']
            is_recipe_request = any(keyword in user_message for keyword in recipe_keywords)
            
            if is_recipe_request:
                print("🍽️  이유식 레시피 생성 모드 활성화")
                recipe_response = {
                    'response': """🍽️ AI 이유식 레시피 생성기를 시작할게요!

냉장고에 있는 재료를 알려주시면, 월령별 맞춤 이유식 레시피를 3초 안에 만들어드립니다!

예: "시금치, 두부, 당근, 쌀" 이렇게 입력해주세요.""",
                    'is_recipe': True,
                    'user_message': user_message,
                }
                return JsonResponse(recipe_response)
            
            # ⚠️ API 키가 없거나 차단된 경우 테스트 모드
            if not GOOGLE_API_KEY:
                print("⚠️  테스트 모드: 실제 API 대신 더미 응답 반환")
                dummy_response = f"안녕하세요! 저는 맘스로그 AI입니다.\n\n당신의 질문: '{user_message}'\n\n❌ 죄송하지만, 현재 Google API 키가 설정되지 않아 실제 답변을 드릴 수 없습니다.\n관리자가 새로운 API 키를 설정해주시면 정상 작동합니다."
                return JsonResponse({'response': dummy_response})
            
            try:
                # 모델 이름 변경 (사용자 목록에 있는 최신 모델로 변경)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # 시스템 프롬프트 (챗봇의 성격 설정)
                system_prompt = "당신은 육아 커뮤니티 '맘스로그'의 친절한 AI 상담사입니다. 답변은 친절하고 따뜻한 말투로 해주세요."
                full_prompt = f"{system_prompt}\n\n사용자 질문: {user_message}"

                print(f"▶ API 호출 중... (모델: gemini-2.5-flash)")
                
                # 질문 보내기
                response = model.generate_content(full_prompt)
                ai_response = response.text
                
                print(f"▶ AI 답변 생성 성공: {ai_response[:50]}...")

                return JsonResponse({'response': ai_response})
            
            except Exception as api_error:
                if "PermissionDenied" in str(type(api_error).__name__) or "leaked" in str(api_error):
                    error_response = "❌ API 키 오류\n\n현재 사용 중인 Google API 키가 차단되었습니다.\n새로운 API 키를 발급받아야 합니다.\n\n[해결 방법]\n1. Google AI Studio (aistudio.google.com/app/apikey)에서 새 키 발급\n2. 발급받은 키를 관리자에게 전달\n3. 관리자가 settings.py에 키를 업데이트"
                    print(f"⚠️  API 키 차단됨: {str(api_error)}")
                    return JsonResponse({'response': error_response}, status=403)
                else:
                    raise

        except json.JSONDecodeError as e:
            error_msg = f"JSON 파싱 오류: {str(e)}"
            print(f"!!!!!! {error_msg} !!!!!! ")
            return JsonResponse({'response': '죄송합니다. 요청 형식이 잘못되었습니다.'}, status=400)
        
        except Exception as e:
            import traceback
            error_msg = f"{type(e).__name__}: {str(e)}"
            traceback.print_exc()
            print(f"!!!!!! 에러 발생 !!!!!! : {error_msg}")
            return JsonResponse({'response': f'죄송합니다. 오류가 발생했어요. [{type(e).__name__}]'}, status=500)

    return render(request, 'chatbot/chatbot_widget.html')