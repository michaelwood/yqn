# Copyright: Michael Wood 2019
# Web: http://michaelwood.me.uk
# License: LICENSE.txt

from rest_framework import generics
from django_filters import rest_framework as filters
from db_yqn.models import Event, Venue, Region


class EventListFilter(filters.FilterSet):

    date_time_start = filters.DateTimeFromToRangeFilter()
    id = filters.NumberFilter

    class Meta:
        model = Event
        fields = ['date_time_start', 'id']

class EventsAtVenueFilter(filters.FilterSet):

    lng = filters.RangeFilter()
    lat = filters.RangeFilter()

    id = filters.NumberFilter

    class Meta:
        model = Venue
        fields = ['lat','lng', 'id']


class EventsAtRegionFilter(filters.FilterSet):

    lng_tl = filters.RangeFilter()
    lat_tl = filters.RangeFilter()

    lng_br = filters.RangeFilter()
    lat_br = filters.RangeFilter()

    id = filters.NumberFilter

    class Meta:
        model = Region
        fields = ['lat_tl','lng_tl','lat_br','lng_br', 'id']