from django.contrib import messages
from django.shortcuts import redirect, reverse
from core import managers
from . import forms
import rooms.models as room_models


def create_review(request, room):
    if request.method == "POST":
        form = forms.CreateReviewForm(request.POST)
        room = room_models.Room.objects.get_or_none(pk=room)
        if not room:
            return redirect(reverse('core:home'))
        if form.is_valid():
            review = form.save()
            review.room = room
            review.user = request.user
            review.save()
            messages.success(request, 'Review uploaded')
            return redirect(reverse("room:detail", kwargs={'pk':room.pk}))
