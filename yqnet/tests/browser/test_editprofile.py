# Copyright: Michael Wood 2019
# Web: http://michaelwood.me.uk
# License: LICENSE.txt

"""
A small example test demonstrating the basics of writing a test with
SeleniumTestCase; this just fetches the home page
and checks the brand navigation exist
"""

from django.urls import reverse
from tests.browser.yqn_browser_test import YqnBrowserTest

import time
import os

class TestSample(YqnBrowserTest):
    """ Test updating profile """

    @YqnBrowserTest.login
    def test_change_avatar(self):
        self.get(reverse('edit-profile'))
        filename = "testupload.jpg"

        image_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

        self.find("#file-upload").send_keys(image_file)

        time.sleep(3)

        avatar = self.find("#avatar")

        # Note we only use filename without the extension because the live test server
        # Does funny things to upload paths and names
        self.assertTrue(filename[:3] in avatar.get_attribute("src"), "The new avatar wasn't present on the page")

