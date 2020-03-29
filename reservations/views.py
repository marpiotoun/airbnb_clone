import datetime
from django.http import Http404
from django.views.generic import View
from django.contrib import messages
import rooms.models as room_models
from . import models
from django.shortcuts import redirect, reverse, render
from reviews import forms as review_forms


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
            check_out=date_obj + datetime.timedelta(days=1)
        )
        return redirect(reverse('reservation:detail', kwargs={'pk': reservation.pk}))


class ReservationDetailView(View):
    def get(self, *args, **kwargs):
        pk = kwargs.get('pk')
        reservation = models.Reservation.objects.get_or_none(pk=pk)
        form = review_forms.CreateReviewForm()
        if not reservation or \
                (reservation.guest != self.request.user and reservation.room.host != self.request.user):
            raise Http404()

        return render(self.request, 'reservations/reservation_detail.html', {"reservation": reservation,
                                                                             "form": form})


def edit_reservation(request, pk, verb):
    reservation = models.Reservation.objects.get_or_none(pk=pk)
    if not reservation or (
        reservation.guest != request.user and reservation.room.host != request.user
    ):
        raise Http404()
    if verb == "confirm":
        reservation.status = models.Reservation.STATUS_CHOICES[1][1]
    elif verb == "cancel":
        reservation.status = models.Reservation.STATUS_CHOICES[2][1]
        models.BookedDay.objects.filter(reservation=reservation).delete()
    reservation.save()
    messages.success(request, "Reservation Updated")
    return redirect(reverse("reservation:detail", kwargs={"pk": reservation.pk}))