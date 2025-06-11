from django import forms

class StudentScoreForm(forms.Form):
    student_id = forms.CharField(label='학번')
    name = forms.CharField(label='이름')
    english = forms.IntegerField(label='English')
    c_language = forms.IntegerField(label='C Language')
    python = forms.IntegerField(label='Python')
