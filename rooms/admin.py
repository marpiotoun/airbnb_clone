from django.contrib import admin
from . import models
from django.utils.html import mark_safe

@admin.register(models.RoomType, models.Amenity, models.Facility, models.HouseRule)
class ItemAdmin(admin.ModelAdmin):

    """Item Admin Definition"""
    list_display = (
        'name',
        'used_by'
    )
    def used_by(self, obj):
        return obj.rooms.count()


@admin.register(models.Photo)
class PhotoAdmin(admin.ModelAdmin):

    """Photo Admin Definition"""

    list_display = ('__str__', 'get_thumbnail')

    def get_thumbnail(self, obj):
        return mark_safe(f'<img width=100px src=\'{obj.file.url}\'>')
    get_thumbnail.short_description = 'Thumbnail'


class PhotoInline(admin.StackedInline):

    model = models.Photo


@admin.register(models.Room)
class RoomAdmin(admin.ModelAdmin):

    """Room Admin Definition"""

    inlines = (PhotoInline,)
    ordering = ('created',)
    fieldsets = (
        (
            "Basic Info",
            {"fields": ('name', 'description', 'Country', 'city', 'address', 'price',)}
        ),
        (
            "Times",
            {"fields": ('check_in', 'check_out', 'instance_booking',)}
        ),
        (
            "More About the Space",
            {'fields': ('bedrooms', 'beds', 'baths', 'guests',)}
        ),
        (
            "Spaces",
            {'fields': ('amenity', 'facility', 'house_rule')}
        ),
        (
            "Last Details",
            {'fields': ('host',)}
        )
    )

    list_display = (
        'name',
        'description',
        'Country',
        'city',
        'address',
        'price',
        'bedrooms',
        'beds',
        'baths',
        'guests',
        'check_in',
        'check_out',
        'instance_booking',
        'count_amenities',
        'count_photos',
        'rating',
    )

    list_filter = (
        'instance_booking',
        'host__superHost',
        'room_type',
        'amenity',
        'facility',
        'house_rule',
        'city',
        'Country')

    filter_horizontal = (
        'amenity',
        'facility',
        'house_rule'
    )

    raw_id_fields = ("host", )

    # def save_model(self, request, obj, form, change):
    #     print(obj, change, form)
    #     super().save_model(request, obj, form, change)

    def count_amenities(self, obj):
        return(obj.amenity.count())

    def count_photos(self, obj):
        return(obj.photos.count())
    search_fields = ('name', 'city', 'host__username',)