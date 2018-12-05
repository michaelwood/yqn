# Copyright: Michael Wood 2019
# Web: http://michaelwood.me.uk
# License: LICENSE.txt
from django.views.generic.base import TemplateView
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin

from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

import os
import magic

from db_yqn.models import GroupPageMedia, UserMedia, GroupPage

class MediaBrowser(TemplateView, LoginRequiredMixin):
    template_name = "media_browser.html"