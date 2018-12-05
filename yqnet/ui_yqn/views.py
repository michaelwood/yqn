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

import datetime
from db_yqn.models import Post, Twitter, GroupPage, Event, EventsLocation, Venue


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

        twitter = Twitter.objects.all()
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

class EventView(EventsView):
    template_name = "event.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['id'] = kwargs['pk']

        return context


class MapView(EventsView):
    template_name = "map.html"

class EventsListingView(EventsView):
    template_name = "events_listings.html"

class EventsAtVenueView(EventsView):
    template_name = "events_at_venue.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['id'] = kwargs['pk']

        return context


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
    success_url = "?"

    def get_object(self):
        return self.request.user

# TEMP TODO this
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

class AboutView(TemplateView):
    template_name = "about.html"

class PrivacyView(TemplateView):
    template_name = "privacy.html"