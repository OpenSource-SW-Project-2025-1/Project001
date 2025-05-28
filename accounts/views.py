from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from .forms import SignUpForm, UserUpdateForm, ProfileUpdateForm
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic.detail import DetailView
from django.contrib.auth.models import User  # 또는 CustomUser
from django.contrib.auth.mixins import LoginRequiredMixin

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
    success_url = reverse_lazy('home')  # 홈으로 리디렉션

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages

def custom_logout(request):
    logout(request)
    messages.success(request, "로그아웃 되었습니다.")
    return redirect('home')  # 또는 다른 URL

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, "로그아웃되었습니다.")
        return super().dispatch(request, *args, **kwargs)


@login_required
def profile_edit(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('accounts:profile', pk=request.user.pk)
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'pk': request.user.pk
    }

    return render(request, 'accounts/profile_edit.html', context)

@login_required
def profile_view(request):
    user = request.user
    return render(request, 'accounts/profile.html', {'user': user})


@login_required
def profile_delete(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        return redirect('home')
    return render(request, 'accounts/profile_delete.html')

class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'profile_user'