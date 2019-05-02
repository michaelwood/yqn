# Copyright: Michael Wood 2019
# Web: http://michaelwood.me.uk
# License: LICENSE.txt


from rest_framework import serializers
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.utils import timezone
from db_yqn.models import Post, XMLFeed, Instagram, Twitter, GroupPage, Region
from db_yqn.models import EventsLocation, Venue, Event, GroupPageMedia, UserMedia
from db_yqn.models import Sources

# If defining 'fields' remember to add field for id

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','first_name')
        read_only_fields = ('id', 'first_name')

class UserMediaSerializer(serializers.ModelSerializer):
    url = serializers.CharField(read_only=True, source="get_url")
    class Meta:
        model = UserMedia
        fields = ('url',)


class PostSerializerBase(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)
    publish_date = serializers.DateTimeField(format="%d %b %H:%M", read_only=True)
    media = UserMediaSerializer(read_only=True)
    comments_count = serializers.IntegerField(read_only=True, source="comments.count")

    class Meta:
        model = Post
        fields = ('id', 'title', 'media', 'user', 'source','text', 'publish_date', 'ext_url','thumbnail_computed', 'url', 'ext_author', 'comments_count')
        read_only_fields = ('user','source','publish_date', 'ext_author', 'ext_url','thumbnail', 'thumbnail_computed', 'url', 'media')

class PostSerializerNoComments(PostSerializerBase):
    class Meta(PostSerializerBase.Meta):
        pass

class PostSerializerWComments(PostSerializerBase):
    comments = PostSerializerBase(many=True, read_only=True)

    class Meta(PostSerializerBase.Meta):
        fields = PostSerializerBase.Meta.fields + ("comments",)

class CommentPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ("text",)

class XMLFeedSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)

    class Meta:
        model = XMLFeed
        fields = ("__all__")
        read_only_fields = ('user','enabled')

class SocialMediaAccSerializer(serializers.ModelSerializer):
   # user = UserSerializer(read_only=True)

    class Meta:
        fields = ("username",)
        #read_only_fields = ('user',)

class TwitterSerializer(SocialMediaAccSerializer):
    class Meta(SocialMediaAccSerializer.Meta):
        model = Twitter

class InstagramSerializer(SocialMediaAccSerializer):
    class Meta(SocialMediaAccSerializer.Meta):
        model = Instagram

class GroupPagesSerializer(serializers.ModelSerializer):

    go_to = serializers.CharField(read_only=True, source="get_edit_link")
    url = serializers.CharField(read_only=True, source="get_url")

    class Meta:
        model = GroupPage
        fields = ("id", "title", "slug", "body", "email", "go_to", "url")
        read_only_fields = ('users', "body")

class GroupPageRedirectSerializer(serializers.ModelSerializer):
    body = serializers.CharField(label="Description")
    class Meta:
        model = GroupPage
        fields = ("id", "title", "slug", "redirect", "body")
        read_only_fields = ('users',)

class GroupPageSerializer(serializers.ModelSerializer):

    go_to = serializers.CharField(read_only=True, source="get_edit_link")
    url = serializers.CharField(read_only=True, source="get_url")

    class Meta:
        model = GroupPage
        fields = ("id", "go_to", "url", "title", "slug", "redirect", "last_modified", "body", "last_updated_by")
        read_only_fields = ('users',"redirect","last_updated_by")

class GroupPageDetailsSerializer(serializers.ModelSerializer):
    url = serializers.CharField(read_only=True, source="get_url")

    class Meta:
        model = GroupPage
        fields = ("id", "title", "url")

class VenueSerializer(serializers.ModelSerializer):

    url = serializers.URLField(read_only=True, source="get_url")

    class Meta:
        model = Venue
        fields = ("id", "title", "address", "postcode", "lat", "lng", "url")

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields  = ("__all__")

class EventsLocationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    # These details are for special objects curated for display use
    # We deliberately leave in the original fields for Update/Create useage
    # All _details should be read_only
    venue_details = VenueSerializer(read_only=True, source="get_venue")
    group_page_details = GroupPageDetailsSerializer(read_only=True, source="get_group_page")
    region_details = RegionSerializer(read_only=True, source="get_region")

    has_email = serializers.BooleanField(read_only=True)

    def validate(self, data):
        if not 'region' in data and not 'venue' in data:
            raise serializers.ValidationError({ "Region or Venue" : "The event must happen somewhere! Please provide either a Venue or a Region"})

        if not 'url' in data and not 'group_page' in data:
            raise serializers.ValidationError({ "Link or Group Page" : "For people to find out about the events please provide either a Group page or an external Link or both"})

        return data

    class Meta:
        model = EventsLocation
        fields = ("id","title", "url", "group_page", "venue", "user", "venue_details", "group_page_details", "has_email", "region", "private", "region_details")

class EventsSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    # venue field is used for introspection of fk by add-object-model so use a
    # custom field for the deserialised venue
    venue_details = VenueSerializer(read_only=True, source="get_venue")

    url = serializers.CharField(read_only=True, source="get_url")

    # Anti-pattern Date formatting is so much better in Python than JS so do this here
    display_day = serializers.CharField(read_only=True, source="get_display_day")
    display_date_time_start = serializers.CharField(read_only=True, source="get_display_date_time_start")
    display_date_time_end = serializers.CharField(read_only=True, source="get_display_date_time_end")

    has_email = serializers.BooleanField(read_only=True)
    group_page_details = GroupPageDetailsSerializer(read_only=True, source="get_group_page")

    class Meta:
        model = Event
        fields = ("__all__")

#### Nested Events for EventsAtVenue
# As this model isn't the primary model for the API we are also filtering the model
# here.

class FutureEventsListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        if not self.context['request'].user.is_authenticated:
            data = data.exclude(private=True)
        else:
            data = data.all()

        data = data.filter(date_time_start__gte=timezone.now())

        return super().to_representation(data)

class NestedFutureEventsSerializer(serializers.ModelSerializer):

    url = serializers.CharField(read_only=True, source="get_url")
    start = serializers.CharField(read_only=True, source="get_display_date_time_start")
    end = serializers.CharField(read_only=True, source="get_display_date_time_end")

    class Meta:
        model = Event
        list_serializer_class = FutureEventsListSerializer
        fields = ("id", "title", "url", "start" , "end")
####


#### Nested EventsLocation for EventsAtVenue and EventsAtRegion

# As this model isn't the primary model for the API we are filtering the model
# here
class EventsLocationListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        if not self.context['request'].user.is_authenticated:
            data = data.exclude(private=True)
        else:
            data = data.all()

        return super().to_representation(data)

class NestedEventsLocationSerializer(serializers.ModelSerializer):
    group_page = GroupPageDetailsSerializer(read_only=True)

    class Meta:
        model = EventsLocation
        lists_serializer_class = EventsLocationListSerializer
        fields = ("id", "title", "url", "group_page")

####


class EventsAtVenue(serializers.ModelSerializer):
    eventslocation_set = NestedEventsLocationSerializer(many=True, read_only=True)
    url = serializers.URLField(read_only=True, source="get_url")
    event_set = NestedFutureEventsSerializer(read_only=True, many=True)

    class Meta:
        model = Venue
        fields = ("__all__")


class ImageFileSerializer(serializers.ModelSerializer):

    # These are for tinyMCE to consume
    title = serializers.CharField(read_only=True, source="get_title")
    value = serializers.CharField(read_only=True, source="get_url")

    class Meta:
        model = GroupPageMedia
        fields  = ("title", "value")


class EventsAtRegion(serializers.ModelSerializer):
    eventslocation_set = NestedEventsLocationSerializer(many=True, read_only=True)

    class Meta:
        model = Region
        fields = ("__all__")
