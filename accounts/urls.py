from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import main_page, signup, UserLogoutView
from .views import UserLoginView


urlpatterns = [

    path('check_id/', views.check_id, name='check_id'), # 아이디 중복확인
    path('login/', UserLoginView.as_view(), name='login'),  # 로그인 뷰
    #path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('logout/', UserLogoutView.as_view(), name='logout'),

    path('signup/', signup, name='signup'),  # 회원가입
    path('', main_page, name='main'),  # 메인 페이지
    path('custom-welfare/', views.custom_welfare, name='custom_welfare'),
    path('frequent-welfare/', views.frequent_welfare, name='frequent_welfare'),
    path('new-welfare/', views.new_welfare, name='new_welfare'),
    path('chatbot/', views.chatbot_home, name='chatbot_home'),
    path('team-programming/', views.team_programming, name='team_programming'),
    path('project-info/', views.project_info, name='project_info'),
]
