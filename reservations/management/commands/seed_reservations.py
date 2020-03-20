from django.core.management.base import BaseCommand
from django.contrib.admin.utils import flatten
from django_seed import Seed
from datetime import datetime, timedelta
import reservations.models as reservation_models
import rooms.models as room_models
import users.models as user_models
import random


NAME = 'reservations'

class Command(BaseCommand):
    help = f"This command creates {NAME}"

    def add_arguments(self, parser):
        parser.add_argument('--number', type=int, default=1, help=f"How many {NAME} you want to create")

    def handle(self, *args, **options):
        number = options.get('number')
        seeder = Seed.seeder()
        users = user_models.User.objects.all()
        rooms = room_models.Room.objects.all()
        seeder.add_entity(reservation_models.Reservation, number, {
            'status': lambda x: random.choice(['pending', 'confirmed', 'canceled']),
            'guest': lambda x: random.choice(users),
            'room': lambda x: random.choice(rooms),
            'check_in': lambda x: datetime.now(),
            'check_out': lambda x: datetime.now() + timedelta(days=random.randint(3, 25))
        })
        seeder.execute()
        self.stdout.write(self.style.SUCCESS(f"{number} {NAME} created"))