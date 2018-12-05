# Copyright: Michael Wood 2019
# Web: http://michaelwood.me.uk
# License: LICENSE.txt
from django.http import HttpResponseBadRequest

from rest_framework import generics, permissions, mixins
import django_filters.rest_framework

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.views import APIView
from rest_framework import filters


from db_yqn.models import Post, Sources, XMLFeed, Twitter, Instagram, GroupPage
from db_yqn.models import EventsLocation, Venue, Event, GroupPageMedia

from db_yqn.rest_serialiser import PostSerializer, XMLFeedSerializer
from db_yqn.rest_serialiser import InstagramSerializer, TwitterSerializer
from db_yqn.rest_serialiser import GroupPagesSerializer
import db_yqn.rest_serialiser as YqnSerializer
import db_yqn.api_filters as YqnFilters

from db_yqn.api_permissions import IsOwnerOrReadOnly, IsOwner, IsInOwners
from db_yqn.api_metadata import SimpleWithFkModelMetadata

import re


# All the REST API view endpoints

# field search prefix reference django-filters
#
#      lookup_prefixes = {
#        '^': 'istartswith',
#        '=': 'iexact',
#        '@': 'search',
#        '$': 'iregex',
#   }


class FilterRequiredMixin(object):
    """ Requires the request to contains either a filter or a search query 
        This avoids sending large unfiltered data sets
    """
    def get(self, request, *args, **kwargs):

        filter_or_search_present = False

        filter_fields = []

        if hasattr(self, "filter_class"):
            filter_fields += list(self.filter_class.Meta.fields)

        if hasattr(self, "filter_fields"):
            filter_fields += list(self.filter_fields)

        if hasattr(self, "search_fields"):
            filter_or_search_present = (request.GET.get("search") and len(request.GET.get("search")) > 0)

        # Filter out empty key values
        def valid_key(key):
            if request.GET.get(key):
                return key
            return ""

        keys = " ".join([valid_key(key) for key in self.request.GET.keys()])

        if filter_fields:
            for field in filter_fields:
                if re.search(field, keys):
                    filter_or_search_present = True
                    break 

        if not filter_or_search_present:
            return HttpResponseBadRequest("Query Required")

        return super().get(request, *args, **kwargs)


class PostListPaginator(LimitOffsetPagination):
    default_limit = 10

class PostList(generics.ListCreateAPIView):
    description = "Add a Post"

    serializer_class = PostSerializer
    filter_fields = ('source', 'user', 'id')
    pagination_class = PostListPaginator
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)

    def get_queryset(self):
        if self.request.user and self.request.user.is_authenticated:
            return Post.objects.order_by("-publish_date")

        return Post.objects.exclude(private=True).order_by("-publish_date")


    def perform_create(self, serializer):
        serializer.save(user=self.request.user, source=Sources.LOCAL)


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)


class XMLFeedList(generics.ListCreateAPIView):
    description = "Automatically publishes posts from your Blog, Podcast or News feed."
    queryset = XMLFeed.objects.all()
    serializer_class = XMLFeedSerializer
    permission_classes = (IsOwner,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class XMLFeedDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = XMLFeed.objects.all()
    serializer_class = XMLFeedSerializer
    permission_classes = (IsOwner,)


class TwitterList(generics.ListCreateAPIView):
    description = "Add your twitter username"
    queryset = Twitter.objects.all()
    serializer_class = TwitterSerializer
    permission_classes = (IsOwner,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TwitterDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Twitter.objects.all()
    serializer_class = TwitterSerializer
    permission_classes = (IsOwner,)

class InstagramList(generics.ListCreateAPIView):
    queryset = Instagram.objects.all()
    serializer_class = InstagramSerializer
    permission_classes = (IsOwner,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class InstagramDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Instagram.objects.all()
    serializer_class = InstagramSerializer
    permission_classes = (IsOwner,)

class GroupPagesList(generics.ListCreateAPIView):
    description = "Add a dedicated web page for your group"
    queryset = GroupPage.objects.order_by("title")
    serializer_class = GroupPagesSerializer
    permission_classes = (IsOwner,)

    search_fields = ("^title",)
    filter_backends = (filters.SearchFilter,)

    def perform_create(self, serializer):
        serializer.save(users=[self.request.user])

class GroupPagesRedirectList(generics.ListCreateAPIView):
    description = "Create a link which redirects to your group's existing website"
    queryset = GroupPage.objects.all()
    serializer_class = YqnSerializer.GroupPageRedirectSerializer
    permission_classes = (IsOwner,)

class GroupPageDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = GroupPage.objects.all()
    serializer_class = YqnSerializer.GroupPageSerializer
    permission_classes = (IsInOwners,)

    def perform_update(self, serializer):
        serializer.save(last_updated_by=self.request.user)

class GroupPageDetailImages(generics.ListAPIView):
    serializer_class = YqnSerializer.ImageFileSerializer
    permission_classes = (IsInOwners,)

    def get_queryset(self, *args, **kwargs):
        return GroupPageMedia.objects.filter(page=self.kwargs.get("pk"))

class EventsLocationList(FilterRequiredMixin, generics.ListCreateAPIView):
    description = "Add a link to your own events"

    metadata_class = SimpleWithFkModelMetadata
    serializer_class = YqnSerializer.EventsLocationSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)

    filter_fields = ('user', 'id',)
    
    search_fields = ('$title', '$venue__title')
    filter_backends = (filters.SearchFilter, django_filters.rest_framework.DjangoFilterBackend)

    def get_queryset(self):
        if self.request.user and self.request.user.is_authenticated:
            return EventsLocation.objects.order_by("title")

        return EventsLocation.objects.exclude(private=True).order_by("title")


    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class EventList(FilterRequiredMixin, generics.ListCreateAPIView):
    description = "Add your event listing"
    filter_class = YqnFilters.EventListFilter

    search_fields = ('^title',)
    filter_backends = (filters.SearchFilter, django_filters.rest_framework.DjangoFilterBackend)

    metadata_class = SimpleWithFkModelMetadata
    serializer_class = YqnSerializer.EventsSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)

    def get_queryset(self):
        if self.request.user and self.request.user.is_authenticated:
            return Event.objects.all()

        return Event.objects.exclude(private=True)


    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class VenueList(FilterRequiredMixin, generics.ListCreateAPIView):
    description = "Add a venue for your events"
    queryset = Venue.objects.order_by("title")
    search_fields = ('^title',)
    filter_backends = (filters.SearchFilter,)
    metadata_class = SimpleWithFkModelMetadata
    serializer_class = YqnSerializer.VenueSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)


class EventsAtVenue(FilterRequiredMixin, generics.ListAPIView):
#    queryset = Venue.objects.all()
    serializer_class = YqnSerializer.EventsAtVenue
    permission_classes = (permissions.AllowAny,)

    filter_class = YqnFilters.EventsAtVenueFilter

    def get_queryset(self):
        return Venue.objects.all()

        queryset = []

        for venue in venues:
            queryset.append(venue)

        return queryset


#        if not self.request.user.is_authenticated:
