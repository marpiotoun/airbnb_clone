from django.db import models
from django.urls import reverse
from django_countries import countries
from core import models as core_models


class AbstractItem(core_models.AbstractTimeStampedModel):
    """Item Model Definition"""
    name = models.CharField(max_length=100)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class RoomType(AbstractItem):
    """RoomType Model Definition"""
    class Meta:
        verbose_name = 'Room Type'


class Amenity(AbstractItem):
    """Amenity Model Definition"""
    class Meta:
        verbose_name_plural = 'Amenities'


class Facility(AbstractItem):
    """Facility Model Definition"""
    class Meta:
        verbose_name_plural = 'Facilities'


class HouseRule(AbstractItem):
    """HouseRule Model Definition"""
    class Meta:
        verbose_name = 'House Rule'


class Photo(core_models.AbstractTimeStampedModel):
    """Photo Model Definition"""
    caption = models.CharField(max_length=150)
    file = models.ImageField(upload_to='room_photos')
    room = models.ForeignKey('Room', related_name='photos', on_delete=models.CASCADE)

    def __str__(self):
        return self.caption


class Room(core_models.AbstractTimeStampedModel):
    """Room Model Definition"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    # LOCATION
    Country = models.CharField(choices=countries, max_length=100)
    city = models.TextField(blank=True)
    address = models.CharField(max_length=150)
    # OPTIONS
    bedrooms = models.IntegerField()
    beds = models.IntegerField()
    baths = models.IntegerField()
    # CHECKING
    guests = models.IntegerField()
    check_in = models.TimeField()
    check_out = models.TimeField()
    # PRICE
    price = models.IntegerField()
    # RESERVATION
    instance_booking = models.BooleanField(default=False)
    # HOST
    host = models.ForeignKey('users.User', related_name='rooms', on_delete=models.CASCADE)
    # Room Type
    room_type = models.ForeignKey('RoomType', related_name='rooms', on_delete=models.SET_NULL, null=True, blank=True)
    # Amenity
    amenity = models.ManyToManyField('Amenity', related_name='rooms', blank=True)
    # Facility
    facility = models.ManyToManyField('Facility', related_name='rooms', blank=True)
    # HouseRule
    house_rule = models.ManyToManyField('HouseRule', related_name='rooms', blank=True)

    #SAVE
    def save(self, *args, **kwargs):
        self.city = str.capitalize(self.city)
        super().save(*args, **kwargs)

    #RATING
    def rating(self):
        try:
            all_reviews = self.reviews.all()
            all_rating = 0
            for review in all_reviews:
                all_rating += review.rating()
            return round(all_rating/len(all_reviews),2)
        except ZeroDivisionError as e:
            return None

    def first_photo(self):
        try:
            photo, = self.photos.all()[:1]
        except ValueError:
            return None
        return photo.file.url

    def get_next_four_photo(self):
        try:
            photos = self.photos.all()[1:]
        except ValueError:
            return None
        return photos

    def get_absolute_url(self):
        return reverse("room:detail", kwargs={'pk': self.pk})

    def __str__(self):
        return self.name
