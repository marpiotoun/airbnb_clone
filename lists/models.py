from django.db import models
from core.models import AbstractTimeStampedModel


class List(AbstractTimeStampedModel):
    """List Model Definition"""
    name = models.CharField(max_length=100)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    room = models.ManyToManyField('rooms.Room')

    def __str__(self):
        return self.name

    def count_rooms(self):
        return self.room.count()
    count_rooms.short_description = 'Number of Rooms'