from django.db import models
from core.models import AbstractTimeStampedModel


class Conversation(AbstractTimeStampedModel):
    """Conversation Model Definition"""
    participant = models.ManyToManyField('users.User', blank=True)

    def __str__(self):
        usernames = []
        for user in self.participant.all():
            usernames.append(user.username)
        return " , ".join(usernames)

    def count_message(self):
        return self.messages.count()
    count_message.short_description = 'Number Of Messages'

    def count_participants(self):
        return self.participant.count()
    count_participants.short_description = 'Number Of Participants'

class Message(AbstractTimeStampedModel):
    """Message Model Definition"""
    message = models.TextField()
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    conversation = models.ForeignKey('Conversation', related_name='messages', on_delete=models.CASCADE)
    def __str__(self):
        return f'{self.user} : {self.message}'

