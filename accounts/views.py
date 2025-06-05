from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth import login, logout
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.shortcuts import render, redirect
from .forms import SignUpForm,UserProfileForm,UserJobInfoForm,UserLoginForm
from .models import UserID, UserProfile, UserJobInfo
from django.contrib import messages
from django.views import View
from django.http import JsonResponse
from datetime import datetime
from .models import Location

def signup(request):
    if request.method == 'POST':
        user_form = SignUpForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        job_form = UserJobInfoForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid() and job_form.is_valid():
            try:
                # 아이디 중복 확인
                if UserID.objects.filter(user_id=user_form.cleaned_data['user_id']).exists():
                    raise ValueError('이미 존재하는 아이디입니다.')

                # 비밀번호 암호화
                raw_pw = user_form.cleaned_data['user_pw']
                hashed_pw = make_password(raw_pw)

                # 생년월일
                birth_date = profile_form.cleaned_data['user_birthdate']

                # 소득 처리
                income_raw = job_form.cleaned_data.get('user_income')
                income = int(income_raw) if income_raw not in [None, ''] else 0

                # location 처리
                location_id = request.POST.get('location')
                location_instance = Location.objects.get(id=location_id) if location_id else None

                # 유저 생성
                user = UserID.objects.create(
                    user_id=user_form.cleaned_data['user_id'],
                    user_pw=hashed_pw,
                )

                # 프로필 생성
                UserProfile.objects.create(
                    user=user,
                    user_name=profile_form.cleaned_data['user_name'],
                    user_email=profile_form.cleaned_data['user_email'],
                    user_phone_no=profile_form.cleaned_data['user_phone_no'],
                    user_birthdate=birth_date,
                    location=location_instance,
                )

                # 직업 정보 생성
                UserJobInfo.objects.create(
                    user=user,
                    user_job=job_form.cleaned_data['user_job'],
                    user_classification=job_form.cleaned_data['user_classification'],
                    user_income=income,
                )

                return redirect('login')

            except Exception as e:
                return render(request, 'accounts/signup.html', {
                    'user_form': user_form,
                    'profile_form': profile_form,
                    'job_form': job_form,
                    'locations': Location.objects.all(),  # ← 추가!
                    'error': f'회원가입 중 오류가 발생했습니다: {e}'
                })
    else:
        user_form = SignUpForm()
        profile_form = UserProfileForm()
        job_form = UserJobInfoForm()

    return render(request, 'accounts/signup.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'job_form': job_form,
        'locations': Location.objects.all()  # ← 추가!
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

    def form_valid(self, form):
        user = form.cleaned_data['user']
        self.request.session['user_id'] = user.user_id  # 세션에 저장하거나 직접 로그인 처리
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
        {"title": "다문화가족 교육비 지원", "description": "전자 바우처 제공", "d_day": 30},
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




def search_result_mock(request):
    query = request.GET.get('query', '')  # 검색어 가져오기

    mock_results = [
        {
            "id": 1,
            "title": "주거급여 지원",
            "description": "저소득층 대상 주거급여를 지원합니다.",
            "category": "주거",
            "d_day": 10,
            "keywords": ["주거", "저소득층", "정부지원"]
        },
        {
            "id": 2,
            "title": "청년내일채움공제",
            "description": "청년 장기근속 장려금 제공",
            "category": "고용",
            "d_day": 20,
            "keywords": ["청년", "취업", "장려금"]
        },
        {
            "id": 3,
            "title": "기초연금 지급",
            "description": "65세 이상 어르신 대상",
            "category": "연금",
            "d_day": 5,
            "keywords": []
        }
    ]

    return render(request, 'accounts/search_result.html', {
        'results': mock_results,
        'query': query,
        'page_range': range(1, 4),
        'current_page': 1,
    })

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
