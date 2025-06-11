from django.urls import path
from . import views

# urls.py
urlpatterns = [
    path('input/', views.input_student, name='input_student'),
    path('list/', views.student_list, name='student_list'),
]

