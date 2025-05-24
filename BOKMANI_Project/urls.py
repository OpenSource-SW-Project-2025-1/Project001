from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),  # 메인 페이지는 accounts에서 처리
    path('accounts/', include('accounts.urls')),  # 로그인 등은 accounts에서 처리
    # path('myapp/', include('myapp.urls')), ← 필요하면 추가
]
