import uuid
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.shortcuts import reverse

# Create your models here.
class User(AbstractUser):
    """Custom User Model"""

    GENDER_CHOICES = list(zip(['male', 'female'], ['Male', 'Female']))
    LANGUAGE_CHOICES = list(zip(['kr', 'en'], ['Korean', 'English']))
    CURRENCY_CHOICES = list(zip(['usd', 'krw'], ['USD', 'KRW']))
    LOGIN_CHOICES = list(zip(['email', 'github', 'kakao'], ['Email', 'Github', 'Kakao']))

    avatar = models.ImageField(upload_to='avatar', blank=True)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=10, blank=True)
    bio = models.TextField(blank=True, null=True)
    birthDate = models.DateField(default=timezone.now)
    language = models.CharField(choices=LANGUAGE_CHOICES, max_length=2, blank=True, default='kr')
    currency = models.CharField(choices=CURRENCY_CHOICES, max_length=3, blank=True, default='krw')
    email_verified = models.BooleanField(default=False)
    email_verify_key = models.CharField(max_length=20, default="", blank=True)
    superHost = models.BooleanField(default=False)
    login_method = models.CharField(choices=LOGIN_CHOICES, max_length=50, default='email')

    def verify_email(self):
        if self.email_verified is False:
            verify_key = uuid.uuid4().hex[:20]
            self.email_verify_key = verify_key
            html_message = render_to_string(
                "emails/verify_email.html", {"verify_key": verify_key}
            )
            send_mail(
                "Verify Airbnb Account",
                strip_tags(html_message),
                settings.EMAIL_FROM,
                [self.email],
                fail_silently=True,
                html_message=html_message
            )
            self.save()
        return

    def get_absolute_url(self):
        return reverse('user:profile', kwargs={'pk': self.pk})
