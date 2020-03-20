from django.core.management.base import BaseCommand, CommandError
from django_seed import Seed
from django.contrib.admin.utils import flatten
import rooms.models as room_models
from rooms.models import Room, RoomType
from users.models import User
import random

class Command(BaseCommand):
    help = 'This command creates many fake rooms'

    def add_arguments(self, parser):
        parser.add_argument("--number", default=1, type=int, help="How many users do you want to create")

    def handle(self, *args, **options):
        number = options.get('number', 1)
        seeder = Seed.seeder()

        all_users = User.objects.all()
        all_roomtypes = RoomType.objects.all()

        seeder.add_entity(Room, number,{
            'name': lambda x: seeder.faker.address(),
            'host': lambda x: random.choice(all_users),
            'room_type': lambda x: random.choice(all_roomtypes),
            'price': lambda x: 100*random.randint(100, 1000),
            'guests': lambda x: random.randint(1, 5),
            'bedrooms': lambda x: random.randint(1, 5),
            'beds': lambda x: random.randint(1, 5),
            'baths': lambda x: random.randint(1, 5)
        })
        created_photos = seeder.execute()
        created_clean = flatten(list(created_photos.values()))
        amenities = room_models.Amenity.objects.all()
        facilities = room_models.Facility.objects.all()
        rules = room_models.HouseRule.objects.all()
        for pk in created_clean:
            room = room_models.Room.objects.get(pk=pk)
            for i in range(3, random.randint(5, 7)):
                room_models.Photo.objects.create(
                    caption=seeder.faker.sentence(),
                    room=room,
                    file=f'/room_photos/{random.randint(1,31)}.webp'
                )
            for a in amenities:
                magic_number = random.randint(1, 15)
                if magic_number % 2 == 0:
                    room.amenity.add(a)
            for a in facilities:
                magic_number = random.randint(1, 15)
                if magic_number % 2 == 0:
                    room.facility.add(a)
            for a in rules:
                magic_number = random.randint(1, 15)
                if magic_number % 2 == 0:
                    room.house_rule.add(a)
        self.stdout.write(self.style.SUCCESS(f'{number} Room has been created'))
