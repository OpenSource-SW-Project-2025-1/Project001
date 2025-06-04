from django import forms
from .models import UserID, UserProfile, UserJobInfo
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password

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

#로그인 확인 폼
class UserLoginForm(forms.Form):
    user_id = forms.CharField(label="아이디")
    user_pw = forms.CharField(label="비밀번호", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        user_id = cleaned_data.get("user_id")
        user_pw = cleaned_data.get("user_pw")

        try:
            user = UserID.objects.get(user_id=user_id)
            if not check_password(user_pw, user.user_pw):
                raise forms.ValidationError("비밀번호가 올바르지 않습니다.")
            cleaned_data['user'] = user
        except UserID.DoesNotExist:
            raise forms.ValidationError("존재하지 않는 아이디입니다.")

        return cleaned_data
