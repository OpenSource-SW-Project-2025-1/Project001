from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')),             # 메인 페이지는 myapp에서 처리
    path('accounts/', include('accounts.urls')),  # 로그인 등 계정 관련 URL은 accounts에서 처리
]
