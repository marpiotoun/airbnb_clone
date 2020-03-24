from django import forms
from django.contrib.auth.forms import UserCreationForm
from . import models


class LoginForm(forms.Form):

    email = forms.EmailField(widget=forms.EmailInput(attrs=({'placeholder': 'Email'})))
    password = forms.CharField(widget=forms.PasswordInput(attrs=({'placeholder': 'Password'})))

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        try:
            user = models.User.objects.get(email=email)
            if user.check_password(password):
                return self.cleaned_data
            else:
                self.add_error("password", forms.ValidationError('Wrong Password'))
        except models.User.DoesNotExist:
            self.add_error('email', forms.ValidationError('Email does not exist'))

    # def clean_email(self):
    #     email = self.cleaned_data.get('email')
    #     try:
    #         models.User.objects.get(email=email)
    #         return email
    #     except models.User.DoesNotExist:
    #         raise forms.ValidationError("User does not Exist")
    # def clean_password(self):
    #     email = self.cleaned_data.get('email')
    #     password = self.cleaned_data.get('password')
    #     try:
    #         user = models.User.objects.get(email=email)
    #         if user.check_password(password):
    #             return password
    #         else:
    #             raise forms.ValidationError("Wrong Password")
    #     except models.User.DoesNotExist:
    #         raise forms.ValidationError("")


class SignUpForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
        }

    password = forms.CharField(widget=forms.PasswordInput(attrs=({'placeholder': 'Password'})))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=({'placeholder': 'Confirm Password'})), label='Confirm Password')

    def clean_email(self):
        email = self.cleaned_data.get("email")
        try:
            models.User.objects.get(email=email)
            raise forms.ValidationError(
                "That email is already taken", code="existing_user"
            )
        except models.User.DoesNotExist:
            return email

    def clean_password1(self):
        password = self.cleaned_data.get('password')
        password1 = self.cleaned_data.get('password1')
        if password != password1:
            raise forms.ValidationError("Password confirmation does not match")
        else:
            return password

    def save(self, *args, **kwargs):
        username = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        user = super().save(commit=False)
        user.username = username
        user.set_password(password)
        user.save()


# class SignUpForm(forms.Form):
#     first_name = forms.CharField(max_length=50)
#     last_name = forms.CharField(max_length=50)
#     email = forms.EmailField()
#     password = forms.CharField(widget=forms.PasswordInput)
#     password1 = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')
#
#     def clean_email(self):
#         email = self.cleaned_data.get('email')
#         try:
#             models.User.objects.get(email=email)
#             raise forms.ValidationError('Email already exist')
#         except models.User.DoesNotExist:
#             return email
#
#     def clean_password1(self):
#         password = self.cleaned_data.get('password')
#         password1 = self.cleaned_data.get('password1')
#         if password != password1:
#             raise forms.ValidationError("Password confirmation does not match")
#         else:
#             return password
#
#     def form_valid(self, form):
#         pass
#
#     def save(self):
#         first_name = self.cleaned_data.get('first_name')
#         last_name = self.cleaned_data.get('last_name')
#         email = self.cleaned_data.get('email')
#         password = self.cleaned_data.get('password')
#         user = models.User.objects.create_user(email, email, password)
#         user.first_name = first_name
#         user.last_name = last_name
#         user.save()
