from django import forms
from .models import User, UserProfile, UserJobInfo

class SignUpForm(forms.ModelForm):
    user_name = forms.CharField(max_length=100)
    user_birthdate = forms.DateField()
    user_email = forms.EmailField()
    user_phone_no = forms.CharField(max_length=100)
    user_job = forms.CharField(max_length=100)
    user_classification = forms.CharField(max_length=100)
    user_income = forms.FloatField()

    class Meta:
        model = User
        fields = ['user_id', 'user_pw']
