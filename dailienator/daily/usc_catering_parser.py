
import logging

from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)

class RowData(object):
    """A class representing the data for a single row in the target Excel
    sheet. This is empty because it is just data attributes"""
    pass

class Parser():
    building_key = 'Building'
    room_key     = 'Room #'
    floor_key    = 'Floor'
    service_key  = 'Type of Event'
    event_key    = None

    def getShipInfo(self, rowData, rowSoup):
        """
            Retrieve the building, floor, room, sevrice style and event style.
            Return a new copy of the RowData object with this information
            This method will append the following keys to the rowData:
            - building
            - room
            - floor
            - serviceStyle
            - eventStyle
            - specialNotes (dict of key and value)
        """
        # This all just shows up as shipinfolabel
        shipInfo = rowSoup.select(".shipinfolabel")
        shipCount = 0
        rowData.building     = ''
        rowData.room         = ''
        rowData.floor        = ''
        rowData.serviceStyle = ''
        rowData.eventStyle   = ''
        rowData.specialNotes = {}

        for shipCount in range(0, len(shipInfo), 2):
            if self.building_key and shipInfo[shipCount].get_text().strip() == self.building_key + ':' :
                rowData.building = shipInfo[shipCount + 1].get_text().strip()
            elif self.room_key and shipInfo[shipCount].get_text().strip() == self.room_key + ':' :
                rowData.room = shipInfo[shipCount + 1].get_text().strip()
            elif self.floor_key and shipInfo[shipCount].get_text().strip() == self.floor_key + ':' :
                rowData.floor = shipInfo[shipCount + 1].get_text().strip()
            elif self.service_key and shipInfo[shipCount].get_text().strip() == self.service_key + ':' :
                rowData.serviceStyle = shipInfo[shipCount + 1].get_text().strip()
            elif self.event_key and shipInfo[shipCount].get_text().strip() == self.event_key + ':' :
                rowData.eventStyle = shipInfo[shipCount + 1].get_text().strip()
            else :
                # Treat it as a special not. We'll save everything before : as the key
                # and everything after it as the value.
                key = shipInfo[shipCount].get_text().strip()[:-1]
                rowData.specialNotes[key] = shipInfo[shipCount + 1].get_text().strip()

        return rowData

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

    def buildPickUpData(self, allEntries):
        """
            For each row currently in RowData,
            create the corresponding pick up time.
        """
        newList = list()
        for entry in allEntries:
            # Do not build a pick up row if the service style or the event style contains 'All Disposable'
            # Conditions:
            #   service style exists and is all disposable OR event style exists and is all disposable
            #   AND there is a pickUpTime to set as the delivery time
            if (
                (('all disposable' in entry.serviceStyle.lower())
                or ('all disposable' in entry.eventStyle.lower())) == False
                and (entry.endTime or entry.pickUpTime)) :
                pickUpRow = RowData()
                pickUpRow.contactName    = ''
                pickUpRow.contactCompany = ''
                pickUpRow.deliveryTime   = ''
                pickUpRow.startTime      = ''
                pickUpRow.endTime        = ''
                pickUpRow.pickUpTime     = ''
                pickUpRow.guestCount     = ''
                pickUpRow.location       = ''
                pickUpRow.building       = ''
                pickUpRow.room           = ''
                pickUpRow.floor          = ''
                pickUpRow.serviceStyle   = ''
                pickUpRow.eventStyle     = ''
                pickUpRow.specialNotes   = {}

                pickUpRow.guestCount = 'P/U'
                if entry.orderID:
                    pickUpRow.orderID = entry.orderID
                if entry.pickUpTime:
                    pickUpRow.deliveryTime = entry.pickUpTime
                else:
                    pickUpRow.deliveryTime = entry.endTime
                if entry.building:
                    pickUpRow.building = entry.building
                if entry.room:
                    pickUpRow.room = entry.room
                if entry.floor:
                    pickUpRow.floor = entry.floor
                if entry.location:
                    pickUpRow.location = entry.location
                newList.append(pickUpRow)
        allEntries.extend(newList)
        #print 'finished building pick up rows'
        return allEntries

    def buildEntry(self, coverEntry):
        """
            Build a single entry form a cover sheet entry. This method will set the keys
            - contactName
            - contactCompany
            - deliveryTime
            - startTime
            - endTime
            - pickUpTime
            - guestCount
            - location
        """
        rowData = RowData()

        rowData.contactName    = ''
        rowData.contactCompany = ''
        rowData.deliveryTime   = ''
        rowData.startTime      = ''
        rowData.endTime        = ''
        rowData.pickUpTime     = ''
        rowData.guestCount     = ''
        rowData.location       = ''
        # retrieve the Order ID
        rowData.orderID = coverEntry.find('span', 'orderid').get_text().strip()

        # retrive the contact information
        if coverEntry.find('span', 'shipname') is not None:
            rowData.contactName = coverEntry.find('span', 'shipname').get_text().strip()
        if coverEntry.find('span', 'shipcompanyname') is not None:
            rowData.contactCompany = coverEntry.find('span', 'shipcompanyname').get_text().strip()

        # retrieve important times
        if coverEntry.find('span', 'shiptime1') is not None:
            rowData.deliveryTime = coverEntry.find('span', 'shiptime1').get_text().strip()
        if coverEntry.find('span', 'shiptime2') is not None:
            rowData.startTime = coverEntry.find('span', 'shiptime2').get_text().strip()
        if coverEntry.find('span', 'shiptime3') is not None:
            rowData.endTime = coverEntry.find('span', 'shiptime3').get_text().strip()
        if coverEntry.find('span', 'shiptime4') is not None:
            rowData.pickUpTime = coverEntry.find('span', 'shiptime4').get_text().strip()

        # guest count
        logger.debug('Getting guest count')
        rowData.guestCount = coverEntry.find('span', 'guestcount').get_text().strip()

        # Ship information
        logger.debug('Executing method to get ship info')
        rowData = self.getShipInfo(rowData, coverEntry)

        rowData.location = self.buildLocationString(rowData)
        return rowData

    def buildEntries(self, input):
        """
            Build out the data for all rows
            For each basiccoverorw item in the extracted data create a new RowObject
                Place the found information for the basiccoverorw in the RowObject
            Store all of these items in a list of RowObjects
            Return this list
        """
        #print 'Building out row data'
        logger.debug('Building out row data')
        allEntries = list()
        orderCount = 0

        pageSoup = BeautifulSoup(input, "lxml")
        # Gather all of the rows from the input
        coverEntries = pageSoup.select(".basiccoverorw")
        logger.debug('The size of the list is: ' + str(len(coverEntries)))
        # No longer using a secondary BeautifulSoup object for each row
        # as this was causing spinning issues on OpenShift
        for orderCount in range (len(coverEntries)):

            logger.debug('Collecting information for order: ' + str(orderCount))
            entry = self.buildEntry(coverEntries[orderCount])


            # TASK I need to find some way to handle this list properly
            allEntries.append(entry)
            orderCount = orderCount + 1

        #print 'Finished building row data'
        logger.debug('Finished building row data')

        # Now create the pick up entries
        allEntries = self.buildPickUpData(allEntries)
        return allEntries