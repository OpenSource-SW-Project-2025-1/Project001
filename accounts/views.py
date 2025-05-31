from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.shortcuts import render, redirect
from .forms import SignUpForm
from .models import User, UserProfile, UserJobInfo
from django.contrib import messages
from django.views import View

class UserLoginView(FormView):
    template_name = 'accounts/login.html'
    form_class = AuthenticationForm
    success_url = '/'

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "회원정보가 존재하지 않습니다.")
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
    return render(request, 'accounts/custom_welfare.html')

def frequent_welfare(request):
    return render(request, 'accounts/frequent_welfare.html')

def new_welfare(request):
    return render(request, 'accounts/new_welfare.html')

def chatbot_home(request):
    return render(request, 'accounts/chatbot.html')

def team_programming(request):
    return render(request, 'accounts/team_programming.html')

def project_info(request):
    return render(request, 'accounts/project_info.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = User.objects.create(
                user_id=form.cleaned_data['user_id'],
                user_pw=form.cleaned_data['user_pw'],
            )
            UserProfile.objects.create(
                user=user,
                user_name=form.cleaned_data['user_name'],
                user_birthdate=form.cleaned_data['user_birthdate'],
                user_email=form.cleaned_data['user_email'],
                user_phone_no=form.cleaned_data['user_phone_no']
            )
            UserJobInfo.objects.create(
                user=user,
                user_job=form.cleaned_data['user_job'],
                user_classification=form.cleaned_data['user_classification'],
                user_income=form.cleaned_data['user_income']
            )
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

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

    return render(request, 'accounts/searchresult.html', {
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

    return render(request, 'accounts/ai_recommend_result.html', {
        'results': ai_results,
        'query': "AI 추천 결과",
        'page_range': range(1, 2),
        'current_page': 1,
    })
