from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models


# Register your models here.


@admin.register(models.User)
class CustomUserAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + (
        ('Custom Profile', {
            "fields": ('avatar', 'gender', 'bio', 'birthDate', 'language', 'currency', 'superHost', 'login_method')
        }),
    )
    list_filter = UserAdmin.list_filter + ("superHost", 'login_method')

    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "is_active",
        "language",
        "currency",
        "superHost",
        "is_staff",
        "is_superuser",
        "email_verified",
        "email_verify_key",
        "login_method"
    )
    search_fields = UserAdmin.search_fields + ('^last_name', )