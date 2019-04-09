# Copyright: Michael Wood 2019
# Web: http://michaelwood.me.uk
# License: LICENSE.txt

"""
Test all the functionality of the Events page
"""

from django.contrib.auth.models import User

from django.urls import reverse
from django.test import override_settings
from tests.browser.selenium_helpers import SeleniumTestCase
from selenium.webdriver.common.keys import Keys

from tests.browser.yqn_browser_test import YqnBrowserTest

from db_yqn.models import Event, EventsLocation

import time
import os


class TestPosts(YqnBrowserTest):
    """ Test landing page shows the Toaster brand """


    @YqnBrowserTest.login
    def test_single_event(self):
        """ Makes an event then deletes it """

        event_title = "Best event"
        event_text = "Hello world event"

        self.get(reverse("events"))

        time.sleep(0.5)

        self.click_test_id("add-event-btn")

        self.enter_text("#title", event_title)

        # Post text is a TinyMCE  editor
        self.enter_text_tinymce(event_text)

        date_pickers = self.find_all_test_id("date-picker")

        # start date
        date_pickers[0].click()
        time.sleep(0.5)

        days = date_pickers[0].find_elements_by_css_selector(".cell.day")
        days[3].click()

        self.select_option_by_index("[data-test-id='date_time_start-hour-select']", 3)
        self.select_option_by_index("[data-test-id='date_time_start-hour-select']", 4)
        # end date

        date_pickers[1].click()
        days = date_pickers[1].find_elements_by_css_selector(".cell.day")
        days[4].click()

        self.select_option_by_index("[data-test-id='date_time_end-hour-select']", 5)
        self.select_option_by_index("[data-test-id='date_time_end-minute-select']", 6)


        self.enter_text("#email", "email@example.com")
        # This will produce no results in the autocomplete
        self.enter_text("#venue", "test")
        time.sleep(4)

        # Now we enter the "Add new.." for a Venue
        self.find("[data-test-id='venue-autocomplete'] a").click()

        self.enter_text("#title", "Best venue")
        self.enter_text_tinymce("123 House Road")

        self.enter_text("#postcode", "WC2N 4EA")
        # This requires an external api call
        self.click("#postcode-lookup-btn")

        time.sleep(2)

        # Make the new venue
        self.click_test_id("add-object-modal-addnext")

        time.sleep(1)

        # Make the event
        self.click_test_id("add-object-modal-addnext")

        time.sleep(1)

        event_added_headings = self.find_all("#events-widget .list-item h3")

        # First heading is the date
        self.assertTrue("3" in event_added_headings[0].text, "The right event date hasn't appeared on the page")

        # Second heading is the title
        self.assertTrue(event_title in event_added_headings[1].text, "The event title hasn't appeared on the page")