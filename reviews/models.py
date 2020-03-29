from django.db import models
from core.models import AbstractTimeStampedModel


class Review(AbstractTimeStampedModel):

    """Review Model Definition"""

    # REVIEW
    review = models.TextField()
    # RATING
    RATING_CHOICES = list(zip([1,2,3,4,5], [1,2,3,4,5]))
    accuracy = models.IntegerField(choices=RATING_CHOICES)
    communication = models.IntegerField(choices=RATING_CHOICES)
    cleanliness = models.IntegerField(choices=RATING_CHOICES)
    location = models.IntegerField(choices=RATING_CHOICES)
    check_in = models.IntegerField(choices=RATING_CHOICES)
    value = models.IntegerField(choices=RATING_CHOICES)
    # USER
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    # ROOM
    room = models.ForeignKey('rooms.Room', related_name='reviews', on_delete=models.CASCADE)

    class Meta:
        ordering = ('-created', )

    def __str__(self):
        return f'{self.review}-{self.room}'

    def rating(self):
        return(
            round(
                (self.accuracy + self.communication + self.cleanliness + self.location + self.check_in + self.value)/6,
                2
            )
        )
