from django import forms
from .models import User, UserProfile, UserJobInfo

class SignUpForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['user_id', 'user_pw']

class UserProfileForm(forms.ModelForm):
    user_name = forms.CharField(max_length=100)
    user_birthdate = forms.DateField()
    user_email = forms.EmailField()
    user_phone_no = forms.CharField(max_length=100)

    class Meta:
        model = UserProfile
        fields = ['user_name','user_email', 'user_phone_no', 'user_birthdate', 'location']

class UserJobInfoForm(forms.ModelForm):
    user_job = forms.CharField(max_length=100)
    user_classification = forms.CharField(max_length=100)
    user_income = forms.FloatField()

    class Meta:
        model = UserJobInfo
        fields = ['user_job', 'user_classification', 'user_income']