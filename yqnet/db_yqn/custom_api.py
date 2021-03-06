# Copyright: Michael Wood 2019
# Web: http://michaelwood.me.uk
# License: LICENSE.txt
from django.views.generic.base import TemplateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.core import validators
from django.core.exceptions import ValidationError


import os
import magic
import json

from db_yqn.models import GroupPageMedia, UserMedia, GroupPage, Post, Sources
from db_yqn import models
from settings_yqn import settings

from utils_yqn.avatar import make_avatar, delete_old_avatars
from utils_yqn.email import send_email_about_object, send_email_report
from utils_yqn.image_post import make_image_for_post

# All the non rest API here

class Contact(View):
    """
    Report an object to the admin or Contact an object's email

    contact data:

    modelName str
    objectId str|int
    report bool
    username str
    message.url str
    message.name str (optional)
    message.email str (optional)
    message.body str

    """

    contact_data = None

    def validate_length(self, value, field):
        if len(value) < 1:
            raise ValidationError("Expected value for %s not provided (is it set in your profile?)" % field)

    def post(self,request, *args, **kwargs):

        self.contact_data = json.loads(request.body.decode())

        if self.request.user.is_authenticated:
            self.contact_data['message']['email'] = self.request.user.email
            self.contact_data['message']['name'] = self.request.user.get_full_name()

        # Bot honey
        if self.contact_data['message'].get("url"):
            return HttpResponseBadRequest("Pam")

        # These validation errors get sent back and displayed to the user

        try:
            self.validate_length(self.contact_data['message']['name'], "Name")
            self.validate_length(self.contact_data['message']['email'], "Email")
            self.validate_length(self.contact_data['message']['body'], "Message")
            validators.validate_email(self.contact_data['message']['email'])
        except ValidationError as e:
            return JsonResponse({"error": e.message }, status=500)
        except KeyError as e:
            return JsonResponse({"error": "Please fill in all fields" }, status=500)


        if self.contact_data['report']:
            return self.report()
        else:
            return self.enquiry()

        return HttpResponseBadRequest()

    def report(self):
        send_email_report(self.contact_data['message']['email'],
                          self.contact_data['message']['name'],
                          self.contact_data['message']['body'],
                          self.contact_data['modelName'],
                          self.contact_data['objectId'],
                          "%s %s " % (self.request.META['HTTP_REFERER'],
                                      self.request.META['QUERY_STRING']),
                          )

        return JsonResponse({ "status" : "OK"})

    def enquiry(self):

        # This whitelist needs to be kept tight as getattr will blindly access
        # anything it is asked to on the model module
        whitelist_models_names = ['Event', 'EventsLocation', 'GroupPage']

        if self.contact_data['modelName'] not in whitelist_models_names:
            return HttpResponseBadRequest("Bad model")

        model = getattr(models, self.contact_data['modelName'])
        about_object = model.objects.get(pk=self.contact_data['objectId'])

        send_email_about_object(about_object,
                                self.contact_data['message']['body'],
                                self.contact_data['message']['name'],
                                self.contact_data['message']['email'])

        return JsonResponse({ "status": "OK" })




class Upload(LoginRequiredMixin, View):
    """ API to handle file uploads """

    whitelist_mime_types = ['image/', 'application/pdf', 'application/vnd.ms-excel',
    'application/vnd.oasis.opendocument.spreadsheet', ]

    def post(self, request, *args, **kwargs):

        try:
            file_uploaded = request.FILES['file']
        except KeyError:
            return JsonResponse({"error": "No file supplied" }, status=500)

        content_type_valid = False

        if request.POST.get("avatar"):
            media_obj = self.handle_avatar_file(file_uploaded)
            content_type_valid = self.check_content_type(media_obj, ['image/'])

        elif request.POST.get("group_page"):
            media_obj = self.handle_group_page_file(file_uploaded)
            content_type_valid = self.check_content_type(media_obj)

        elif request.POST.get("post"):
            media_obj, post = self.handle_post_image_file(file_uploaded)
            content_type_valid = self.check_content_type(media_obj, ['image/'])

            if not content_type_valid:
                # Do we need this? The media object being deleted would cascade?
                post.delete()

        else:
            self.handle_other_file(file_uploaded)

        if not content_type_valid:
            return HttpResponseBadRequest("File type not permitted")

        return JsonResponse({ "location": media_obj.file_upload.url })

    def check_content_type(self, media_obj, whitelist_mime_types=whitelist_mime_types):
        uploaded_mime = magic.from_file(media_obj.file_upload.path, mime=True)

        for mime in whitelist_mime_types:
            if mime in uploaded_mime:
                return True

        # Mime type wasn't found: destroy the file and object
        os.remove(media_obj.file_upload.path)
        media_obj.delete()

        return False

    def handle_avatar_file(self, file_uploaded):
        # Note this will delete the current avatar if the file type is wrong
        # Thus resetting back to the default
        delete_old_avatars(self.request.user)

        file_uploaded.name = "%s%s" % (
            settings.AVATAR_PREFIX, file_uploaded.name)

        media_obj = UserMedia.objects.create(
            user=self.request.user,
            file_upload=file_uploaded)

        make_avatar(file_uploaded, media_obj.file_upload.path)

        return media_obj


    def handle_group_page_file(self, file_uploaded):
        group_page = self.request.POST.get("group_page")
        media_obj = GroupPageMedia.objects.create(
            page=GroupPage.objects.get(pk=group_page),
            file_upload=file_uploaded)

        with open(media_obj.file_upload.path, 'wb+') as destination:
            for chunk in file_uploaded.chunks():
                destination.write(chunk)

        return media_obj

    def handle_post_image_file(self, file_uploaded):
        media_obj = UserMedia.objects.create(
            user=self.request.user,
            file_upload=file_uploaded)

        post = Post.objects.create(
            title=self.request.POST.get("title"),
            text=self.request.POST.get("text"),
            source=Sources.LOCAL,
            user=self.request.user,
            media=media_obj,
        )

        make_image_for_post(file_uploaded, media_obj.file_upload.path)

        return media_obj, post

    def handle_other_file(self, file_uploaded):
        media_obj = UserMedia.objects.create(
            user=self.request.user,
            file_upload=file_uploaded)

        with open(media_obj.file_upload.path, 'wb+') as destination:
            for chunk in file_uploaded.chunks():
                destination.write(chunk)