from django.contrib import admin
from django.urls import path, include

from accounts.views import search_result_mock
from accounts.views import ai_recommend_result

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')),             # 메인 페이지는 myapp에서 처리
    path('accounts/', include('accounts.urls')),  # 로그인 등 계정 관련 URL은 accounts에서 처리

    path('searchresult/', search_result_mock, name='searchresult'),

    path('recommend/', ai_recommend_result, name='ai-recommend'),  # 추천 결과 직접 등록

]
