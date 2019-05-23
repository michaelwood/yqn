# Copyright Michael Wood 2019
# MichaelWood.me.uk
# Licence see LICENCE
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.db import OperationalError


from db_yqn.models import Sources, Post, XMLFeed

from datetime import datetime
from time import mktime

import pytz
import feedparser
import logging


logger = logging.getLogger("getRSS")

class Command(BaseCommand):
    help = "Fetches RSS feeds"

    total_added = 0

    def extract_posts(self, entry, feed_title, xml_feed):
        try:

            # Create a datetime object from the parsed timestamp

            published = datetime.fromtimestamp(
                mktime(entry.published_parsed),
                tz=pytz.UTC
            )

            # There can be multiple authors on one site
            try:
                if entry.author is not feed_title:
                    name = "%s | %s" % (entry.author_detail.name, feed_title)
                else:
                    name = entry.author_detail.name
            except:
                name = feed_title

            try:
                thumbnail = entry.media_content[0]['url']
            except AttributeError:
                thumbnail = None

            post, created = Post.objects.get_or_create(
                title=entry.title,
                text=entry.summary,
                publish_date=published,
                source=xml_feed.source,
                user=xml_feed.user,
                ext_author=name,
                thumbnail=thumbnail,
                ext_url=entry.link,
                xml_feed=xml_feed)

            if created:
                self.total_added = self.total_added + 1
            else:
                logger.warn("  Skipping %s as we already have it", entry.title)

        except Exception as e:
            # Move on
            logger.warn("Not saving rss entry as a post %s", e)


    def handle(self, *args, **options):

       xml_feeds = XMLFeed.objects.exclude(enabled=False)

       if not xml_feeds:
           logger.warn("No feeds defined")

       for xml_feed in xml_feeds:
           print("Fetching.. %s %s" % (xml_feed.name, xml_feed.url))
           feed = feedparser.parse(xml_feed.url)

           for entry in feed.entries:
               print(" - Extracting %s" % entry.title)
               self.extract_posts(entry, feed.feed.title, xml_feed)

       print("\nTotal posts added %d" % self.total_added)



