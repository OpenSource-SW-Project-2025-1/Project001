from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.views.generic.edit import FormView

class UserLoginView(FormView):
    template_name = 'accounts/login.html'
    form_class = AuthenticationForm
    success_url = '/'  # 로그인 성공 시 이동할 페이지

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super().form_valid(form)
