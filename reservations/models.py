from django.db import models
from django.utils import timezone
from core.models import AbstractTimeStampedModel


class Reservation(AbstractTimeStampedModel):
    """Reservation Model Definition"""
    STATUS_CHOICES = list(zip(['pending', 'confirmed', 'canceled'], ['Pending', 'Confirmed', 'Canceled']))

    status = models.CharField(choices=STATUS_CHOICES, max_length=12, default='pending')
    guest = models.ForeignKey('users.User', models.CASCADE)
    room = models.ForeignKey('rooms.Room', models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()

    def in_progress(self):
        now = timezone.now().date()
        return now >= self.check_in and now <= self.check_out

    def is_finished(self):
        now = timezone.now().date()
        return now > self.check_out

    in_progress.boolean = True
    is_finished.boolean = True

    def __str__(self):
        return f'{self.room}-{self.check_in}'
