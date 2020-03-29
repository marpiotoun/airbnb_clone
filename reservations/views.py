import datetime
from django.views.generic import View
from django.contrib import messages
import rooms.models as room_models
from . import models
from django.shortcuts import redirect, reverse


class CreateError(Exception):
    pass


def create(request, room, year, month, day):
    try:
        date_obj = datetime.datetime(year=year, month=month, day=day)
        room = room_models.Room.objects.get(pk=room)
        models.BookedDay.objects.get(day=date_obj, reservation__room=room)
        raise CreateError
    except (room_models.Room.DoesNotExist, CreateError):
        messages.error("Can't book this room")
        return redirect(reverse("core:home"))
    except models.BookedDay.DoesNotExist:
        reservation = models.Reservation.objects.create(
            guest=request.user,
            room=room,
            check_in=date_obj,
            check_out=date_obj + datetime.timedelta(day=1)
        )
        return redirect(reverse('reservation:detail', kwargs={'pk': reservation.pk}))


class ReservationDetailView(View):
    pass