# Copyright: Michael Wood 2019
# Web: http://michaelwood.me.uk
# License: LICENSE.txt

from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from db_yqn import api, custom_api

app_name = "yqn_api"

urlpatterns = [
    path('Posts/', api.PostList.as_view()),
    path('Post/<int:pk>/', api.PostDetail.as_view()),
    path('Post/<int:pk>/comments/', api.CommentsPost.as_view()),
    path('XMLFeeds/', api.XMLFeedList.as_view()),
    path('XMLFeed/<int:pk>/', api.XMLFeedDetail.as_view()),
    path('Twitters/', api.TwitterList.as_view()),
    path('Twitter/<int:pk>/', api.TwitterDetail.as_view()),
    path('Instagrams/', api.InstagramList.as_view()),
    path('Instagram/<int:pk>/', api.InstagramDetail.as_view()),

    path('GroupPages/', api.GroupPagesList.as_view()),
    path('GroupPage/<int:pk>', api.GroupPageDetail.as_view()),
    path('GroupPage/<int:pk>/images', api.GroupPageDetailImages.as_view()),
    path('GroupRedirectPages/', api.GroupPagesRedirectList.as_view()),

    path('EventsLocations/', api.EventsLocationList.as_view()),
    path('EventsLocation/<int:pk>', api.EventsLocationDetail.as_view()),

    path('Venues/', api.VenueList.as_view(), name="venues"),

    path('Events/', api.EventList.as_view()),
    path('Event/<int:pk>', api.EventDetail.as_view()),

    path('Regions/', api.RegionList.as_view()),

    path('EventsAtVenue/', api.EventsAtVenue.as_view()),
    path('EventsAtRegion/', api.EventsAtRegion.as_view()),

    path('Contact/', custom_api.Contact.as_view()),
    path('Upload/', custom_api.Upload.as_view(), name="media-upload"),
]

urlpatterns = format_suffix_patterns(urlpatterns)