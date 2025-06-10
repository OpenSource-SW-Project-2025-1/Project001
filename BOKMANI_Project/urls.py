from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from accounts import views
from accounts.views import search_result_mock
from accounts.views import ai_recommend_result
from django.urls import path, include
urlpatterns = [




    path('admin/', admin.site.urls),
    path('', include('myapp.urls')),             # 메인 페이지는 myapp에서 처리
    path('accounts/', include('accounts.urls')),  # 로그인 등 계정 관련 URL은 accounts에서 처리

    path('search_result/', search_result_mock, name='search_result'),

    path('recommend/', ai_recommend_result, name='ai-recommend'),  # 추천 결과 직접 등록

    path('chatbot/reply/', views.chatbot_reply, name='chatbot_reply'),
]

# 개발 중 media 파일 서빙
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)