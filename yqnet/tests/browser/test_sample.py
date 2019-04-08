# Copyright: Michael Wood 2019
# Web: http://michaelwood.me.uk
# License: LICENSE.txt

"""
A small example test demonstrating the basics of writing a test with
SeleniumTestCase; this just fetches the home page
and checks the brand navigation exist
"""

from django.urls import reverse
from tests.browser.selenium_helpers import SeleniumTestCase

class TestSample(SeleniumTestCase):
    """ Test landing page shows the Toaster brand """

    def test_landing_page_has_brand(self):
        url = reverse('index')
        self.get(url)
        brand_link = self.find("a.navbar-brand")
        self.assertTrue(brand_link is not None)
