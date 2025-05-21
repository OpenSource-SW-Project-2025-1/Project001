from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [

    path('admin/', admin.site.urls),
    path('home/', include('myapp.urls')),
    path('', lambda request: redirect('home/')),
    path('accounts/', include('accounts.urls')),  # accounts 앱의 로그인/회원가입
    path('accounts/', include('django.contrib.auth.urls')),  # 기본 login/logout 기능

]
