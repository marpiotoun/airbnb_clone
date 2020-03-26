from django.http import Http404
from django.views import View
from django.views.generic import ListView, DetailView, UpdateView
# from django.views.generic import View
# from django.core.paginator import Paginator
from django.shortcuts import render
from django_countries import countries
from . import models
from users.mixin import LoggedInOnlyMixin
# from . import forms


# 3
class HomeView(ListView):

    """Home View Model Definition"""

    model = models.Room
    paginate_by = 15
    paginate_orphans = 5
    ordering = "created"


class RoomDetail(DetailView):

    """Room Detail View Definition"""

    model = models.Room


# class SearchView(View):
#
#     """Search View Definition"""
#
#     def get(self, request):
#
#         country = request.GET.get("country")
#         # filter_args = {}
#
#         if country:
#
#             form = forms.SearchForm(request.GET)
#
#             if form.is_valid():
#
#                 city = form.cleaned_data.get("city"),
#                 country = form.cleaned_data.get("country"),
#                 room_type = form.cleaned_data.get("room_type"),
#                 price = form.cleaned_data.get("price"),
#                 guests = form.cleaned_data.get("guests"),
#                 bedrooms = form.cleaned_data.get("bedrooms"),
#                 beds = form.cleaned_data.get("beds"),
#                 baths = form.cleaned_data.get("baths"),
#                 instant = form.cleaned_data.get("instant"),
#                 super_host = form.cleaned_data.get("super_host"),
#                 amenities = form.cleaned_data.get("amenities"),
#                 facilities = form.cleaned_data.get("facilities")
#                 filter_args = {}
#                 if city is not 'Anywhere':
#                     filter_args["city__startswith"] = city
#                     filter_args['Country'] = country
#                 if room_type is not None:
#                     filter_args['room_type'] = room_type
#                 if price is not None:
#                     filter_args['price__lte'] = price
#                 if guests is not None:
#                     filter_args['guests__gte'] = guests
#                 if bedrooms is not None:
#                     filter_args['bedrooms__gte'] = bedrooms
#                 if beds is not None:
#                     filter_args['beds__gte'] = beds
#                 if baths is not None:
#                     filter_args['baths__gte'] = baths
#                 if instant is True:
#                     filter_args['instance_booking'] = True
#                 if super_host is True:
#                     filter_args['host__superHost'] = True
#                 for amenity in amenities:
#                     filter_args["amenity"] = amenity
#                 for facility in facilities:
#                     filter_args["facility"] = facility
#                 qs = models.Room.objects.filter(**filter_args)
#
#                 paginator = Paginator(qs, 10, orphans=5)
#
#                 page = request.GET.get('page', 1)
#
#                 rooms = paginator.get_page(page)
#                 return render(request, 'rooms/search.html', {'form': form, 'rooms': rooms})
#         else:
#             form = forms.SearchForm()
#         # rooms = models.Room.objects.filter(**filter_args)
#         return render(request, 'rooms/search.html', {'form': form})


# function-based search -1
def search(request):

    # Get objects from DB
    city = request.GET.get('city', 'Anywhere')
    try:
        city = str.capitalize(city)
    except TypeError:
        pass
    room_types = models.RoomType.objects.all()
    amenities = models.Amenity.objects.all()
    facilities = models.Facility.objects.all()

    # Get values from form
    country = request.GET.get('country', 'KR')
    try:
        room_type = int(request.GET.get('room_type'))
    except TypeError as e:
        room_type = 0
    try:
        price = int(request.GET.get('price', 0))
    except ValueError as e:
        price = 0
    try:
        guests = int(request.GET.get('guests', 0))
    except ValueError as e:
        guests = 0
    try:
        bedrooms = int(request.GET.get('bedrooms', 0))
    except ValueError as e:
        bedrooms = 0
    try:
        beds = int(request.GET.get('beds', 0))
    except ValueError as e:
        beds = 0
    try:
        baths = int(request.GET.get('baths', 0))
    except ValueError as e:
        baths = 0
    instant = bool(request.GET.get('instant', False))
    super_host = bool(request.GET.get('super_host', False))
    s_amenities = list(map(int, request.GET.getlist('amenity')))
    s_facilities = list(map(int, request.GET.getlist('facility')))

    # Context=
    form = {
        's_city': city,
        's_country': country,
        's_room_type': room_type,
        's_price': price,
        's_guests': guests,
        's_bedrooms': bedrooms,
        's_beds': beds,
        's_baths': baths,
        's_amenities': s_amenities,
        's_facilities': s_facilities,
        's_instant': instant,
        's_super_host': super_host,
    }
    choices = {
        'countries': countries,
        'room_types': room_types,
        'amenities': amenities,
        'facilities': facilities
    }

    filter_args = {}
    if city is not 'Anywhere':
        filter_args["city__startswith"] = city
    filter_args['Country'] = country
    if room_type != 0:
        filter_args['room_type__pk'] = room_type
    if price != 0:
        filter_args['price__lte'] = price
    if guests != 0:
        filter_args['guests__gte'] = guests
    if bedrooms != 0:
        filter_args['bedrooms__gte'] = bedrooms
    if beds != 0:
        filter_args['beds__gte'] = beds
    if baths != 0:
        filter_args['baths__gte'] = baths
    if instant is True:
        filter_args['instance_booking'] = True
    if super_host is True:
        filter_args['host__superHost'] = True
    if len(s_amenities) > 0:
        for s_pk in s_amenities:
            filter_args["amenity__pk"] = int(s_pk)
    if len(s_facilities) > 0:
        for s_pk in s_facilities:
            filter_args["facility__pk"] = int(s_pk)

    rooms = models.Room.objects.filter(**filter_args)
    return render(request, 'rooms/search.html', {**form, **choices,
        'rooms': rooms,
        })


class EditRoom(LoggedInOnlyMixin, UpdateView):
    model = models.Room
    template_name = 'rooms/edit_room.html'
    fields = ('name', 'description', 'Country', 'city', 'address', 'bedrooms', 'beds', 'baths', 'guests', 'price', 'instance_booking', 'room_type', 'amenity', 'facility', 'house_rule')
    def get_object(self, queryset=None):
        room = super().get_object(queryset=queryset)
        if room.host.pk != self.request.user.pk:
            raise Http404()
        return room


class EditPhotosView(LoggedInOnlyMixin, DetailView):
    model = models.Room
    template_name = 'rooms/edit_photos.html'

    def get_object(self, queryset=None):
        room = super().get_object(queryset=queryset)
        if room.host.pk != self.request.user.pk:
            raise Http404()
        return room



# def room_detail(request, pk):
#     try:
#         room = models.Room.objects.get(pk=pk)
#         return render(request, 'rooms/room_detail.html', context={
#             'room': room
#         })
#     except models.Room.DoesNotExist as e:
#         raise Http404()




# 2
# def all_rooms(request):
#     page = request.GET.get('page', 1)
#     room_list = models.Room.objects.all()
#     paginator = Paginator(room_list, 10, orphans=3)
#     try:
#         return render(request, 'rooms/room_list.html', context={
#             'rooms': paginator.page(page),
#         })
#     except EmptyPage:
#         return redirect('/')




# 1
# def all_rooms(request):
#     page = request.GET.get('page', 1)
#     page = int(page or 1)
#     page_size = 10
#     limit = page_size * page
#     offset = limit-page_size
#     all_rooms = models.Room.objects.all()[offset : limit]
#     end_page = ceil(models.Room.objects.count()/page_size)
#     return render(request, 'rooms/room_list.html', context={
#         'rooms': all_rooms,
#         'page': page,
#         'end_page': end_page,
#         'page_range': range(1, end_page+1)
#     })