from django.core.management.base import BaseCommand, CommandError
from django_seed import Seed
from django.contrib.admin.utils import flatten
import reviews.models as review_models
import rooms.models as room_models
import users.models as user_models
import random

class Command(BaseCommand):
    help = 'This command creates many fake reviews'

    def add_arguments(self, parser):
        parser.add_argument("--number", default=1, type=int, help="How many reviews do you want to create")

    def handle(self, *args, **options):
        number = options.get('number', 1)
        seeder = Seed.seeder()

        all_users = user_models.User.objects.all()
        all_rooms = room_models.Room.objects.all()

        seeder.add_entity(review_models.Review, number, {
            'user': lambda x: random.choice(all_users),
            'room': lambda x: random.choice(all_rooms),
            'accuracy': lambda x: random.randint(1, 6),
            'communication': lambda x: random.randint(1, 6),
            'cleanliness': lambda x: random.randint(1, 6),
            'location': lambda x: random.randint(1, 6),
            'check_in': lambda x: random.randint(1, 6),
            'value': lambda x: random.randint(1, 6)
        })
        seeder.execute()
        self.stdout.write(self.style.SUCCESS(f'{number} Reviews has been created'))
