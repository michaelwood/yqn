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
from selenium.webdriver.common.keys import Keys

from tests.browser.yqn_browser_test import YqnBrowserTest

from db_yqn.models import UserMedia, XMLFeed

import time
import os


class TestPosts(YqnBrowserTest):
    """ Test landing page shows the Toaster brand """


    @YqnBrowserTest.login
    def test_post_text(self):
        """ Makes a Text Post then deletes it """
        post_text = "Hello world"
        post_title = "Hello"

        url = reverse('posts')
        self.get(url)

        self.click("#add-posts-btn-group-drop")
        self.click('a[data-target="#add-object-modal-Posts"]')

        self.enter_text("#title", post_title)

        # Post text is a TinyMCE  editor
        self.enter_text_tinymce(post_text)

        self.click("#add-object-modal-Posts .btn-primary")

        # Wait for the Vue widget to render the new post
        time.sleep(2)

        new_post = self.find_all(".list-item")[0]

        result_text = new_post.find_element_by_class_name("post-text").text
        result_title = new_post.find_element_by_tag_name("h3").text

        self.assertTrue(post_text in result_text)
        self.assertTrue(post_title in result_title)

        new_post.find_element_by_css_selector("a.action-menu-yqn").click()
        new_post.find_element_by_css_selector('a[data-test-id="post-delete-btn"]').click()

        time.sleep(2)

        # We've deleted all the items so we should now have 0
        self.assertTrue(len(self.find_all(".list-item")) != 0, "Multiple post found so it was not deleted?")


    @YqnBrowserTest.login
    def test_image_post(self):
        """ Makes an Image Post then deleted it """

        post_title = "Images hello"
        post_text = "Here is a lovely picture"
        image_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "testupload.jpg")

        url = reverse('posts')
        self.get(url)

        self.click("#add-posts-btn-group-drop")
        self.click('a[data-target="#add-picture-post-modal"]')

        self.enter_text("#pp-title", post_title)
        self.find("#pp-file").send_keys(image_file)

        self.enter_text_tinymce(post_text)

        self.click("#add-picture-post-modal .btn-primary")

        # Wait for the Vue widget to render the new post
        time.sleep(2)

        new_post = self.find_all(".list-item")[0]

        result_text = new_post.find_element_by_class_name("post-text").text
        result_title = new_post.find_element_by_tag_name("h3").text

        self.assertTrue(post_text in result_text)
        self.assertTrue(post_title in result_title)

        new_post.find_element_by_css_selector("a.action-menu-yqn").click()
        new_post.find_element_by_css_selector('a[data-test-id="post-delete-btn"]').click()

        time.sleep(2)

        # We've deleted all the items so we should now have 0
        self.assertTrue(len(self.find_all(".list-item")) != 0, "Multiple post found so it was not deleted?")

        # Check to see if the file uploaded was written
        media = UserMedia.objects.first()
        self.assertTrue(os.path.exists(media.file_upload.path), "File failed to upload %s" % media.file_upload.path)

    @YqnBrowserTest.login
    def test_add_feed(self):
        feed_url = "http://wwww.example.com"

        url = reverse('posts')
        self.get(url)

        self.click('button[data-target="#add-object-modal-XMLFeeds"]')

        #fill in the form
        self.enter_text("#add-object-modal-XMLFeeds #url", feed_url)
        self.enter_text("#add-object-modal-XMLFeeds #name", "Best Blog")
        self.select_option_by_index("#add-object-modal-XMLFeeds #source", 0)

        # And submit it
        self.click("#add-object-modal-XMLFeeds .btn-primary")

        time.sleep(2)

        self.assertTrue(XMLFeed.objects.count() > 0, "Xml Feed wasn't added to DB")