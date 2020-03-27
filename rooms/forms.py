# from django import forms
# from django_countries.fields import CountryField
# from . import models
#
#
# class SearchForm(forms.Form):
#
#     city = forms.CharField(initial="Anywhere", empty_value='')
#     country = CountryField(default='KR').formfield()
#     room_type = forms.ModelChoiceField(empty_label="Any Kind", queryset=models.RoomType.objects.all(), required=False)
#     price = forms.IntegerField(required=False)
#     guests = forms.IntegerField(required=False)
#     bedrooms = forms.IntegerField(required=False)
#     beds = forms.IntegerField(required=False)
#     baths = forms.IntegerField(required=False)
#     instant = forms.BooleanField(required=False)
#     super_host = forms.BooleanField(required=False)
#     amenities = forms.ModelMultipleChoiceField(
#         queryset=models.Amenity.objects.all(),
#         widget=forms.CheckboxSelectMultiple,
#         required=False
#     )
#     facilities = forms.ModelMultipleChoiceField(
#         queryset=models.Facility.objects.all(),
#         widget=forms.CheckboxSelectMultiple,
#         required=False
#     )

from django import forms
from . import models


class CreatePhotoForm(forms.ModelForm):
    class Meta:
        model = models.Photo
        fields = ("caption", "file")

    def save(self, pk, *args, **kwargs):
        photo = super().save(commit=False)
        room = models.Room.objects.get(pk=pk)
        photo.room = room
        photo.save()


class CreateRoomForm(forms.ModelForm):
    class Meta:
        model = models.Room
        fields = (
            'name',
            'description',
            'Country',
            'city',
            'address',
            'bedrooms',
            'beds',
            'baths',
            'guests',
            'check_in',
            'check_out',
            'price',
            'instance_booking',
            'room_type',
            'amenity',
            'facility',
            'house_rule'
        )

    def save(self, *args, **kwargs):
        room = super().save(commit=False)
        return room
