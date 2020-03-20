import os
import requests
from django.http import HttpResponseRedirect
from django.views import View
from django.views.generic import FormView
from django.shortcuts import redirect, reverse
from django.urls import reverse_lazy
from django.core.files.base import ContentFile
from . import forms, models
from django.contrib.auth import authenticate, login, logout


class LoginView(FormView):
    # content_type = None
    # extra_context = None
    form_class = forms.LoginForm
    # http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']
    # initial = {}
    # prefix = None
    # _lazy means that it call data when it is used
    success_url = reverse_lazy('core:home')
    # template_engine = None
    template_name = 'users/login.html'

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)


def logout_view(request):
    logout(request)
    return redirect(reverse('core:home'))


class SignUpView(FormView):
    form_class = forms.SignUpForm
    success_url = reverse_lazy('core:home')
    template_name = 'users/signup.html'
    initial = {
        'first_name': 'Sangsoo',
        'last_name': 'Han',
        'email': 'plus470@naver.com'
    }
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
                raise GithubException()
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
                        raise GithubException()
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
                return redirect(reverse('core:home'))
            else:
                raise GithubException()
            return redirect(reverse("user:login"))
        else:
            raise GithubException()
        return redirect(reverse("core:home"))
    except KakaoException:
        # Send error msg
        return redirect(reverse("core:home"))


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
            raise KakaoException
        access_token = token_json.get('access_token')
        profile_request = requests.get(f'https://kapi.kakao.com/v2/user/me', headers={
            'Authorization': f'Bearer {access_token}'
        })
        profile_json = profile_request.json()
        kakao_account = profile_json.get('kakao_account')
        user_info = {'login_method': 'kakao', 'email_verified': True}
        email = kakao_account.get('email')
        if email is None:
            print('email')
            raise KakaoException
        user_info.update({'username': email, 'email': email})
        properties = profile_json.get('properties')
        nickname = properties.get('nickname')
        if nickname is not None:
            user_info.update({'first_name': nickname})
        profile_image = properties.get('profile_image', None)

        try:
            user = models.User.objects.get(email=email)
            if user.login_method != 'kakao':
                raise KakaoException
        except models.User.DoesNotExist:
            user = models.User.objects.create(**user_info)
            user.set_unusable_password()
            user.save()
            if profile_image is not None:
                photo_request = requests.get(profile_image)
                user.avatar.save(f'{nickname}-avatar', ContentFile(photo_request.content))
        login(request, user)
        return redirect(reverse('core:home'))
    except KakaoException:
        return redirect(reverse('user:login'))

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
"""
{'login': 'marpiotoun', 'id': 60564849, 'node_id': 'MDQ6VXNlcjYwNTY0ODQ5', 'avatar_url': 'https://avatars0.githubusercontent.com/u/60564849?v=4', 'gravatar_id': '', 'url': 'https://api.github.com/users/marpiotoun', 'html_url': 'https://github.com/marpiotoun', 'fo
llowers_url': 'https://api.github.com/users/marpiotoun/followers', 'following_url': 'https://api.github.com/users/marpiotoun/following{/other_user}', 'gists_url': 'https://api.github.com/users/marpiotoun/gists{/gist_id}', 'starred_url': 'https://api.github.com/us
ers/marpiotoun/starred{/owner}{/repo}', 'subscriptions_url': 'https://api.github.com/users/marpiotoun/subscriptions', 'organizations_url': 'https://api.github.com/users/marpiotoun/orgs', 'repos_url': 'https://api.github.com/users/marpiotoun/repos', 'events_url':
'https://api.github.com/users/marpiotoun/events{/privacy}', 'received_events_url': 'https://api.github.com/users/marpiotoun/received_events', 'type': 'User', 'site_admin': False, 'name': None, 'company': None, 'blog': '', 'location': None, 'email': 'plus470@gmail
.com', 'hireable': None, 'bio': None, 'public_repos': 6, 'public_gists': 0, 'followers': 0, 'following': 0, 'created_at': '2020-02-02T07:00:44Z', 'updated_at': '2020-03-19T09:13:33Z', 'private_gists': 0, 'total_private_repos': 0, 'owned_private_repos': 0, 'disk_u
sage': 92684, 'collaborators': 0, 'two_factor_authentication': False, 'plan': {'name': 'free', 'space': 976562499, 'collaborators': 0, 'private_repos': 10000}}
"""