
import logging

from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)

class RowData(object):
    """A class representing the data for a single row in the target Excel
    sheet. This is empty because it is just data attributes"""
    pass

class Parser():

    def getShipInfo(self, rowData, rowSoup):
        """Retrieve the building, floor, room, sevrice style and event style.
        Return a new copy of the RowData object with this information"""
        # This all just shows up as shipinfolabel
        shipInfo = rowSoup.select(".shipinfolabel")
        shipCount = 0
        # retrieve Ship Info

        for shipCount in range(len(shipInfo)):
            if shipInfo[shipCount].get_text().strip() == 'Building:' :
                rowData.building = shipInfo[shipCount + 1].get_text().strip()
            elif shipInfo[shipCount].get_text().strip() == 'Room #:' :
                rowData.room = shipInfo[shipCount + 1].get_text().strip()
            elif shipInfo[shipCount].get_text().strip() == 'Floor:' :
                rowData.floor = shipInfo[shipCount + 1].get_text().strip()

            # TASK Only the serviceStyle is actually put in the excel
            elif shipInfo[shipCount].get_text().strip() == 'Type of Event:' :
                rowData.serviceStyle = shipInfo[shipCount + 1].get_text().strip()
            elif shipInfo[shipCount].get_text().strip() == 'Type of Event:' :
                rowData.eventStyle = shipInfo[shipCount + 1].get_text().strip()

            shipCount = shipCount + 2
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

    def buildPickUpData(self, rowList):
        """
            For each row currently in RowData,
            create the corresponding pick up time.
        """
        newList = list()
        for rowData in rowList:
            # Do not build a pick up row if the service style or the event style contains 'All Disposable'
            # Conditions:
            #   service style exists and is all disposable OR event style exists and is all disposable
            #   AND there is a pickUpTime to set as the delivery time
            if (((hasattr(rowData, 'serviceStyle') and'all disposable' in rowData.serviceStyle.lower())
            or (hasattr(rowData, 'eventStyle') and 'all disposable' in rowData.eventStyle.lower()))
            == False) and hasattr(rowData, 'endTime') == True:
                newRow = RowData()
                newRow.guestCount = 'P/U'
                if hasattr(rowData, 'orderID'):
                    newRow.orderID = rowData.orderID
                if hasattr(rowData, 'endTime'):
                    newRow.deliveryTime = rowData.endTime
                if hasattr(rowData, 'building'):
                    newRow.building = rowData.building
                if hasattr(rowData, 'room'):
                    newRow.room = rowData.room
                if hasattr(rowData, 'floor'):
                    newRow.floor = rowData.floor
                if hasattr(rowData, 'location'):
                    newRow.location = rowData.location
                newList.append(newRow)
        rowList.extend(newList)
        #print 'finished building pick up rows'
        return rowList

    def buildRowData(self, input):
        """
            Build out the data for all rows
            For each basiccoverorw item in the extracted data create a new RowObject
                Place the found information for the basiccoverorw in the RowObject
            Store all of these items in a list of RowObjects
            Return this list
        """
        #print 'Building out row data'
        logger.debug('Building out row data')
        allRows = list()
        orderCount = 0
        # populate with an empty RowData object for each available row.

        pageSoup = BeautifulSoup(input, "lxml")
        # Gather all of the rows from the input
        coverRows = pageSoup.select(".basiccoverorw")
        logger.debug('The size of the list is: ' + str(len(coverRows)))
        # No longer using a secondary BeautifulSoup object for each row
        # as this was causing spinning issues on OpenShift
        for orderCount in range (len(coverRows)):
            logger.debug('Collecting information for order: ' + str(orderCount))
            rowData = RowData()
            # retrieve the Order ID
            rowData.orderID = coverRows[orderCount].find('span', 'orderid').get_text().strip()

            # retrive the contact information
            if(coverRows[orderCount].find('span', 'shipname') is None) == False:
                rowData.contactName = coverRows[orderCount].find('span', 'shipname').get_text().strip()
            if(coverRows[orderCount].find('span', 'shipcompanyname') is None) == False:
                rowData.contactCompany = coverRows[orderCount].find('span', 'shipcompanyname').get_text().strip()

            # retrieve important times
            if(coverRows[orderCount].find('span', 'shiptime1') is None) == False:
                rowData.deliveryTime = coverRows[orderCount].find('span', 'shiptime1').get_text().strip()
            if(coverRows[orderCount].find('span', 'shiptime2') is None) == False:
                rowData.startTime = coverRows[orderCount].find('span', 'shiptime2').get_text().strip()
            if(coverRows[orderCount].find('span', 'shiptime3') is None) == False:
                rowData.endTime = coverRows[orderCount].find('span', 'shiptime3').get_text().strip()
            if(coverRows[orderCount].find('span', 'shiptime4') is None) == False:
                rowData.pickUpTime = coverRows[orderCount].find('span', 'shiptime4').get_text().strip()

            # guest count
            logger.debug('Getting guest count')
            rowData.guestCount = coverRows[orderCount].find('span', 'guestcount').get_text().strip()

            # Ship information
            logger.debug('Executing method to get ship info')
            rowData = self.getShipInfo(rowData, coverRows[orderCount])

            rowData.location = self.buildLocationString(rowData)

            # TASK I need to find some way to handle this list properly
            allRows.append(rowData)
            orderCount = orderCount + 1

        #print 'Finished building row data'
        logger.debug('Finished building row data')

        # Now create the pick up entries
        allRows = self.buildPickUpData(allRows)
        return allRows