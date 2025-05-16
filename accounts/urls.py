from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import UserLoginView

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('login/', UserLoginView.as_view(), name='login'),
]
