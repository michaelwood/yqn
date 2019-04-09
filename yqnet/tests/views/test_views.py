# Copyright: Michael Wood 2019
# Web: http://michaelwood.me.uk
# License: LICENSE.txt

from django.test import TestCase, override_settings
from django.urls import reverse_lazy, URLPattern
from django.contrib.auth.models import User

from db_yqn.models import GroupPage
from ui_yqn.urls import urlpatterns

class UIViewsTests(TestCase):
    """Basic tests to verify all UI urls respond """

    def setUp(self):
        user = User.objects.create_user(username="test", password="test")

        gp = GroupPage.objects.create(title="test",
                                 slug="test")
        gp.users.add(user)


    def test_view_is_ok(self):
        """Basic test to make sure views return 200 status"""
        for path in urlpatterns:
            if type(path) is not URLPattern or path.name is None:
                continue

            if "slug" in path.pattern.describe() and "int" in path.pattern.describe():
                url = reverse_lazy(path.name, args=("test", 1))
            elif "int" in path.pattern.describe():
                url = reverse_lazy(path.name, args=(1,))
            elif "slug" in path.pattern.describe():
                url = reverse_lazy(path.name, args=("test",))
            else:
                url = reverse_lazy(path.name)

            if "accounts" in url:
                self.client.login(username="test", password="test")

            print("Testing %s" % url)

            response = self.client.get(url, HTTP_HOST="localhost", follow=True)

            self.assertEqual(response.status_code, 200, "%s failed %s" % (url, response.reason_phrase))
            self.assertTrue(response['Content-Type'].startswith('text/html'))
