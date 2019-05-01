# Copyright: Michael Wood 2019
# Web: http://michaelwood.me.uk
# License: LICENSE.txt
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone, formats
from django.urls import reverse_lazy, resolve
from django.urls.exceptions import Resolver404
from django.core import validators
from django.core.exceptions import ValidationError

import bleach
import difflib

from settings_yqn import settings


# Rule - ForeignKey fields should be named lower case and underscores of their
# class name. e.g. test = models.ForeignKey()

class Sources(object):
    LOCAL = 0
    BLOG = 1
    PODCAST = 2
    NEWS = 3
    COMMENT = 4

    SOURCE_TYPES = (
        (LOCAL, "Local Post"),
        (BLOG, "Blog"),
        (PODCAST, "Podcast"),
        (NEWS, "News"),
        (COMMENT, "Comment"),
    )

    # All but the Local post
    REMOTE_SOURCE_TYPES = SOURCE_TYPES[1:]

    @staticmethod
    def get_name(source):
        return Sources.SOURCE_TYPES[source][1]


class XMLFeed(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)

    url = models.URLField(help_text="Url should be an Atom or RSS feed",
                          unique=True,
                          verbose_name="Link (URL)")

    name = models.CharField(max_length=100)
    enabled = models.BooleanField(default=False)

    source = models.IntegerField(choices=Sources.REMOTE_SOURCE_TYPES,
                                 help_text="The 'source' or category for this feed",
                                 verbose_name="Category")

    manual_thumbnail = models.URLField(
        help_text="Url to a thumbnail img, used if the feed doesn't provide one automatically",
        blank=True, null=True)

    def __str__(self):
        return "%s - %s" % (Sources.get_name(self.source), self.url)


def user_dir(instance, filename):
    return "user/%s/%s" % (instance.user.pk, filename)

class UserMedia(models.Model):
    file_upload = models.FileField(upload_to=user_dir)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_url(self):
        return self.file_upload.url


class Post(models.Model):

    publish_date = models.DateTimeField("publish", name="publish_date", default=timezone.now)
    text = models.TextField()
    title = models.CharField(max_length=100, default="", blank=True, null=True, help_text="Title or Subject of Post")
    thumbnail = models.URLField(blank=True, null=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ext_author = models.CharField(max_length=100, null=True, blank=True)

    source = models.IntegerField(choices=Sources.SOURCE_TYPES,
                                 default=Sources.LOCAL)

    ext_url = models.URLField(blank=True)
    xml_feed = models.ForeignKey(XMLFeed, on_delete=models.CASCADE, null=True, blank=True)

    private = models.BooleanField(default=False, help_text="Only show this post to logged in users")

    media = models.ForeignKey(UserMedia, on_delete=models.CASCADE, null=True, blank=True)
    comments = models.ManyToManyField("self", symmetrical=False, blank=True)

    def thumbnail_computed(self):

        if self.thumbnail:
            return self.thumbnail

        if self.xml_feed and self.xml_feed.manual_thumbnail:
            return self.xml_feed.manual_thumbnail

        avatar = UserMedia.objects.filter(user=self.user, file_upload__contains=settings.AVATAR_PREFIX).first()
        if avatar:
            return avatar.file_upload.url

        return "%s/imgs/fav/android-chrome-192x192.png" % settings.STATIC_URL

    def url(self):
        if self.ext_url:
            return self.ext_url

        return reverse_lazy("posts") + "#post-%s" % self.id


    def save(self, *args, **kwargs):

        bleach.ALLOWED_ATTRIBUTES['img'] = ['src', 'title', 'alt']

        self.text = bleach.clean(
            self.text,
            strip=True,
            tags=bleach.ALLOWED_TAGS + ['br', 'p', 'img'],
            attributes=bleach.ALLOWED_ATTRIBUTES,
            )

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        for comment in self.comments.all():
            comment.delete()

        super().delete(*args, **kwargs)


    def __str__(self):
        return "%s %s" % (self.id ,self.title)


class Twitter(models.Model):
    username = models.CharField(help_text="Enter your Twitter username", unique=True, max_length=200)
    user = models.ForeignKey(User, null=True, default=None, on_delete=models.CASCADE)

    def __str__(self):
        return self.username

class Instagram(models.Model):
    username = models.CharField(help_text="Enter your Instagram username (without @)", unique=True, max_length=200)
    user = models.ForeignKey(User, null=True, default=None, on_delete=models.CASCADE)

    def __str__(self):
        return self.username


def validate_no_slug_clash(value):
    """ Don't allow a slug to clash with our existing urls """
    valid = False
    try:
        match  = resolve("/%s/" % value)
        # If the match is to the user pages then that's OK
        if 'user-pages' in match.url_name:
            valid = True

    except Resolver404:
        valid = True

    if not valid:
        raise ValidationError("Entered slug clashes with our own urls")


class GroupPage(models.Model):

    slug_help = "This sets up a short link to the page e.g. 'my-group-name' results in http://yqnet.uk/my-group-name"
    title = models.CharField(max_length=400)

    slug = models.SlugField(max_length=200,
                            unique=True,
                            help_text=slug_help,
                            validators=[validators.validate_slug, validate_no_slug_clash])

    redirect = models.URLField(blank=True, null=True,
     help_text="Provide a Link to redirect people to your website",
     verbose_name="Link")
    body = models.TextField(default="", blank=True)
    last_modified = models.DateTimeField(auto_now=True)
    email = models.EmailField(help_text="Email address for enquiries", null=True, blank=True)
    users = models.ManyToManyField(User)
    last_updated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.DO_NOTHING, related_name="page_updater")

    def has_email(self):
        if self.email and len(self.email) > 0:
            return True
        return False

    def can_user_edit(self, username):
        if self.users.filter(username=username).count() > 0:
            return True

        return False

    def get_edit_link(self):
        if not self.redirect:
            return reverse_lazy("user-page-edit", args=(self.slug,))
        return ""

    def get_url(self):
        if self.redirect:
            return self.redirect

        return reverse_lazy("user-pages", args=(self.slug,))

    def significant_change(self, new_body):
        """ perform a unified diff and to see whether this change is significant """
        old_body = GroupPage.objects.get(pk=self.pk).body

        diff = difflib.unified_diff(old_body, new_body)

        length = len([line for line in diff])

        if length > 100:
            return True

        return False


    def save(self, *args, **kwargs):
        try:
            updated_or_created = "updated"
            do_post = False

            if self.pk is None:
                updated_or_created = "added"
                do_post = True
                user = self.users.first()
            elif self.significant_change(self.body):
                do_post = True
                user = self.last_updated_by

            if do_post:
                Post.objects.update_or_create(
                        title="%s %s their page" % (self.title, updated_or_created),
                        text="The group page %s has been %s - Check it out!" % (self.title, updated_or_created),
                        user=user,
                        source=Sources.LOCAL,
                        ext_url=self.get_url(),
                )
        # Making a post is optional and we don't want any errors
        # to fail the save on this object
        except Exception as e:
            print(e)
            pass

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Region(models.Model):
    title = models.CharField(max_length=200, unique=True, verbose_name="Region name")

    lat_tl = models.FloatField(max_length=200, verbose_name="Latitude top left")
    lng_tl = models.FloatField(max_length=200, verbose_name="Longitude top left")

    lat_br = models.FloatField(max_length=200, verbose_name="Latitude bottom right")
    lng_br = models.FloatField(max_length=200, verbose_name="Longitude bottom right")


    def __str__(self):
        return self.title


# Note Venues are all public but can have private events/eventlocations
class Venue(models.Model):
    title = models.CharField(max_length=200, unique=True, verbose_name="Venue name")
    address = models.TextField()
    postcode = models.CharField(max_length=20, help_text="Must be valid UK postcode")

    # We try and do the postcode to lat,lng lookup client side so set a default value
    # If we weren't able to then a default value is provided to allow the validation
    # and to mark it for geocodeing later on
    lat = models.FloatField(max_length=200, default=-99)
    lng = models.FloatField(max_length=200, default=-99)

    def get_url(self):
        return reverse_lazy("venue", args=(self.id,))

    def __str__(self):
        return self.title


    # TODO lookup geocode
    #def save(self, *args, **kwargs):
    #    if self.lat == -99 or self.lng == -99:
    #        print("Need to get location looked up")
#
#        super().save(*args, **kwargs)


class Event(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField(null=True, blank=True)
    description = models.TextField()
    date_time_start = models.DateTimeField()
    date_time_end = models.DateTimeField()
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, verbose_name="Venue name", help_text="e.g. Westminster Quaker Meeting")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    private = models.BooleanField(default=False, help_text="Only show this event to logged in users")
    email = models.EmailField(null=True, blank=True, help_text="Email address for enquiries")
    group_page = models.ForeignKey(GroupPage, null=True, on_delete=models.DO_NOTHING, help_text="Associate this Event with a Group")

    out_format = "%a %d %b %Y at %H:%M"

    def save(self, *args, **kwargs):
    #TODO Do we have a standardised bleach ?
        bleach.ALLOWED_ATTRIBUTES['img'] = ['src', 'title', 'alt']

        self.description = bleach.clean(
            self.description,
            strip=True,
            tags=bleach.ALLOWED_TAGS + ['br', 'p', 'img'],
            attributes=bleach.ALLOWED_ATTRIBUTES,
            )


        # We're doing an insert i.e. a new event then make a post about it
        if self.pk is None:
            try:
                Post.objects.create_or_update(
                    title="New event %s" % self.title,
                    text="%s %s" % (self.get_display_date_time_start(), self.description),
                    user=self.user,
                    source=Sources.LOCAL,
                    ext_url=self.get_url(),
                    private=self.private
                )
            # Making a post is optional and we don't want any errors
            # to fail the save on this object
            except Exception:
               pass



        super().save(*args, **kwargs)

    def get_group_page(self):
        return self.group_page

    def get_display_day(self):
        # https://docs.djangoproject.com/en/2.1/ref/templates/builtins/#std:templatefilter-date
        return formats.date_format(self.date_time_start, format="jS")

    def get_display_date_time_start(self):
        return self.date_time_start.strftime(self.out_format)

    def get_display_date_time_end(self):
        return self.date_time_end.strftime(self.out_format)

    def get_venue(self):
        return self.venue

    def get_url(self):
        if self.url:
            return self.url

        return reverse_lazy("event", args=(self.id,))

    def has_email(self):
        if self.email and len(self.email) > 0:
            return True
        return False

    def __str__(self):
        return self.title


class EventsLocation(models.Model):
    # Addional validation logic is provided at the API level to ensure venue
    # or region and group page or url are provided.
    title = models.CharField(max_length=200, help_text="e.g. Quaker Meeting")
    group_page = models.ForeignKey(GroupPage, null=True, on_delete=models.DO_NOTHING, help_text="Associate this event with a Group")
    url = models.URLField(help_text="External link to find out more about your events. e.g. http://example.com/events", blank=True, null=True, verbose_name="Link (URL)")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    private = models.BooleanField(default=False, help_text="Only show this information to logged in users")
    email = models.EmailField(null=True, blank=True, help_text="If left blank enquiries will be forwarded to your current login email")

    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Venue name", help_text="Lookup an existing Venue or Add new")
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True, help_text="If your events happen in multiple places in a Region rather than at a single Venue. e.g. London Area or Add new")

    def get_venue(self):
        return self.venue

    def get_group_page(self):
        return self.group_page

    def get_region(self):
        return self.region

    def has_email(self):
        if self.email and len(self.email) > 0:
            return True
        return False

    def save(self, *args, **kwargs):

        # We're doing an insert i.e. a new event then make a post about it
        if self.pk is None:
            try:
                Post.objects.create_or_update(
                    title="New events %s" % self.title,
                    text="",
                    user=self.user,
                    source=Sources.LOCAL,
                    ext_url=self.url,
                    private=self.private
                )
            # Making a post is optional and we don't want any errors
            # to fail the save on this object
            except Exception:
               pass

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# Note file sizes should be limited using the http server
# e.g. Apache2 LimitRequestBody 102400 (100k)

def group_dir(instance, filename):
    return "group/%s/%s" % (instance.page.slug, filename)


class GroupPageMedia(models.Model):
    file_upload = models.FileField(upload_to=group_dir)
    page = models.ForeignKey(GroupPage, on_delete=models.CASCADE)

    def get_title(self):
        return self.file_upload.name.split("/")[-1:][0]

    def get_url(self):
        return self.file_upload.url

# Register models with django /admin site
from django.contrib import admin
admin.site.register(Post)
admin.site.register(Twitter)
admin.site.register(GroupPage)
admin.site.register(Instagram)
admin.site.register(XMLFeed)
admin.site.register(EventsLocation)
admin.site.register(Venue)
admin.site.register(Event)
admin.site.register(UserMedia)
admin.site.register(GroupPageMedia)
admin.site.register(Region)
