from django.contrib.auth.hashers import make_password
from django.contrib.auth import login, logout
from django.views.generic.edit import FormView
from django.shortcuts import render, redirect
from collections import defaultdict
import time
from BOKMANI_Project.settings import genai_API_KEY
from .forms import SignUpForm, UserProfileForm, UserJobInfoForm, UserLoginForm
from .models import UserID, UserProfile, UserJobInfo,Location
from django.contrib import messages
from django.views import View
from django.http import JsonResponse
import google.generativeai as genai
from django.views.decorators.csrf import csrf_exempt
import json

genai.configure(api_key=genai_API_KEY)

import subprocess
from django.shortcuts import render
from django.conf import settings
import time
import os

# def search_result_mock(request):
#     result_path = os.path.join(settings.BASE_DIR, 'media', 'api_result.txt')
#     parsed_results = []
#
#     if os.path.exists(result_path):
#         with open(result_path, 'r', encoding='utf-8') as f:
#             lines = [line.strip() for line in f.readlines() if line.strip()]
#         i = 0
#         while i + 15 <= len(lines):
#             result = {
#                 "title": lines[i + 3],
#                 "category": lines[i + 5],
#                 "description": lines[i + 7],
#                 "keywords": [lines[i + 4]]
#             }
#             parsed_results.append(result)
#             i += 15
#     else:
#         parsed_results = []
#
#     return render(request, "accounts/search_result.html", {
#         "results": parsed_results,
#         "query": "",
#         "page_range": range(1, 2),
#         "current_page": 1,
#     })

def search_result_mock(request):
    age = request.GET.get('age', '')
    searchWrd = request.GET.get('query', '')
    lifeArray = request.GET.get('lifeArray', '')
    trgterIndvdlArray = request.GET.get('trgterIndvdlArray', '')
    intrsThemaArray = request.GET.get('ThemaArray', '')

    parsed_results = []
    message = ""

    script_path = os.path.join(settings.BASE_DIR, 'central_welfare_api.py')
    result_path = os.path.join(settings.BASE_DIR, 'media', 'api_result.txt')

    # 스크립트 실행 조건
    if searchWrd or intrsThemaArray or age or lifeArray or trgterIndvdlArray:
        try:
            command = [
                'python', script_path,
                age, searchWrd, lifeArray, trgterIndvdlArray, intrsThemaArray
            ]

            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )

            if result.returncode == 0:
                message = "API 호출 스크립트 완료."
            else:
                message = f"API 호출 스크립트 실패: {result.stderr.strip()}"
                print(f"Script Error: {result.stderr}")

        except Exception as e:
            message = f"스크립트 실행 중 예외 발생: {str(e)}"
            print(f"Exception during script execution: {e}")
    else:
        message = "검색어를 입력하거나 키워드를 선택해주세요."

    # 결과 파일 파싱
    if os.path.exists(result_path):
        try:
            with open(result_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines()]

            start_data_idx = -1
            for idx, line in enumerate(lines):
                if line.strip().isdigit() and (idx == 0 or not lines[idx - 1].strip().isdigit()):
                    start_data_idx = idx
                    break

            if start_data_idx != -1:
                # 데이터 시작 지점부터 16줄 간격으로 파싱 (데이터 15줄 + 1줄 공백)
                i = start_data_idx
                while i + 15 < len(lines):  # 총 15줄 데이터가 있어야 하므로 i+15까지 확인
                    # 각 필드에 해당하는 정확한 줄 번호 확인
                    # (lines[i]가 '1'이면, lines[i+1]이 ID, lines[i+2]가 제목 등)
                    service_id = lines[i + 1] if len(lines) > i + 1 else None
                    title = lines[i + 2] if len(lines) > i + 2 else "제목 없음"
                    category = lines[i + 3] if len(lines) > i + 3 else "분류 없음"
                    description = lines[i + 9] if len(lines) > i + 9 else "내용 없음"
                    link = lines[i + 10] if len(lines) > i + 10 else "#"
                    # 키워드 필드(대상)는 lines[i + 6]
                    # 추가 키워드/특징은 lines[i + 14]
                    # 둘 다 활용하여 keywords 필드를 구성

                    keywords_from_target = [lines[i + 6]] if (
                                len(lines) > i + 6 and lines[i + 6] and lines[i + 6].lower() != 'none') else []
                    keywords_from_last_line = []
                    if len(lines) > i + 14 and lines[i + 14] and lines[i + 14].lower() != 'none':
                        keywords_from_last_line = [k.strip() for k in lines[i + 14].split(',') if
                                                   k.strip()]  # 쉼표로 구분된 키워드

                    # 두 키워드 소스를 합쳐서 중복 제거
                    combined_keywords = list(set(keywords_from_target + keywords_from_last_line))

                    parsed_results.append({
                        "id": service_id,  # 상세 링크를 위해 ID도 포함
                        "title": title,
                        "category": category,
                        "description": description,
                        "link": link,
                        "keywords": combined_keywords,
                    })
                    i += 16  # 다음 서비스 항목은 16줄 뒤에 시작 (15줄 데이터 + 빈 줄 1개)

                if not message:
                    message = f"총 {len(parsed_results)}개의 복지 서비스를 조회했습니다."
            else:
                message = "결과 파일에서 복지 서비스 데이터를 찾을 수 없습니다."

        except Exception as e:
            message = f"결과 파일 파싱 중 오류 발생: {str(e)}"
            print(f"File parsing error: {e}")
            parsed_results = []
    else:
        if not (searchWrd or intrsThemaArray or age or lifeArray or trgterIndvdlArray):
            message = "검색어를 입력하거나 키워드를 선택해주세요."
        else:
            message = "스크립트 실행 후 결과 파일을 찾을 수 없거나 파일 내용이 비어있습니다."
        parsed_results = []

    context = {
        "results": parsed_results,
        "query": searchWrd,
        "age": age,
        "lifeArray": lifeArray,
        "trgterIndvdlArray": trgterIndvdlArray,
        "ThemaArray": intrsThemaArray,
        "message": message,
        "page_range": range(1, max(2, (len(parsed_results) + 9) // 10)),  # 결과 수에 따라 페이지네이션 조정 (예시)
        "current_page": 1,
    }
    return render(request, "accounts/search_result.html", context)


def run_local_api_script(request):
    import time
    import os
    from django.conf import settings
    import subprocess

    script_path = os.path.join(settings.BASE_DIR, 'central_welfare_api.py')

    # GET 요청에서 파라미터 추출
    age = request.GET.get('age', '')
    searchWrd = request.GET.get('searchWrd', '')
    lifeArray = request.GET.get('lifeArray', '')
    trgterIndvdlArray = request.GET.get('trgterIndvdlArray', '')
    intrsThemaArray = request.GET.get('ThemaArray', '')  # keyword 버튼에서 전달됨

    # API 호출 실행
    try:
        result = subprocess.run(
            ['python', script_path, age, searchWrd, lifeArray, trgterIndvdlArray, intrsThemaArray],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        message = "API 호출 완료" if result.returncode == 0 else f"실패: {result.stderr}"
    except Exception as e:
        message = f"실행 중 오류: {str(e)}"

    # 결과 파일 경로
    result_path = os.path.join(settings.BASE_DIR, 'media', 'api_result.txt')
    parsed_results = []

    # 결과 파싱
    if os.path.exists(result_path):
        modified_time = time.ctime(os.path.getmtime(result_path))
        with open(result_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        i = 0
        while i + 15 <= len(lines):
            result = {
                "title": lines[i + 3],
                "category": lines[i + 5],
                "description": lines[i + 7],
                "keywords": [lines[i + 4]]
               }
            parsed_results.append(result)
            i += 15  # 한 항목당 15줄 + 공백

        content = "\n".join(lines)  # 디버깅용 텍스트
    else:
        modified_time = "파일이 존재하지 않음"
        content = "결과 파일이 없습니다."

    # 결과 페이지로 렌더링
    return render(request, 'accounts/search_result.html', {
        'content': content,
        'message': message,
        'modified_time': modified_time,
        'results': parsed_results,
    })


def signup(request):
    error_msg = None

    if request.method == 'POST':
        user_form = SignUpForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        job_form = UserJobInfoForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid() and job_form.is_valid():
            try:
                if UserID.objects.filter(user_id=user_form.cleaned_data['user_id']).exists():
                    raise ValueError('이미 존재하는 아이디입니다.')

                hashed_pw = make_password(user_form.cleaned_data['user_pw'])
                birth_date = profile_form.cleaned_data['user_birthdate']
                income_raw = job_form.cleaned_data.get('user_income')
                income = int(income_raw) if income_raw not in [None, ''] else 0

                # 시/도, 시군구 → location 객체 찾기
                sido = request.POST.get('sido')
                sigungu = request.POST.get('sigungu')
                location_instance = Location.objects.filter(sido=sido, sigungu=sigungu).first()

                user = UserID.objects.create(
                    user_id=user_form.cleaned_data['user_id'],
                    user_pw=hashed_pw,
                )

                UserProfile.objects.create(
                    user=user,
                    user_name=profile_form.cleaned_data['user_name'],
                    user_email=profile_form.cleaned_data['user_email'],
                    user_phone_no=profile_form.cleaned_data['user_phone_no'],
                    user_birthdate=birth_date,
                    location=location_instance,
                )

                UserJobInfo.objects.create(
                    user=user,
                    user_job=job_form.cleaned_data['user_job'],
                    user_classification=job_form.cleaned_data['user_classification'],
                    user_income=income,
                )

                messages.success(request, '회원가입이 성공적으로 완료되었습니다!')
                return redirect('login')

            except Exception as e:
                error_msg = f'회원가입 중 오류가 발생했습니다: {e}'
        else:
            error_msg = '입력값이 유효하지 않습니다.'
    else:
        user_form = SignUpForm()
        profile_form = UserProfileForm()
        job_form = UserJobInfoForm()

    # location_json 항상 계산
    location_dict = defaultdict(set)
    for loc in Location.objects.all():
        location_dict[loc.sido].add(loc.sigungu)

    location_data = {
        sido: sorted(list(sigungu_set))
        for sido, sigungu_set in location_dict.items()
    }

    return render(request, 'accounts/signup.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'job_form': job_form,
        'location_json': location_data,
        'error': error_msg
    })


# 아이디 유효성 검사
def check_id(request):
    user_id = request.GET.get('user', '')
    exists = UserID.objects.filter(user_id=user_id).exists()
    return JsonResponse({'exists': exists})


# # 로그인 확인코드
class UserLoginView(FormView):
    template_name = 'accounts/login.html'
    form_class = UserLoginForm
    success_url = '/'

    def dispatch(self, request, *args, **kwargs):
        # request.session에 'user_id'가 존재하면 (로그인 상태로 간주)
        if request.session.get('user_id'):
            # 로그인 페이지 대신 success_url (홈 페이지)로 리다이렉션
            return redirect(self.success_url)
        # 로그인 상태가 아니면, 원래의 로그인 뷰 로직을 계속 진행
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.cleaned_data['user']
        self.request.session['user_id'] = user.user_id  # 세션에 저장하거나 직접 로그인 처리
        # login(self.request, user)
        messages.success(self.request, f"환영합니다, {user.user_id}님!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "아이디 또는 비밀번호가 일치하지 않습니다.")
        return super().form_invalid(form)


class UserLogoutView(View):

    def post(self, request, *args, **kwargs):
        messages.success(request, "로그아웃 되었습니다.")
        logout(request)
        return redirect('main')


def main_page(request):
    new_benefits = [
        {"title": "의료급여 임신.출산진료비지원", "description": "임신.출산 진료비로 100만원 지원", "d_day": 365},
        {"title": "청년 월세 지원", "description": "1년간 최대 월 20만원", "d_day": 12},
    ]

    popular_benefits = [
        {"title": "취업 준비금 지원", "description": "1인당 150만원", "d_day": 5},
        {"title": "자격증 시험비 지원", "description": "최대 3회 지원", "d_day": 22},
    ]

    return render(request, 'accounts/main.html', {
        'new_benefits': new_benefits,
        'popular_benefits': popular_benefits
    })


def custom_welfare(request):
    return render(request, 'accounts/search_result.html')

def frequent_welfare(request):
    return render(request, 'accounts/search_result.html')


def new_welfare(request):
    return render(request, 'accounts/search_result.html')


def welfare_info(request):
    return render(request, 'accounts/welfare_info.html')


def chatbot_home(request):
    return render(request, 'accounts/ai_recommend_result.html')


def team_programming(request):
    return render(request, 'accounts/team_programming.html')


def project_info(request):
    return render(request, 'accounts/project_info.html')


def ai_recommend_result(request):
    # 추후 AI 추천 데이터로 대체 가능
    ai_results = [
        {
            "id": 101,
            "title": "AI 추천 - 청년 취업 지원금",
            "description": "청년을 위한 맞춤형 취업 장려금 제공",
            "category": "고용",
            "d_day": 15,
            "keywords": ["청년", "AI추천", "취업"]
        },
        {
            "id": 102,
            "title": "AI 추천 - 주거 급여 확대",
            "description": "AI가 추천한 최근 주거 정책",
            "category": "주거",
            "d_day": 30,
            "keywords": ["주거", "맞춤형"]
        },
    ]

    return render(request, 'accounts/ai_result.html', {
        'results': ai_results,
        'query': "AI 추천 결과",
        'page_range': range(1, 2),
        'current_page': 1,
    })


# 챗봇 모델 설정을 위한 함수 (중복 코드를 줄이고 관리 용이하게)
def get_gemini_model_configured():
    return genai.GenerativeModel(
        'gemini-2.0-flash',
        system_instruction="""
        너는 사용자에게 친절하고 간결하게 복지정보에 대해 답변하는 AI 챗봇이야.
        답변은 항상 3~4문장 이내로 요약해서 제공해야 해.
        사용자의 질문에 직접적으로 답변하고, 불필요한 서론이나 미사여구는 사용하지 마.
        글씨체를 두껍게 하는 표시 등은 일체 사용하지마.
        **같은 기호도 사용하지 마
        복지에 대해서는 이름, 장소, 날짜, 시간 등을 명확히 대답해줘.
        관련 웹사이트의 URL을 텍스트 형식으로 제공해줘.
        만약 특정 링크를 알지 못하더라도, '관련 정보를 찾아보시려면 충북대학교 공식 홈페이지를 방문하여 [어떤 메뉴]를 찾아보세요.' 와 같이 구체적인 안내를 텍스트로 제공해야 해
        또한 답변에 대한 정보를 찾을 수 잇는 링크도 제공해
        충북대학교 생활협동조합에서 받을 수 있는 복지에 대해 알려줘. -> ~~ 추가적으로 충북대학교 생활협동조합 홈페이지는 https://www.cbnucoop.com/ 입니다.
        **매우 중요: 모든 답변에 Markdown 형식 (예: *, **, _, [], (), #)을 절대 사용하지 마.**
        링크는 https:// 부터 전부 제공해
        관련 웹사이트 링크가 있다면 **반드시 웹사이트 URL 주소 텍스트를 그대로 출력해야 해. Markdown 하이퍼링크 ([텍스트](URL)) 형식은 절대 사용하지 마.**
        너에게 받아온 텍스트를 그대로 출력하니 텍스트를 깔끔한 형태로 표현해. 링크를 제공한 후에는 줄바꿈을 적극적으로 활용해
        링크를 제공하지 못할 경우, "관련 정보를 찾아보시려면 [기관명] 공식 홈페이지를 검색해 주세요." 와 같이 설명해야 해.
        제공하지 못한다면 최소한 더 큰 범위에서의 링크 예) 청주시청 홈페이지.  같은거라도 제공해.
        전화번호도 제공하면 좋지만 링크를 우선적으로 제공해
        절대 '개인정보보호를 위해 링크를 제공하지 않습니다', '링크를 제공할 수 없으나' 와 같은 표현은 사용하지 마.
        """,
        # 답변 길이를 제어
        generation_config=genai.GenerationConfig(
            max_output_tokens=300,  # 최대 출력 토큰 수 (대략 140~200단어. 6~8문장에 맞게 조절)
            temperature=0.7,  # 답변의 창의성 (0.0~1.0, 낮을수록 보수적)
        )
    )


def chatbot(request):
    # 만약 menu.html이 이 페이지에 필요 없다고 판단되면 include를 제거합니다.
    return render(request, 'accounts/chatbot.html')


@csrf_exempt
def chatbot_reply(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '')
        # *** 클라이언트(JS)에서 보낸 대화 이력 받기 ***
        chat_history = data.get('history', [])

        try:
            # 설정이 적용된 모델 객체 가져오기
            model = get_gemini_model_configured()
            chat = model.start_chat(history=chat_history)

            # 새 메시지 전송 (chat 객체를 통해)
            response = chat.send_message(user_message)
            reply_text = response.text

        except Exception as e:
            # 에러 발생 시 처리
            print(f"Gemini API Error: {e}")
            reply_text = "죄송합니다. 현재 시스템에 문제가 발생했습니다. 다시 시도해 주세요."
            if "ResourceExhausted" in str(e):
                reply_text = "죄송합니다. 현재 요청이 너무 많아 잠시 후 다시 시도해 주세요. (API 사용량 초과)"
            elif "NotFound" in str(e):
                reply_text = "죄송합니다. 챗봇 모델을 찾을 수 없습니다. 관리자에게 문의하세요."
            # 토큰 길이 초과 오류 처리 (긴 대화 시 발생 가능)
            elif "Quota exceeded for model" in str(e) or "Too many tokens" in str(e) or "context length" in str(
                    e).lower():
                reply_text = "대화 내용이 너무 길어져 이전 내용을 모두 기억하기 어렵습니다. 대화를 새로 시작해 주세요."
            else:  # 그 외 예상치 못한 오류
                reply_text = "알 수 없는 오류가 발생했습니다: " + str(e)

        return JsonResponse({'reply': reply_text})
    return JsonResponse({'error': 'Invalid request method'}, status=400)