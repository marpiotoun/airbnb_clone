from django.contrib import admin
from . import models


@admin.register(models.Reservation)
class ReservationAdmin(admin.ModelAdmin):
    """Reservation Admin Definition"""
    list_display = (
        "room",
        'guest',
        'check_in',
        'check_out',
        'status',
        'in_progress',
        'is_finished'
    )

    list_filter = ('status',)