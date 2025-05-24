from django.urls import path
from django.contrib.auth import views as auth_views
from .views import main_page, signup
from .views import UserLoginView

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),  # 로그인 뷰
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('signup/', signup, name='signup'),  # 회원가입
    path('', main_page, name='main'),  # 메인 페이지
]
