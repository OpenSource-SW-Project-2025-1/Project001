from django import forms
from .models import UserID, UserProfile, UserJobInfo
from django.contrib.auth.hashers import make_password

class SignUpForm(forms.ModelForm):
    class Meta:
        model = UserID
        fields = ['user_id', 'user_pw']
        widgets = {
            'user_pw': forms.PasswordInput()
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_pw = make_password(self.cleaned_data['user_pw'])
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['user_name','user_email', 'user_phone_no', 'user_birthdate', 'location']

class UserJobInfoForm(forms.ModelForm):
    class Meta:
        model = UserJobInfo
        fields = ['user_job', 'user_classification', 'user_income']