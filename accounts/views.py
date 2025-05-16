from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from .forms import SignUpForm

class UserLoginView(FormView):
    template_name = 'accounts/login.html'
    form_class = AuthenticationForm
    success_url = '/home/'  # 로그인 성공 시 이동할 페이지

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super().form_valid(form)

class UserSignUpView(FormView):
    template_name = 'accounts/signup.html'
    form_class = SignUpForm
    success_url = reverse_lazy('/home/')  # 홈으로 리디렉션

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)