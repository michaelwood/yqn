# Copyright: Michael Wood 2019
# Web: http://michaelwood.me.uk
# License: LICENSE.txt

from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from rest_framework.metadata import SimpleMetadata

class SimpleWithFkModelMetadata(SimpleMetadata):
    """ Adds metadata about fields which are forigen keys """

    def get_serializer_info(self, serializer):
        info = super().get_serializer_info(serializer)

        for item in info:
            if info[item]['type'] is "field":
                try:
                    info[item]['api_hint'] = reverse("api:%ss" % item)
                except NoReverseMatch:
                    pass


                if "_" in item:
                    model_name = ""
                    for camel in item.split("_"):
                        model_name += camel.capitalize()
                        info[item]['model_hint'] = "%ss" % model_name
                else:
                    model_name = item
                    info[item]['model_hint'] = "%ss" % item.capitalize()


        return info
