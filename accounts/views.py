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
import requests

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
                # 각 서비스 항목이 숫자로 시작하는 규칙을 따름
                if line.strip().isdigit() and (idx == 0 or not lines[idx - 1].strip().isdigit()):
                    start_data_idx = idx
                    break

            if start_data_idx != -1:
                i = start_data_idx
                while i + 15 < len(lines):  # 총 16줄 데이터 (0~15 인덱스) 확인
                    # 각 필드에 대한 정확한 줄 번호 확인 및 파싱 (제공해주신 데이터 형식 기반)

                    # 1줄: 번호 (예: 1, 2) - 사용하지 않음
                    # 2줄: 서비스 ID
                    current_service_id = lines[i + 1] if len(lines) > i + 1 else None
                    # 3줄: 정책 이름
                    policy_name = lines[i + 2] if len(lines) > i + 2 else "정보 없음"
                    # 4줄: 관심 분야
                    category = lines[i + 3] if len(lines) > i + 3 else "정보 없음"
                    # 5줄: 소관 부처명
                    ministry_name = lines[i + 4] if len(lines) > i + 4 else "정보 없음"
                    # 6줄: 소관 조직명
                    division_name = lines[i + 5] if len(lines) > i + 5 else "정보 없음"
                    # 7줄: 대상 연령
                    target_age = lines[i + 6] if len(lines) > i + 6 else "정보 없음"
                    # 8줄: 온라인 신청 가능 여부
                    online_application_available = lines[i + 7] if len(lines) > i + 7 else "N"
                    # 9줄: 문의처
                    contact_number = lines[i + 8] if len(lines) > i + 8 else "정보 없음"
                    # 10줄: 서비스 요약 (description)
                    summary = lines[i + 9] if len(lines) > i + 9 else "정보 없음"
                    # 11줄: 상세 링크
                    detail_link = lines[i + 10] if len(lines) > i + 10 else "#"
                    # 12줄: 지원 주기
                    support_cycle = lines[i + 11] if len(lines) > i + 11 else "정보 없음"
                    # 13줄: 제공 유형
                    offer_type = lines[i + 12] if len(lines) > i + 12 else "정보 없음"
                    # 14줄: 등록일
                    reg_date = lines[i + 13] if len(lines) > i + 13 else "정보 없음"
                    # 15줄: 대상자 (가구 유형, 대상자, 선정기준이 함께 있을 수 있음)
                    # 이 부분은 단일 필드로 처리
                    target_audience_raw = lines[i + 14] if len(lines) > i + 14 else "정보 없음"


                    # 'target_audience_raw'에서 가구 유형, 대상자, 선정 기준을 분리해야 한다면
                    # 추가적인 파싱 로직 필요 (예: 콤마로 구분되어 있으면 split)

                    # 현재 데이터 형식에 맞춰 keywords는 15번째 줄의 콤마로 구분된 값으로 가정
                    keywords_str = lines[i + 14] if len(lines) > i + 14 else ""
                    keywords = [k.strip() for k in keywords_str.split(',') if k.strip()] if keywords_str else []

                    # '지급 서비스'는 10번째 줄에 해당하는 요약에서 가져오거나,
                    # 아니면 별도의 필드가 있다면 해당 인덱스에서 가져와야 함.
                    # 현재 제공된 데이터에서는 "서비스 요약"과 "지급 서비스"가 동일한 줄(10번째)에 있는 것으로 보임.
                    # 만약 별도의 줄에 있다면 해당 인덱스를 찾아야 함.
                    benefits = summary  # 임시로 summary와 동일하게 설정, 필요시 수정

                    # 복지 서비스 객체에 모든 상세 필드 포함
                    service_data = {
                        "id": current_service_id,
                        "policy_name": policy_name,
                        "category": category,
                        "ministry_name": ministry_name,
                        "division_name": division_name,
                        "summary": summary,
                        "benefits": benefits,  # 지급 서비스
                        "detail_link": detail_link,
                        "support_cycle": support_cycle,
                        "offer_type": offer_type,
                        "reg_date": reg_date,
                        "target_age": target_age,
                        "online_application_available": online_application_available,
                        "contact_number": contact_number,
                        "keywords": keywords,
                        # 추가적으로 파싱되어야 할 필드가 있다면 여기에 추가
                        "household_type": "",  # 현재 데이터에서 명확히 분리되지 않으면 비워두기
                        "target_audience": target_audience_raw,
                        "selection_criteria": "",  # 현재 데이터에서 명확히 분리되지 않으면 비워두기
                    }
                    parsed_results.append(service_data)
                    print(f"Parsed and stored item ID: {current_service_id}")
                    i += 16  # 다음 서비스 항목 시작 인덱스

                if not message and parsed_results:
                    message = f"총 {len(parsed_results)}개의 복지 서비스를 조회했습니다."
                elif not message:
                    message = "검색 결과가 없습니다."
            else:
                message = "결과 파일에서 복지 서비스 데이터를 찾을 수 없습니다. 파일 형식을 확인해주세요."

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

    # 파싱된 결과를 캐시에 저장하여 welfare_detail 뷰에서 접근할 수 있도록 함
    # TTL (Time To Live)은 적절히 설정 (예: 5분 = 300초)
    # 실제 사용자 세션 ID 등을 키로 사용하면 더 안전함
    request.session['search_results_data'] = parsed_results
    # 캐시 대신 Django 세션 사용을 권장합니다. 사용자별 데이터를 저장하기 용이합니다.
    # cache.set('search_results_data', parsed_results, 300)

    context = {
        "results": parsed_results,
        "query": searchWrd,
        "age": age,
        "lifeArray": lifeArray,
        "trgterIndvdlArray": trgterIndvdlArray,
        "ThemaArray": intrsThemaArray,
        "message": message,
        "page_range": range(1, max(2, (len(parsed_results) + 9) // 10)),
        "current_page": 1,
    }
    return render(request, "accounts/search_result.html", context)


def welfare_detail(request, service_id):
    detail_info = {}

    # search_results 뷰에서 세션에 저장한 데이터를 가져옴
    all_search_results = request.session.get('search_results_data', [])

    found_item = None
    for item in all_search_results:
        if item.get('id') == service_id:
            found_item = item
            break

    if found_item:
        detail_info = found_item
        print(f"상세 정보 조회 성공: {service_id}")
    else:
        print(f"세션에서 상세 정보 찾을 수 없음: {service_id}")
        detail_info = {
            "policy_name": "정보 없음",
            "summary": f"ID {service_id}에 해당하는 복지 서비스 정보를 찾을 수 없습니다.",
            "policy_id": service_id,
            "category": "정보 없음",
            "ministry_name": "정보 없음",
            "division_name": "정보 없음",
            "benefits": "정보 없음",
            "detail_link": "#",
            "support_cycle": "정보 없음",
            "offer_type": "정보 없음",
            "reg_date": "정보 없음",
            "target_age": "정보 없음",
            "online_application_available": "정보 없음",
            "contact_number": "정보 없음",
            "household_type": "정보 없음",
            "target_audience": "정보 없음",
            "selection_criteria": "정보 없음",
        }

    context = {
        'detail_info': detail_info,
        'service_id': service_id,
    }
    return render(request, 'accounts/welfare_info.html', context)



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
    # 메인 페이지에 표시할 8개의 복지 서비스 데이터
    # 각 필드명은 main.html 및 welfare_info.html에서 사용하는 변수명과 일치시켜야 합니다.
    # 'id' 필드는 welfare_info 상세 페이지로 넘겨줄 핵심 값입니다.
    all_main_benefits = [
        {
            "id": "WLF00003250",
            "policy_name": "영유아보육료 지원", # 상세 페이지 제목으로 사용될 이름 (정책명)
            "category": "보육",
            "ministry_name": "교육부",
            "division_name": "영유아재정과",
            "target_age": "영유아",
            "online_application_available": "Y",
            "contact_number": "02-6222-6060",
            "summary": "어린이집 이용 영유아에 대한 보육료 지원을 통해 부모의 자녀양육 부담경감 및 원활한 경제활동을 지원합니다.",
            "detail_link": "https://www.bokjiro.go.kr/ssis-tbu/twataa/wlfareInfo/moveTWAT52011M.do?wlfareInfoId=WLF00003250&wlfareInfoReldBztpCd=01",
            "support_cycle": "월",
            "offer_type": "전자바우처(바우처)",
            "reg_date": "20210903",
            "target_audience": "", # 제공된 데이터에서는 None 이지만, 빈 문자열로 두는 것이 일반적입니다.
            "keywords": "보육,영유아", # main.html에서 해시태그로 표시할 키워드 (쉼표로 구분)
            "period": "상시", # main.html에 표시할 신청 기간
            "tag": "교육부", # main.html에 표시할 태그 (부처명)
            "d_day": 10 # main.html에 표시할 D-day
        },
        {
            "id": "WLF00000969",
            "policy_name": "유아학비 지원(3~5세 누리과정 지원)",
            "category": "교육",
            "ministry_name": "교육부",
            "division_name": "영유아재정과",
            "target_age": "영유아",
            "online_application_available": "Y",
            "contact_number": "1544-0079",
            "summary": "국공사립유치원에 재원하는 유아를 대상으로 보호자의 소득수준에 관계없이 전 계층에 유아학비를 지원하여 실질적 교육기회 보장을 지원합니다.",
            "detail_link": "https://www.bokjiro.go.kr/ssis-tbu/twataa/wlfareInfo/moveTWAT52011M.do?wlfareInfoId=WLF00000969&wlfareInfoReldBztpCd=01",
            "support_cycle": "월",
            "offer_type": "전자바우처(바우처)",
            "reg_date": "20210903",
            "target_audience": "",
            "keywords": "교육,영유아",
            "period": "상시",
            "tag": "교육부",
            "d_day": 5
        },
        {
            "id": "WLF00004657",
            "policy_name": "부모급여 지원",
            "category": "보육",
            "ministry_name": "보건복지부",
            "division_name": "아동정책과",
            "target_age": "영유아",
            "online_application_available": "Y",
            "contact_number": "129",
            "summary": "영아기 집중돌봄을 두텁게 지원하여 출산 및 양육으로 인한 경제적 부담을 줄여드립니다.",
            "detail_link": "https://www.bokjiro.go.kr/ssis-tbu/twataa/wlfareInfo/moveTWAT52011M.do?wlfareInfoId=WLF00004657&wlfareInfoReldBztpCd=01",
            "support_cycle": "월",
            "offer_type": "현금지급",
            "reg_date": "20220103",
            "target_audience": "",
            "keywords": "보육,출산,경제적부담",
            "period": "상시",
            "tag": "보건복지부",
            "d_day": 20
        },
        {
            "id": "WLF00003253",
            "policy_name": "가정양육수당 지원사업",
            "category": "보육",
            "ministry_name": "교육부",
            "division_name": "영유아재정과",
            "target_age": "영유아,아동",
            "online_application_available": "Y",
            "contact_number": "02-6222-6060",
            "summary": "가정에서 아이를 돌보는 가정 양육 시, 부모의 자녀 양육에 대한 부담을 줄이고 보육 서비스에 대한 선택권을 보장합니다.",
            "detail_link": "https://www.bokjiro.go.kr/ssis-tbu/twataa/wlfareInfo/moveTWAT52011M.do?wlfareInfoId=WLF00003253&wlfareInfoReldBztpCd=01",
            "support_cycle": "월",
            "offer_type": "현금지급",
            "reg_date": "20210903",
            "target_audience": "",
            "keywords": "보육,가정양육",
            "period": "상시",
            "tag": "교육부",
            "d_day": 15
        },
        {
            "id": "WLF00000024",
            "policy_name": "아이돌봄 서비스",
            "category": "보육,보호·돌봄",
            "ministry_name": "여성가족부",
            "division_name": "가족문화과",
            "target_age": "영유아,아동,청소년",
            "online_application_available": "Y",
            "contact_number": "1577-8136",
            "summary": "맞벌이를 하거나 갑자기 아이를 돌볼 수 없는 일이 생겼을 때 육아 도우미가 방문하여 12세 이하 자녀의 양육을 도와줍니다.",
            "detail_link": "https://www.bokjiro.go.kr/ssis-tbu/twataa/wlfareInfo/moveTWAT52011M.do?wlfareInfoId=WLF00000024&wlfareInfoReldBztpCd=01",
            "support_cycle": "수시",
            "offer_type": "기타",
            "reg_date": "20210903",
            "target_audience": "다문화·탈북민,다자녀,장애인,한부모·조손",
            "keywords": "아이돌봄,맞벌이,육아",
            "period": "수시",
            "tag": "여성가족부",
            "d_day": 30
        },
        {
            "id": "WLF00000867",
            "policy_name": "방과후학교 자유수강권",
            "category": "교육,보호·돌봄",
            "ministry_name": "교육부",
            "division_name": "늘봄학교정책과",
            "target_age": "아동,청소년",
            "online_application_available": "Y",
            "contact_number": "1544-9654",
            "summary": "방과후학교 수업을 통해 저소득층 자녀의 지속적이며 실직적인 교육기회를 확대하고 공교육 활성화 및 저소득층의 교육격차 해소를 돕습니다.",
            "detail_link": "https://www.bokjiro.go.kr/ssis-tbu/twataa/wlfareInfo/moveTWAT52011M.do?wlfareInfoId=WLF00000867&wlfareInfoReldBztpCd=01",
            "support_cycle": "수시",
            "offer_type": "프로그램/서비스(서비스)",
            "reg_date": "20210903",
            "target_audience": "다문화·탈북민,저소득,한부모·조손",
            "keywords": "방과후학교,자유수강권,저소득",
            "period": "수시",
            "tag": "교육부",
            "d_day": 25
        },
        {
            "id": "WLF00001140",
            "policy_name": "방과후보육료지원",
            "category": "보육,교육",
            "ministry_name": "교육부",
            "division_name": "교육보육과정지원과",
            "target_age": "아동",
            "online_application_available": "Y",
            "contact_number": "02-6222-6060",
            "summary": "어린이집을 이용하는 12세 이하 취학아동에 대한 방과후 보육료를 지원하여 양육의 부담을 줄이고 원활한 경제활동을 돕습니다.",
            "detail_link": "https://www.bokjiro.go.kr/ssis-tbu/twataa/wlfareInfo/moveTWAT52011M.do?wlfareInfoId=WLF00001140&wlfareInfoReldBztpCd=01",
            "support_cycle": "월",
            "offer_type": "전자바우처(바우처)",
            "reg_date": "20210903",
            "target_audience": "장애인,저소득,한부모·조손",
            "keywords": "방과후보육료,아동",
            "period": "월",
            "tag": "교육부",
            "d_day": 18
        },
        {
            "id": "WLF00001067",
            "policy_name": "장애아보육료지원",
            "category": "보육",
            "ministry_name": "교육부",
            "division_name": "영유아재정과",
            "target_age": "영유아,아동",
            "online_application_available": "Y",
            "contact_number": "02-6222-6060",
            "summary": "어린이집 이용 장애아동에 대한 보육료 지원을 통해 부모의 자녀양육 부담경감 및 원활한 경제활동을 지원합니다.",
            "detail_link": "https://www.bokjiro.go.kr/ssis-tbu/twataa/wlfareInfo/moveTWAT52011M.do?wlfareInfoId=WLF00001067&wlfareInfoReldBztpCd=01",
            "support_cycle": "월",
            "offer_type": "전자바우처(바우처)",
            "reg_date": "20210903",
            "target_audience": "장애인",
            "keywords": "장애아보육료,보육",
            "period": "월",
            "tag": "교육부",
            "d_day": 22
        },
    ]

    new_benefits = all_main_benefits[:4]
    popular_benefits = all_main_benefits[4:]

    # welfare_info 뷰에서 사용할 수 있도록 모든 데이터를 세션에 저장
    request.session['search_results_data'] = all_main_benefits

    context = {
        'new_benefits': new_benefits,
        'popular_benefits': popular_benefits,
    }
    return render(request, 'accounts/main.html', context)


def custom_welfare(request):
    return render(request, 'accounts/search_result.html')

def frequent_welfare(request):
    return render(request, 'accounts/search_result.html')


def new_welfare(request):
    return render(request, 'accounts/search_result.html')


def welfare_info(request, service_id):  # <-- service_id 인자를 받도록!
    detail_info = {}

    # 세션에서 이전에 main_page에서 저장된 모든 복지 서비스 데이터를 가져옵니다.
    all_benefits_from_session = request.session.get('search_results_data', [])

    found_item = None
    for item in all_benefits_from_session:
        if item.get('id') == service_id:  # 세션 데이터의 'id' 필드와 URL에서 받은 service_id를 비교
            found_item = item
            break

    if found_item:
        detail_info = found_item
        print(f"상세 정보 조회 성공 (세션 사용): {service_id}")  # 디버깅용 메시지
    else:
        print(f"세션에서 ID {service_id}에 해당하는 상세 정보 찾을 수 없음. 기본 정보 표시.")  # 디버깅용 메시지
        # 세션에 정보가 없을 경우 (예: URL에 직접 접근하거나 세션 만료), 기본 정보 표시
        detail_info = {
            "policy_name": f"ID {service_id}에 해당하는 복지 서비스 정보를 찾을 수 없습니다.",
            "summary": "세션에 저장된 데이터에 해당 복지 정보가 없습니다. (API 호출 없음)",
            "id": service_id,
            "category": "정보 없음",
            "ministry_name": "정보 없음",
            "division_name": "정보 없음",
            "benefits": "정보 없음",  # welfare_info.html에서 사용하는 필드
            "detail_link": "#",
            "support_cycle": "정보 없음",
            "offer_type": "정보 없음",
            "reg_date": "정보 없음",
            "target_age": "정보 없음",
            "online_application_available": "정보 없음",
            "contact_number": "정보 없음",
            "household_type": "정보 없음",
            "target_audience": "정보 없음",
            "selection_criteria": "정보 없음",
            "period": "정보 없음",
            "tag": "정보 없음",
            "d_day": 0
        }

    context = {
        'detail_info': detail_info,
        'service_id': service_id,  # 템플릿에서 service_id가 필요할 경우를 위해 전달
    }
    return render(request, 'accounts/welfare_info.html', context)


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