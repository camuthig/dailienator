
import logging

from bs4 import BeautifulSoup
from basic_parser import BasicParser


logger = logging.getLogger(__name__)

class Parser(BasicParser):
    building_key = 'Building'
    room_key     = 'Room #'
    floor_key    = 'Floor'
    service_key  = 'Type of Event'
    event_key    = None

    def buildLocationString(self, row):
        """
            USC doesn't include a floor in their description of
            the location
        """
        locationString = ""
        if hasattr(row, 'building'):
                locationString = row.building + " - "
        else:
            locationString = "-"
        if hasattr(row, 'room'):
            locationString = locationString + row.room
        else:
            locationString = locationString
        return locationString