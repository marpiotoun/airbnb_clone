from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect, reverse
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin


class LoggedOutOnlyMixin(UserPassesTestMixin):

    permission_denied_message = 'You are already logged in'

    def test_func(self):
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        messages.info(self.request, self.get_permission_denied_message())
        return redirect(reverse('core:home'))


class LoggedInOnlyMixin(LoginRequiredMixin):
    login_url = reverse_lazy("user:login")
    permission_denied_message = 'You have to login'


class EmailLoginOnlyMixin(UserPassesTestMixin):

    permission_denied_message = 'Your login method is not email'

    def test_func(self):
        return self.request.user.login_method == 'email'

    def handle_no_permission(self):
        messages.info(self.request, self.get_permission_denied_message())
        return redirect(reverse('core:home'))
