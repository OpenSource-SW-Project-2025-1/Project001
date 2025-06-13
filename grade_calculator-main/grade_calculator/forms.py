from django import forms
from .models import Student

class StudentScoreForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['student_id', 'name', 'en_grade', 'c_grade', 'py_grade']