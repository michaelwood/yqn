# Copyright: Michael Wood 2019
# Web: http://michaelwood.me.uk
# License: LICENSE.txt

from django.core.exceptions import ValidationError
from django.test import TestCase
from db_yqn.models import validate_no_slug_clash


class TestSlugClashValidator(TestCase):
    """Tests to make sure we can't break the url structure with an invalid slug """

    def test_slug_clash(self):
        caught_it = False

        try:
            validate_no_slug_clash("posts")
        except ValidationError:
            caught_it = True

        self.assertTrue(caught_it, "Didn't catch that we're adding a slug that conflicts")