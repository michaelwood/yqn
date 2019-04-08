# Copyright: Michael Wood 2019
# Web: http://michaelwood.me.uk
# License: LICENSE.txt

from django.test import TestCase, override_settings

from settings_yqn import settings

new_framework_settings = settings.REST_FRAMEWORK
# We want all the REST_FRAMEWORK settings apart from the throttling
del new_framework_settings['DEFAULT_THROTTLE_CLASSES']
del new_framework_settings['DEFAULT_THROTTLE_RATES']


@override_settings(REST_FRAMEWORK=new_framework_settings)
class ListApiTests(TestCase):
    """Tests to verify API end points respond """

    urls = [
        '/Posts',
        '/XMLFeeds',
        '/Twitters',
        '/Instagrams',
        '/GroupPages',
        '/GroupRedirectPages',
        '/EventsLocations/?search=a',
        '/Venues/?search=a',
        '/Regions',
        '/EventsAtVenue/?id=0',
        '/EventsAtRegion/?id=0',
    ]


    def test_endpoint_is_ok(self):
        """Basic test to make sure list API end points return 200 status"""
        for url in self.urls:
            response = self.client.get("/api%s" % url, follow=True)

            self.assertEqual(response.status_code, 200, "%s failed %s" % (url, response.reason_phrase))
            self.assertTrue(response['Content-Type'].startswith('application/json'))