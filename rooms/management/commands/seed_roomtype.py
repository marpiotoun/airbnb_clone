from django.core.management.base import BaseCommand, CommandError
from rooms.models import RoomType



class Command(BaseCommand):
    help = 'This command creates many Room types'

    def handle(self, *args, **options):
        room_type = [
            '주택', '아파트', '게스트', '스위트', '게스트', '용', '별채', '담무소', '(이탈리아)로프트', '방갈로', '샬레', '저택', '전원주택', '키클라데스', '주택(그리스)', '타운하우스', '통나무집', '트룰로', '펜션(한국)'
        ]

        for r in room_type:
            RoomType.objects.create(name=r)
        self.stdout.write(self.style.SUCCESS('Room types has been created'))

