# Copyright Michael Wood 2019
# MichaelWood.me.uk
# Licence see LICENCE

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.db import OperationalError

from bs4 import BeautifulSoup
from bs4.element import Tag

import requests
import time

from django.contrib.auth.models import User
from db_yqn.models import Venue, EventsLocation

import logging
import json


logger = logging.getLogger("getMeetings")
logger.setLevel(logging.INFO)


class Command(BaseCommand):
    help = "Sync the Quaker meetings list"
    meetings = []

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            action='store_true',
            dest='file',
            help='Load from meetings json file',
        )

    def extract_meeting_info(self, meeting_page_url):

        meeting_page_dom = requests.get(meeting_page_url)
        meeting = {}
        logger.info("Getting %s" % meeting_page_url)

        soup = BeautifulSoup(meeting_page_dom.text, 'html.parser')

        meeting['url'] = meeting_page_url
        meeting['name'] = soup.find("h1", class_="meeting__name").string

        if not meeting['name']:
            raise Exception("Fail - can't even get name")
        
        try:

            para = soup.find("div", class_="col-sm-5").find_all("p")[0]

            addr_lines = para.find_all(string=True)
            # ['Friends Meeting House', '98 Crown Street', 'Aberdeen', 'AB11 6HJ']

            addr = ", ".join(addr_lines[:-1])

            meeting['address'] = addr

            meeting['postcode'] = addr_lines[-1:][0]

            map_tag = soup.find("div", class_="meeting__map")

            meeting['lat'] = map_tag['data-lat']
            meeting['lng'] = map_tag['data-lng']

        except Exception:
            meeting['address'] = 'Unknown'
            meeting['lat'] = "-1" 
            meeting['lng'] = "-1"
            meeting['postcode'] = "Unknown"

        time.sleep(1) # Be kind to the server

        return meeting

    def load_from_web(self):
        base_url = "http://quaker.org.uk/"

        meetings_list = requests.get(base_url + "/meetings/all")
               
        soup = BeautifulSoup(meetings_list.text, 'html.parser')

        meeting_links = soup.find_all("a", class_="meeting-summary__link")
        logger.info("Found %d meetings", len(meeting_links))
        
        for meeting_link in meeting_links:
            logger.info("Looking up %s" % meeting_link)
            print(meeting_link['href'])
            self.meetings.append(self.extract_meeting_info(base_url + meeting_link['href']))
            print(self.meetings)

        with open("meetings.json", 'w+') as f:
            f.write(json.dumps(self.meetings))


    def handle(self, *args, **options):

        if options['file']:
            fp = open("meetings.json")
            self.meetings = json.loads(fp.read())
        else:
            self.load_from_web()


        # Now update the objects in our db
        
        user = User.objects.filter(is_superuser=True).first()

        for meeting in self.meetings:
            print("Updating %s" % meeting['name'])

            try:
                venue = Venue.objects.get(title=meeting['name'])

                venue.address=meeting['address']
                venue.lat_lng = "%s,%s" % (meeting['lat'], meeting['lng'])
                venue.postcode = meeting['postcode']

                venue.save()

            except Venue.DoesNotExist:
                venue, created = Venue.objects.update_or_create(
                    title = meeting['name'],
                    address = meeting['address'],
                    lat = meeting['lat'],
                    lng = meeting['lng'],
                    postcode = meeting['postcode'],
                )


            EventsLocation.objects.update_or_create(
                title=meeting['name'],
                url=meeting['url'],
                user=user,
                venue=venue)

