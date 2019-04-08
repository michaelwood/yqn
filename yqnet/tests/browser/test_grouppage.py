# Copyright: Michael Wood 2019
# Web: http://michaelwood.me.uk
# License: LICENSE.txt

"""
Test all the functionality of the Posts page
"""

from django.contrib.auth.models import User
from django.urls import reverse
from django.test import override_settings
from django.core import mail

from tests.browser.selenium_helpers import SeleniumTestCase
from selenium.webdriver.common.alert import Alert

from tests.browser.yqn_browser_test import YqnBrowserTest
from db_yqn.models import GroupPage, GroupPageMedia

import time
import os


class TestGroupPage(YqnBrowserTest):
    """ Test Group page functions """

    @YqnBrowserTest.login
    def test_group_page_new(self):
        """ Makes a group page """
        page_title = "Hello world"
        page_email = "email@example.com"
        element_text = "olleh"
        page_body = "<p>page body</p>"

        self.get(reverse('pages'))

        self.click('button[data-target="#add-object-modal-GroupPages"]')

        self.enter_text("#title", page_title)
        self.enter_text("#email", page_email)

        self.click("#add-object-modal-GroupPages .btn-primary")

        # Wait for the redirect to the new page
        time.sleep(2)

        self.enter_text_tinymce(page_body)

        self.click("#save-page")

        time.sleep(1)

        # This is the slug we are expecting to have been created for us based on the title
        self.get(reverse("user-pages", args=("hello-world",)))

        self.assertTrue(page_title in self.find("h3").text, "Expected title was not on page")

        # Check that the page rendered the body as html
        self.assertTrue("page body" in self.find_all(".container p")[0].text, "Expected body was not on page")

        page = GroupPage.objects.get(title=page_title)

        self.assertTrue(page_title in page.title)
        self.assertTrue(page_email in page.email)
        self.assertTrue(page_body in page.body)


    @YqnBrowserTest.login
    def test_image_post(self):
        """ Edit a page then deleted it """

        slug = "start-slug"

        new_title = "new-title"
        new_slug = "new-page"
        new_email = "new@example.com"

        page = GroupPage.objects.create(
            title="Start title",
            slug=slug,
            body="<p>Hi</p>",
            email="test@example.com")

        page.save()

        page.users.add(User.objects.first())

        time.sleep(2)

        self.get(reverse("user-pages", args=(slug,)))

        self.click('a[data-test-id="page-edit-btn"]')

        self.replace_text("#title-input", new_title)
        self.replace_text("#slug-input", new_slug)
        self.replace_text("#email-input", new_email)

        self.click("#save-page")

        time.sleep(2)


        self.get(reverse("user-pages", args=(new_slug,)))

        time.sleep(2)

        self.assertTrue(new_title in self.find("h3").text, "Expected title was not on page")

    @YqnBrowserTest.login
    def test_email_contact_on_page(self):
        """ Test the contact us form on the group page """
        page_owner = User.objects.create_user(username="dooo", password="deee", first_name="Doo")

        slug = "cool-group"
        message = "Hi I have some questions"

        page = GroupPage.objects.create(
            title="Start title",
            slug=slug,
            body="<p>Hi</p>",
            email="test@example.com")

        page.save()

        page.users.add(page_owner)

        time.sleep(2)

        self.get(reverse("user-pages", args=(slug,)))

        self.click("#contact-btn")

        # We we're not logged in we need to provide these details
        if not self.logged_in_user:
            self.enter_text("#name", "wibble")
            self.enter_text("#email", "email@example.com")

        self.enter_text("#body", message)

        self.click('button[data-test-id="contact-send-btn"]')

        time.sleep(3)

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct.
        self.assertTrue(message in mail.outbox[0].body, "Our message wasn't in the email body")

        time.sleep(2)

        ## TODO DJANGO Mail tools check outbox

    def test_anon_email_contact_on_page(self):
        """ Test non logged in contact us on page """
        self.test_email_contact_on_page()



    @YqnBrowserTest.login
    def test_delete_group_page(self):
        slug = "test"
        page = GroupPage.objects.create(
            title="Start title",
            slug=slug,
            body="<p>Hi</p>",
            email="test@example.com")

        page.save()

        page.users.add(self.logged_in_user)

        self.get(reverse("user-page-edit", args=(slug,)))

        time.sleep(2)

        self.click("#delete-page")

        time.sleep(2)

        Alert(self.driver).accept()

        time.sleep(1)

        self.assertTrue(GroupPage.objects.count() is 0, "Page still exists after delete")



