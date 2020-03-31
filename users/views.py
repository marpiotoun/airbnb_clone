import os
import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, password_validation
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.views.generic import FormView, DetailView, UpdateView
from django.shortcuts import redirect, reverse
from django.urls import reverse_lazy
from django.utils import translation
from django.utils.translation import gettext, gettext_lazy as _
from django import forms as django_forms
from . import forms, models
from users.mixin import LoggedOutOnlyMixin, LoggedInOnlyMixin, EmailLoginOnlyMixin


class LoginView(LoggedOutOnlyMixin, FormView):
    form_class = forms.LoginForm
    template_name = 'users/login.html'

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
            messages.success(self.request, f'Welcome back {user.first_name}')
        return super().form_valid(form)

    def get_success_url(self):
        next_arg = self.request.GET.get('next')
        if next_arg is not None:
            return next_arg
        else:
            return reverse('core:home')


def logout_view(request):
    messages.info(request, f"See you later {request.user.first_name}")
    logout(request)
    return redirect(reverse('core:home'))


class SignUpView(FormView):
    form_class = forms.SignUpForm
    success_url = reverse_lazy('core:home')
    template_name = 'users/signup.html'

    def form_valid(self, form):
        form.save()
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        user.verify_email()
        return super().form_valid(form)

def complete_verification(request, key):
    try:
        user = models.User.objects.get(email_verify_key=key)
        user.email_verified = True
        user.email_verify_key = ''
        user.save()
        """to do : add success message - see django message framework"""
    except models.User.DoesNotExist:
        """add some error msg"""
        pass
    return redirect(reverse('core:home'))

def github_login(request):
    client_id = os.environ.get('CLIENT_ID')
    redirect_uri = 'http://127.0.0.1:8000/user/login/github/callback/'
    return redirect(f'https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=read:user')


class GithubException(Exception):
    pass

def github_callback(request):
    try:
        client_id = os.environ.get('CLIENT_ID')
        client_secret = os.environ.get('CLIENT_SECRET')
        code = request.GET.get('code', None)
        if code is not None:
            token_request = requests.post(f"https://github.com/login/oauth/access_token?client_id={client_id}&client_secret={client_secret}&code={code}",
                                    headers={"Accept":"application/json"})
            token_json = token_request.json()
            error = token_json.get("error")
            if error is not None:
                raise GithubException("Something wrong with your login with github")
            access_token = token_json.get('access_token')
            profile_request = requests.get('https://api.github.com/user',
                                       headers={'Authorization': f'token {access_token}', "Accept": "application/json"})
            profile_json = profile_request.json()
            username = profile_json.get('login', None)

            if username is not None:
                name = profile_json.get('name')
                email = profile_json.get('email')
                bio = profile_json.get('bio')
                try:
                    user = models.User.objects.get(email=email)
                    if user.login_method != 'github':
                        raise GithubException(f"Your email already exist. try: {user.login_method}")
                except models.User.DoesNotExist:
                    user = models.User.objects.create(
                        username=email,
                        email=email,
                        first_name=name,
                        bio=bio,
                        login_method='github'
                    )
                    user.set_unusable_password()
                    user.save()
                login(request, user)
                messages.success(request, f'Welcome back {user.first_name}')
                return redirect(reverse('core:home'))
            else:
                raise GithubException("Your Github account doesn't have your name. Try with other method")
            return redirect(reverse("user:login"))
        else:
            raise GithubException("Can't get your code")
        return redirect(reverse("user:login"))
    except GithubException as e:
        messages.error(request, e)
        return redirect(reverse("user:login"))


def kakao_login(request):
    app_key = os.environ.get('K_APP_KEY')
    redirect_uri = os.environ.get('K_REDIRECT_URL')
    return redirect(f'https://kauth.kakao.com/oauth/authorize?client_id={app_key}&redirect_uri={redirect_uri}&response_type=code')


class KakaoException(Exception):
    pass


def kakao_callback(request):
    try:
        code = request.GET.get('code')
        app_key = os.environ.get('K_APP_KEY')
        redirect_uri = os.environ.get('K_REDIRECT_URL')
        token_request = requests.post(f'https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={app_key}&redirect_uri={redirect_uri}&code={code}')
        token_json = token_request.json()
        error = token_json.get('error', None)
        if error is not None:
            raise KakaoException("Can't get authorization code")
        access_token = token_json.get('access_token')
        profile_request = requests.get(f'https://kapi.kakao.com/v2/user/me', headers={
            'Authorization': f'Bearer {access_token}'
        })
        profile_json = profile_request.json()
        kakao_account = profile_json.get('kakao_account')
        user_info = {'login_method': 'kakao', 'email_verified': True}
        email = kakao_account.get('email')
        if email is None:
            raise KakaoException("please also give me your Email")
        user_info.update({'username': email, 'email': email})
        properties = profile_json.get('properties')
        nickname = properties.get('nickname')
        if nickname is not None:
            user_info.update({'first_name': nickname})
        profile_image = properties.get('profile_image', None)

        try:
            user = models.User.objects.get(email=email)
            if user.login_method != 'kakao':
                raise KakaoException(f"Please log in with: {user.login_method}")
        except models.User.DoesNotExist:
            user = models.User.objects.create(**user_info)
            user.set_unusable_password()
            user.save()
            if profile_image is not None:
                photo_request = requests.get(profile_image)
                user.avatar.save(f'{nickname}-avatar', ContentFile(photo_request.content))
        login(request, user)
        messages.success(request, f'Welcome back {user.first_name}')
        return redirect(reverse('core:home'))
    except KakaoException as e:
        messages.error(request, e)
        return redirect(reverse('user:login'))


class UserProfileView(LoggedInOnlyMixin, DetailView):
    model = models.User
    context_object_name = 'user_obj'
    template_name = 'users/profile.html'


class UpdateProfileView(LoggedInOnlyMixin, SuccessMessageMixin, UpdateView):
    model = models.User
    fields = ('first_name', 'last_name', 'bio', 'language')
    template_name = 'users/update_profile.html'
    context_object_name = 'user'
    success_message = 'Profile updated'

    def get_object(self, queryset=None):
        return self.request.user


class PasswordChangeForm(SetPasswordForm):
    """
    A form that lets a user change their password by entering their old
    password.
    """
    error_messages = {
        **SetPasswordForm.error_messages,
        'password_incorrect': _("Your old password was entered incorrectly. Please enter it again."),
    }
    old_password = django_forms.CharField(
        label=_("Old password"),
        strip=False,
        widget=django_forms.PasswordInput(attrs={'placeholder': 'Current password', 'autocomplete': 'current-password', 'autofocus': True}),
    )
    new_password1 = django_forms.CharField(
        label=_("New password"),
        widget=django_forms.PasswordInput(attrs={'placeholder': 'New password', 'autocomplete': 'new-password'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = django_forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=django_forms.PasswordInput(attrs={'placeholder': 'Comfirm New password', 'autocomplete': 'new-password'}),
    )
    field_order = ['old_password', 'new_password1', 'new_password2']


class UpdatePasswordView(EmailLoginOnlyMixin, LoggedInOnlyMixin, PasswordChangeView):
    template_name = 'users/update_password.html'
    form_class = PasswordChangeForm

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        return self.request.user.get_absolute_url()


@login_required
def switch_host(request):
    try:
        del request.session['is_hosting']
    except KeyError:
        request.session['is_hosting'] = True
    return redirect(request.META.get('HTTP_REFERER'))


def switch_language(request):
    lang = request.GET.get("lang", None)
    if lang is not None:
        request.session[translation.LANGUAGE_SESSION_KEY] = lang
    return HttpResponse(status=200)


# from django.views import View
# from django.shortcuts import render, redirect, reverse
# from . import forms
# from django.contrib.auth import authenticate, login, logout
#
#
# class LoginView(View):
#
#     def get(self, request):
#         form = forms.LoginForm()
#         return render(request, 'users/login.html', {'form': form})
#
#     def post(self, request):
#         form = forms.LoginForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data.get("email")
#             password = form.cleaned_data.get("password")
#             user = authenticate(request, username=email, password=password)
#             if user is not None:
#                 login(request, user)
#                 return redirect(reverse("core:home"))
#         return render(request, 'users/login.html', {'form': form})
#
#
# def logout_view(request):
#     logout(request)
#     return redirect(reverse('core:home'))

