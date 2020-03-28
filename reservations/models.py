from django.db import models
from django.utils import timezone
from core.models import AbstractTimeStampedModel


class BookedDay(AbstractTimeStampedModel):

    day = models.DateField()
    reservation = models.ForeignKey('Reservation', related_name='booked_day', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Booked Day"
        verbose_name_plural = "Booked Days"

    def __str__(self):
        return str(self.day)+" at "+self.reservation.room.name


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

    def save(self, *args, **kwargs):
        if self.pk is None:
            start = self.check_in
            end = self.check_out
            difference = end - start
            is_already_booked = BookedDay.objects.filter(day__range=(start, end)).exists()
            if not is_already_booked:
                super().save(*args, **kwargs)
                for i in range(difference.days + 1):
                    day = start + timezone.timedelta(days=i)
                    BookedDay.objects.create(day=day, reservation=self)
                return
        return super().save()

        #
        #     for i in range(difference):
        #
        #     existing_book_already = Reservation.objects.filter(check_in=)
        # else:
        #     print('im old')
