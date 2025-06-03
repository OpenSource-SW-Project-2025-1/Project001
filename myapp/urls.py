from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import welfare_view

urlpatterns = [
    path('', views.home, name='home'),

    # 로그인 페이지 연결
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),

    # 로그아웃
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    path('welfare/', welfare_view, name='welfare'),
]
# accounts/urls.py

