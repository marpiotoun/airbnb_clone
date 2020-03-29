import datetime
from django import template
from reservations import models as reservation_models
register = template.Library()

@register.simple_tag
def is_booked(room, day):
    if day == '':
        return
    try:
        day = datetime.datetime(year=day.year, month=day.month, day=day.day)
        reservation_models.BookedDay.objects.get(day=day, reservation__room=room)
        return True
    except reservation_models.BookedDay.DoesNotExist:
        return False
