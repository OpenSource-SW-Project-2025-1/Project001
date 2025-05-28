from django.urls import path, include
from .views import UserLoginView, UserSignUpView, custom_logout, profile_view, profile_edit, profile_delete
from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    #path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', UserSignUpView.as_view(), name='signup'),
    path('home/', include('myapp.urls')),
    path('logout/', custom_logout, name='logout'),
    #path('profile/', profile_view, name='profile'),
    path('profile/edit/', profile_edit, name='profile_edit'),
    path('profile/delete/', profile_delete, name='profile_delete'),
    path('profile/<int:pk>/', views.UserProfileView.as_view(), name='profile'),
]
