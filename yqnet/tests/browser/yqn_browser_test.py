# Copyright: Michael Wood 2019
# Web: http://michaelwood.me.uk
# License: LICENSE.txt

"""
Test all the functionality of the Posts page
"""

from django.contrib.auth.models import User

from django.urls import reverse
from django.test import override_settings
from tests.browser.selenium_helpers import SeleniumTestCase
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import WebDriverException

from ui_yqn.urls import urlpatterns
from settings_yqn import settings

import time

class bcolors:
    #https://stackoverflow.com/a/287944
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

class YqnBrowserTest(SeleniumTestCase):
    """ A base class that does some of the common things of yqn for us """

    logged_in_user = None


    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        try:
            new_framework_settings = settings.REST_FRAMEWORK
            # We want all the REST_FRAMEWORK settings apart from the throttling
            del new_framework_settings['DEFAULT_THROTTLE_CLASSES']
            del new_framework_settings['DEFAULT_THROTTLE_RATES']

            override_settings(REST_FRAMEWORK=new_framework_settings)
            override_settings(IN_TEST=True)
        except Exception as e:
            # It is not required that these settings are present or as a prerequiste
            # for running the tests so just note instead
            print("Note - not overriding settings %s" % e)
            pass


    @staticmethod
    def login(test_func):
        """ Decorator to login on before running a test function on an YqnBrowserTest instance """

        def login_before_test(self, *args):

            username = "test"
            password = "test"

            self.logged_in_user = User.objects.create_user(
                username=username,
                password=password,
                first_name="Test face",
                email="example@example.com")

            self.get(reverse("login"))
            self.enter_text("#id_username", username)
            self.enter_text("#id_password", password)
            self.click("input[type=submit]")

            # Wait for the redirect and load after login
            time.sleep(1)

            return test_func(self, *args)

        return login_before_test


    def tearDown(self):

        # https://github.com/SeleniumHQ/selenium/wiki/Logging
        try:
            print("--- Browser Log ---")

            for log in self.driver.get_log("browser"):
                print("[%s%s%s] - %s" % (bcolors.BOLD, log['level'], bcolors.RESET, log['message']))
                # It would be nice if we could just assert here but this is only in tearDown
                if "SEVERE" in log['level']:
                    raise Exception("JS Exception: %s" % log['message'])

            print("--- / Browser Log ---")

        except WebDriverException as e:
            # Not all drivers are made equal.. some don't have this log some do
            print(e)

        super().tearDown()


    def enter_text_tinymce(self, value):
        """ Enter the text into the current active tinyMCE editor """
        self.driver.execute_script("tinyMCE.activeEditor.setContent(\"%s\");" % value)

    def replace_text(self, selector, value):
        """ Replace text in element matching selector """
        self.find(selector).clear()

        return self.enter_text(selector, value)

    def select_option_by_index(self, selector, index):
        select = Select(self.find(selector))
        select.select_by_index(index)
        # N.b. assumes jquery available (which it is)
        self.driver.execute_script("$(\"%s\").trigger('change');" % selector)

    def click_test_id(self, test_id):
        """ Finds the [data-test-id=test_id] element and clicks it """
        return self.click("[data-test-id='%s']" % test_id)



