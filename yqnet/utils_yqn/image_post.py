# Copyright: Michael Wood 2019
# Web: http://michaelwood.me.uk
# License: LICENSE.txt

from PIL import Image, ImageOps

from db_yqn.models import UserMedia
from settings_yqn import settings

import os

def make_image_for_post(filep, path):
    """ Overwrites the given file with a smaller version of the file for a post"""

    image = Image.open(filep)

    image.thumbnail((600,600), Image.ANTIALIAS)
    image.save(path)