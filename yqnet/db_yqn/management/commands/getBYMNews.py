# Copyright Michael Wood 2019
# MichaelWood.me.uk
# Licence see LICENCE

from django.core.management.base import BaseCommand

from bs4 import BeautifulSoup

import requests
from datetime import datetime

from django.contrib.auth.models import User
from db_yqn.models import Post, Sources

import logging
import pytz

logger = logging.getLogger("getBYMNews")
logger.setLevel(logging.INFO)


class Command(BaseCommand):
    help = "Fetches news articles from BYM website"

    total_added = 0
    base_url = "https://quaker.org.uk"
    thumb_url = "https://quaker.org.uk/assets/quakers-logo-b2e98470cdb2cc01191f7dc88d5825f557e128bd5490aa7e8ae02f840ccdf45e.svg"
    name = "Britian Yearly Meeting"

    def extract_article(self, article):
        title = article.h3.a.text
        ext_url = "%s%s" % (self.base_url, article.h3.a['href'])
        published = None

        try:
            date_str = article.find(class_="recent-articles__date").text
            published = datetime.strptime(date_str, "%d %B %Y")
            # We don't have an actual time so set it to nowish
            published = published.replace(hour=datetime.now().hour, tzinfo=pytz.UTC)

        except:
            logger.warn("Couldn't work out a date")
            pass

        text = article.find_all("p")[-1:][0].text

        user = User.objects.filter(is_superuser=True).first()

        try:
            try:
                post, created = Post.objects.get_or_create(
                    title=title,
                    text=text,
                    source=Sources.NEWS,
                    user=user,
                    ext_author=self.name,
                    thumbnail=self.thumb_url,
                    ext_url=ext_url)

                if not created:
                    logger.warn("  Skipping %s as we already have it", title)
                else:
                    self.total_added = self.total_added + 1

            except Post.MultipleObjectsReturned:
                logger.warn("  Database has already got duplicates. Doing nothing for %s", title)

        except Exception as e:
            logger.warn("Error saving rss as a post %s", e)


    def load_from_web(self):
        url = "%s/news-and-events/news" % self.base_url

        news_page = requests.get(url)

        soup = BeautifulSoup(news_page.text, 'html.parser')

        articles = soup.find_all("li", class_="recent-articles__item")
        logger.info("Found %d articles", len(articles))

        for article in articles:
            self.extract_article(article)


    def handle(self, *args, **options):

        self.load_from_web()

        print("Added %d articles" % self.total_added)
