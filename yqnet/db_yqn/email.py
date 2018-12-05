# Copyright: Michael Wood 2019
# Web: http://michaelwood.me.uk
# License: LICENSE.txt

from django.core.mail import EmailMessage
from settings_yqn import settings


def send_email_about_object(about_object, message, sender_name, sender_email):

    subject = "New enquiry about %s (via Quakr)" % about_object.title

    body_info = {
        "obj_title": about_object.title,
        "sender_name": sender_name,
        "sender_address": sender_email,
        "message": message,
        "contact_us": settings.DEFAULT_FROM_EMAIL,
    }

    body = (
        "Hello, \n\n"
        "Please see enquiry details below from %(sender_name)s <%(sender_address)s> regarding %(obj_title)s: \n"
        "~ Message ~\n\n"
        "%(message)s \n\n"
        "~ End Message ~\n"
        "\n"
        "If you have received this message in error please contact us at %(contact_us)s\n"
        "Thanks!\n\n"
        "---\n"
        "Quakr"
        ) % body_info


    message = EmailMessage(
        to = (about_object.email,),
        subject = subject,
        body = body,
        from_email = settings.DEFAULT_FROM_EMAIL, # This is the default anyway but here to be explicit
        reply_to = (sender_email,)
    )

    print(body)
    print(message)

    message.send()


def send_email_report(reportee_email, reportee_name, message, model_name, object_id, request_metadata):

    body = (
        "Hello, \n\n"
        "Some content has been reported by %(reportee_name)s <%(reportee_email)s>\n"
        "Object: %(model_name)s-%(object_id)s \n"
        "Via: %(request_metadata)s \n"
        "Message: \n\n"
        "%(message)s \n\n"
        "End Message\n"
        "\n"
        "Please investigate. Thanks!\n\n"
        "---\n"
        "Quakr"
        ) % locals()


    message = EmailMessage(
        to = (settings.DEFAULT_FROM_EMAIL,),
        subject = "Some content has been reported",
        body = body,
        from_email = settings.DEFAULT_FROM_EMAIL, # This is the default anyway but here to be explicit
    )

    print(body)
    print(message)

    message.send()


    