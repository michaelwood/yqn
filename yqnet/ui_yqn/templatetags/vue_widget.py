# Copyright Michael Wood 2019
# MichaelWood.me.uk
# Licence see LICENCE

from django import template
from settings_yqn import settings

from django.utils.safestring import mark_safe

import os

register = template.Library()

# Errors fromr tags will be raised as Template Errors

@register.simple_tag
def vue_widget(widget_name):
    widget_path = os.path.join(settings.VUE_WIDGETS_PATH, widget_name)
    with open(widget_path, "r") as widget_f:
        widget_content = widget_f.read()
        return mark_safe(widget_content)