
import logging

from bs4 import BeautifulSoup
from basic_parser import BasicParser


logger = logging.getLogger(__name__)

class RowData(object):
    """A class representing the data for a single row in the target Excel
    sheet. This is empty because it is just data attributes"""
    pass

class Parser(BasicParser):
    building_key = 'Building'
    room_key     = 'Room #'
    floor_key    = 'Floor'
    service_key  = 'Type of Event'
    event_key    = None

    def buildLocationString(self, row):
        """
            Utility method to build the hyphen delimited location string.
        """
        locationString = ""
        if hasattr(row, 'building'):
                locationString = row.building + " - "
        else:
            locationString = "-"
        if hasattr(row, 'floor'):
            locationString = locationString + row.floor + " - "
        else:
            locationString = locationString + " - "
        if hasattr(row, 'room'):
            locationString = locationString + row.room
        else:
            locationString = locationString
        return locationString