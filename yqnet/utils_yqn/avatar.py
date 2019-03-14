# Copyright: Michael Wood 2019
# Web: http://michaelwood.me.uk
# License: LICENSE.txt

from PIL import Image, ImageOps

from db_yqn.models import UserMedia
from settings_yqn import settings

import os

def make_avatar(filep, path):
    """ Overwrites the given file with a smaller version of the file for an avatar"""

    image = Image.open(filep)

    size = 200,200

    image = ImageOps.fit(image, size, Image.ANTIALIAS)
    image.save(path)

def delete_old_avatars(user):
    """ Delete any old avatars from given user """

    try:
        for avatar in UserMedia.objects.filter(user=user, file_upload__contains=settings.AVATAR_PREFIX):
            os.remove(avatar.file_upload.path)
            avatar.delete()
    except UserMedia.DoesNotExist:
        pass

