from django.core.management.base import BaseCommand, CommandError
from django.contrib.admin.utils import flatten
from django_seed import Seed

import lists.models as list_models
import rooms.models as room_models
import users.models as user_models
import random

NAME = 'lists'


class Command(BaseCommand):
    help = f"This command creates {NAME}"

    def add_arguments(self, parser):
        parser.add_argument('--number', type=int, default=1, help=f"How many {NAME} you want to create")

    def handle(self, *args, **options):
        number = options.get('number')
        seeder = Seed.seeder()
        rooms = room_models.Room.objects.all()
        seeder.add_entity(list_models.List, number, {
            'user': lambda x: random.choice(user_models.User.objects.all())
        })
        created_list = seeder.execute()
        created_clear = flatten(list(created_list.values()))
        for pk in created_clear:
            list_model = list_models.List.objects.get(pk=pk)
            to_add = rooms[random.randint(0, 5):random.randint(6, 30)]
            list_model.room.add(*to_add)
        self.stdout.write(self.style.SUCCESS(f"{number} {NAME} created"))