# Copyright: Michael Wood 2019
# Web: http://michaelwood.me.uk
# License: LICENSE.txt
from django.views.generic.base import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy

import datetime
from db_yqn.models import Post, Twitter, GroupPage, Event, EventsLocation, Venue
from db_yqn.models import UserMedia
from settings_yqn import settings


# Not in use
class IndexView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        posts = Post.objects.order_by('-id').exclude(private=True)[:3]
        events = Event.objects.order_by('-id').exclude(private=True)[:3]
        events_location = EventsLocation.objects.exclude(private=True).order_by('-id')[:3]
        pages = GroupPage.objects.order_by("-last_updated")[:3]

        context['posts'] = posts
        context['events'] = events
        context['events_location'] = events_location
        context['pages'] = pages

        return context
# End not in use

# Posts
class PostsView(TemplateView):
    template_name = "posts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['total_posts'] = Post.objects.count()
        return context

class TwittersView(PostsView):
    template_name = "twitters.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        twitter = Twitter.objects.order_by('?')
        context['twitter'] = twitter

        return context

class InstagramView(PostsView):
    template_name = "instagram.html"

# End Posts

# TODO We'll probably do this more dynamically than in these templates

class EventsView(TemplateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        total = Event.objects.count()
        total = total + EventsLocation.objects.count()

        context['total_events'] = total
        return context

# Note these inherit from the EventsView which is why they're not
# direct templates
class EventView(EventsView):
    template_name = "event.html"

class MapView(EventsView):
    template_name = "map.html"

class EventsListingView(EventsView):
    template_name = "events_listings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if kwargs.get("slug"):
            context['group_page'] = GroupPage.objects.get(slug=kwargs['slug'])

        return context

class EventsAtVenueView(EventsView):
    template_name = "events_at_venue.html"

class GroupPageView(TemplateView):
    template_name = "user_page.html"
    page = None

    def get(self, request, *args, **kwargs):
        self.page = get_object_or_404(GroupPage, slug=kwargs['slug'])
        if self.page.redirect:
            return redirect(self.page.redirect)

        return super().get(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['user_can_edit'] = False
        context['user_can_edit'] = self.page.can_user_edit(self.request.user)

        context['page'] = self.page

        return context

class GroupPageEditView(GroupPageView, LoginRequiredMixin):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['editing'] = True

        return context


class GroupPagesView(TemplateView):
    template_name = "user_pages.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['pages'] = GroupPage.objects.all().order_by("-last_modified")
        context['origin'] = self.request.META['HTTP_HOST']

        return context

class UpdateUserDetailsView(UpdateView, LoginRequiredMixin):
    template_name = "update_userdetails.html"
    model = User
    fields = ['username','first_name', 'last_name', 'email']
    success_url = "?result=success"

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context['current_avatar'] = UserMedia.objects.get(user=self.request.user, file_upload__contains="yqn-avatar-").file_upload.url
        except UserMedia.DoesNotExist as e:
            print(e)
            context['current_avatar'] = settings.STATIC_URL + '/imgs/fav/android-chrome-192x192.png'

        return context

# TEMP TODO this. This is a clunky way to edit the permissions.
# Will be relaced once a proper ui is designed.
class GroupPageEditorsUpdate(UpdateView, LoginRequiredMixin):
    template_name = "update_grouppage_editors.html"
    fields = ['users']
    success_url = "?result=success"
    model = GroupPage

    def get_object(self, **kwargs):
        page = super().get_object(**kwargs)

        if not page.can_user_edit(self.request.user):
            raise PermissionDenied("User not allowed")

        return page