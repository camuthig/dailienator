# dailienator.py
# Chris Muthig

import mechanize
from mechanize import ControlNotFoundError
import cookielib
import lxml
import xlsxwriter
import time
from bs4 import BeautifulSoup
import os
from django.conf import settings
from django.core.mail import *
import logging
import traceback
import base64
from time import strftime

from importlib import import_module

from dailienator.sodexoaccounts.models import AccountUser, Account, AccountStaticDailyEntry

# global variables
# Column numbers

columns = {
    'guest_count_col'          : 0,
    'set_time_col'             : 1,
    'contract_number_col'      : 2,
    'location_col'             : 3,
    'service_style_col'        : 4,
    'event_style_col'          : 5,
    'pick_up_time_col'         : 6,
    'assigned_caterer_col'     : 7,
    'special_instructions_col' : 8,
    'lead_on_event_col'        : 9,
    'vehicle_col'              : 10
}

logger = logging.getLogger(__name__)

class DailyGenerator():
    def validateDate(self, date):
        try:
            time.strptime(date, '%m/%d/%Y')
        except ValueError:
            raise ValueError("Invalid date")

    def isLoggedIn(self, data):
        """
            Verify that the user has successfully logged into the CaterTrax system.
        """
        loggedIn = "true"
        pageSoup = BeautifulSoup(data, "lxml")
        pageTitle = pageSoup.title.string
        if pageTitle == "Emory Catering - Administrative Login":
            for div in pageSoup.find_all('div'):
                if div.get_text().strip() == "Your userid/password cannot be located":
                    raise Exception("Your Catertrax userid/password cannot be located")
                    break
            #The user is not logged in, but it was not due to the username/password
            #Log this as an unknown issue.
            if loggedIn == "true":
                raise Exception("Unkown error occurred logging into Catertrax")
                loggedIn = "unknown_error"
        return loggedIn

    def retrieveSheetData(self, username, password, date, site):
        """
            This function will retrieve the data from the catertrax site.
            Input data will be the credentials to access the site, and the
            date for which to pull the data.
        """
        # Browser
        br = mechanize.Browser()

        # Cookie Jar
        cj = cookielib.LWPCookieJar()
        br.set_cookiejar(cj)

        # Browser options
        br.set_handle_equiv(True)
        br.set_handle_gzip(True)
        br.set_handle_redirect(True)
        br.set_handle_referer(True)
        br.set_handle_robots(False)

        # Follows refresh 0 but not hangs on refresh > 0
        br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

        # Open the login menu site
        #print ("Connecting to " + site + "shopcatertrax.asp")
        try:
            r = br.open(site + "shopcatertrax.asp")
        except Exception, e:
            br.close()
            raise Exception(str(e) + " occurred accessing " + site + "shopcatertrax.asp")
        # Select the first (and only form) to login with
        br.select_form(nr=0)
        # User credentials
        try:
            br.form['UserName'] = username
            br.form['Password'] = password
        except ControlNotFoundError:
            br.close()
            raise ControlNotFoundError("Connection error occurred creating Daily.")

        # Login
        br.submit()
        # If the browser is still on the login page, something went wrong.
        # The scenario will be analyzed in the isLoggedIn method later.
        if "Administrative Login" in br.title():
            data = br.response().read()
            br.close()
            return data

        # Move to the coversheet page for specified date.
        dailyDate = site + "coversheet.asp?startdate=" + date + "&enddate=" + date
        br.open(dailyDate)
        data = br.response().read()
        br.close()
        return data

    def addKitchenSheetInfo(self,username,password,site,orders,):
        """
        This function will access CaterTrax once using the already checked
        credentials. To be safe, the isLoggedIn method will still need to be
        used. After the user is logged in, we will access the kitchen sheet
        for each individual order and update the Row object with any additional
        information.
        """

        orderCount = 0
        total = 0

        # Browser

        br = mechanize.Browser()

        # Cookie Jar

        cj = cookielib.LWPCookieJar()
        br.set_cookiejar(cj)

        # Browser options

        br.set_handle_equiv(True)
        br.set_handle_gzip(True)
        br.set_handle_redirect(True)
        br.set_handle_referer(True)
        br.set_handle_robots(False)

        # Follows refresh 0 but not hangs on refresh > 0

        br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(),max_time=1)

        # Open the login menu site

        #print 'Connecting to ' + site + 'shopcatertrax.asp'
        r = br.open(site + 'shopcatertrax.asp')

        # Select the first (and only form) to login with

        br.select_form(nr=0)

        # User credentials

        try:
            br.form['UserName'] = username
            br.form['Password'] = password
        except ControlNotFoundError:
            br.close()
            raise ControlNotFoundError('Connection error preparing kitchen information.')

        # Login

        br.submit()

        # If the browser is still on the login page, something went wrong.
        # The scenario will be analyzed in the isLoggedIn method.
        data = br.response().read()
        try:
            self.isLoggedIn(data)
        except Exception, e:
            br.close()
            raise Exception(str(e))

        for order in orders:

            # Move to the coversheet page for specified date.

            if hasattr(order, 'orderID'):
                orderId = order.orderID
                kitchenSheet = site + 'shopa_formatprint.asp?orderid=' \
                    + orderId + '&idfield=orderid'
                br.open(kitchenSheet)
                data = br.response().read()

                pageSoup = BeautifulSoup(data, 'lxml')

                # Grab the divs in the file.
                # The first one will be the "DIV" from the kitchen sheet.
                # This will always contain whether or not the event is waited.

                body = pageSoup.find_all('div')

                if 'SERVICE STAFF' in str(body[0]):
                    order.specialInstructions = 'ATTEND'
        br.close()
        return orders

    def sortRowList(self, rowList):
        """Change the AM/PM time for simplified comparison."""
        for item in rowList:
            try:
                newTime = time.strptime(item.deliveryTime, '%I:%M %p')
                item.militaryTime = time.strftime('%H:%M', newTime)
            except Exception, e:
                try:
                    newTime = time.strptime(item.deliveryTime, '%I:%M:%S %p')
                    item.militaryTime = time.strftime('%H:%M', newTime)
                except Exception, ie:
                    raise Exception('Error sorting orders' + str(ie))

        sortedList = sorted(rowList, key=lambda x: x.militaryTime)
        #print 'Finished sorting rows'
        return sortedList

    def buildExcelSheet(self, input, date, account):
        """
            Build out the excel sheet
            Iterate through the list of RowObjects, writing information in
            proper format
            This method expects each element of input to  have the following keys.
            The values of the keys may be either empty strings or empty dicts
            - building
            - room
            - floor
            - location
            - serviceStyle
            - eventStyle
            - guestCount
            - orderID
            - pickUpTime
            - deliveryTime
            - startTime
            - endTime
            - contactName
            - contactCompany
            - specialNotes
        """
        #print 'Starting to build the excel file'
        headers = ['Guest Count', 'Set Time', 'Contract #', 'Location',
                'Service Type', 'Pick Up Time', 'Assigned Caterer',
                'Special Instructions', 'Lead on Event', 'Vehicle']
        columnCounter = 0

        # Build the basic workbook
        inputDate = time.strptime(date, '%m/%d/%Y')
        yearFolder = time.strftime('%Y', inputDate)
        fileDate = time.strftime('%m.%d.%y', inputDate)
        # Set the file name
        fileName = 'Master_Daily-' + fileDate + '.xlsx'
        if settings.DEBUG is True:
            path = os.path.join(settings.BASE_DIR, '..', 'tests', fileName)
        else:
            path = os.environ['OPENSHIFT_DATA_DIR'] + fileName
        file = open(path, 'w')
        file.close()
        os.chmod(path, 0777)
        workbook = xlsxwriter.Workbook(path)
        worksheet = workbook.add_worksheet('Master Daily Scheduling Sheet')
        worksheet.set_landscape()
        worksheet.set_zoom(75)
        #worksheet.fit_to_pages(1, 0)


        # header Style
        coverFormat = workbook.add_format({
        'bold':     True,
        'border':   1,
        'align':    'center',
        'valign':   'vcenter',
        'font_name': 'Arial',
        'font_size': 14,
        })
        coverSayingFormat = workbook.add_format({
        'bold':     True,
        'border':   1,
        'align':    'center',
        'valign':   'vcenter',
        'fg_color': '#92D050',
        'font_name': 'Arial',
        'font_size': 16,
        'text_wrap': True
        })
        headerFormat = workbook.add_format({
        'top': 1,
        'left': 1,
        'right': 1,
        'bottom':   5,
        'align':    'center',
        'valign':   'vcenter',
        'text_wrap': True,
        'font_name': 'Arial',
        'font_size': 10,
        })
        startFormat = workbook.add_format({
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'text_wrap': True,
        'font_name': 'Arial',
        'bold': True,
        'font_size': 10,
        'fg_color': '#92D050',
        })
        eventFormat = workbook.add_format({
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'text_wrap': True,
        'font_name': 'Arial',
        'font_size': 10,
        })
        attendFormat = workbook.add_format({
        'bold': True,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'text_wrap': True,
        'font_name': 'Arial',
        'font_size': 10,
        'font_color': '#FF0000',
        })
        pickUpFormat = workbook.add_format({
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'text_wrap': True,
        'font_name': 'Arial',
        'font_size': 10,
        'fg_color': '#FF00FF',
        })
        endFormat = workbook.add_format({
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'text_wrap': True,
        'font_name': 'Arial',
        'font_size': 10,
        'font_color': '#0000FF',
        'bold': True,
        'fg_color': '#FFFF00',
        })

        # Column widths
        worksheet.set_column(columns['guest_count_col'], columns['guest_count_col'], 6)
        worksheet.set_column(columns['set_time_col'], columns['set_time_col'], 10)
        worksheet.set_column(columns['contract_number_col'], columns['contract_number_col'], 11)
        worksheet.set_column(columns['location_col'], columns['location_col'], 19)
        worksheet.set_column(columns['service_style_col'], columns['service_style_col'], 13)
        worksheet.set_column(columns['event_style_col'], columns['event_style_col'], 13)
        worksheet.set_column(columns['pick_up_time_col'], columns['pick_up_time_col'], 20)
        worksheet.set_column(columns['assigned_caterer_col'], columns['assigned_caterer_col'], 22)
        worksheet.set_column(columns['special_instructions_col'], columns['special_instructions_col'], 20)
        worksheet.set_column(columns['lead_on_event_col'], columns['lead_on_event_col'], 19)
        worksheet.set_column(columns['vehicle_col'], columns['vehicle_col'], 9)

        # build cover row
        worksheet.set_row(0, 75)
        worksheet.merge_range(0, columns['guest_count_col'], 0, columns['contract_number_col'], account.name, coverFormat)
        # worksheet.insert_image(0, columns['set_time_col'], 'images\emory_catering.jpeg', {'x_offset': -30, 'y_offset': 10})
        # TODO Get images working again - will need to upload them

        if account.header_slogan:
          worksheet.merge_range(0, columns['location_col'], 0, columns['pick_up_time_col'], account.header_slogan, coverSayingFormat)
        else :
            worksheet.merge_range(0, columns['location_col'], 0, columns['pick_up_time_col'], "Visit the Account Page to Set a Slogan", coverSayingFormat)
        # Build out the date
        writeDate = time.strftime('%A , %B %d, %Y', inputDate)
        worksheet.merge_range(0, columns['assigned_caterer_col'], 0, columns['vehicle_col'], writeDate, coverFormat)
        # build header rows
        columnCounter = 0
        rowCounter = 1
        for header in headers:
            if header == 'Service Type':
                worksheet.merge_range(rowCounter, columnCounter, rowCounter, columnCounter + 1, header, headerFormat)
                columnCounter += 2
            else:
                worksheet.write(rowCounter, columnCounter, header, headerFormat)
                columnCounter += 1


        columnCounter = 0
        start_entries = AccountStaticDailyEntry.objects.filter(account=account, position='start')
        if start_entries:
            # Put a blank entry for each column
            # Then add in the start format columns
            for columnCounter in range(len(columns)):
                worksheet.write(rowCounter, columnCounter, "", eventFormat)
            columnCounter = 0
            for entry in start_entries:
                if entry.column == 'service_style':
                    worksheet.merge_range(
                        rowCounter,
                        columns.get('service_style_col'),
                        rowCounter,
                        columns.get('event_style_col'),
                        entry.value,
                        startFormat)
                else:
                    worksheet.write(rowCounter, columns.get(entry.column + '_col'), entry.value, startFormat)
            rowCounter += 1

        # Iterate through the input row data, adding the information as needed
        for row in input:
            worksheet.set_row(rowCounter, 42)
            if row.deliveryTime:
                worksheet.write(rowCounter, columns['set_time_col'], row.deliveryTime, eventFormat)
            if row.guestCount and row.guestCount == "P/U":
                worksheet.write(rowCounter, columns['guest_count_col'], row.guestCount, pickUpFormat)
                worksheet.write(rowCounter, columns['contract_number_col'], "", eventFormat)
                worksheet.write(rowCounter, columns['location_col'], row.location, eventFormat)
            elif row.guestCount:
                worksheet.write(rowCounter, columns['guest_count_col'], row.guestCount, eventFormat)
                worksheet.write(rowCounter, columns['contract_number_col'], row.orderID, eventFormat)
                worksheet.write(rowCounter, columns['location_col'], row.location, eventFormat)

            # Write the service style column
            if row.serviceStyle:
                # If this is a All Disposable event, write service style as "All Disposable"
                if ((row.serviceStyle != '' and 'all disposable' in row.serviceStyle.lower())
                    or (row.eventStyle != '' and 'all disposable' in row.eventStyle.lower())):
                    worksheet.write(rowCounter, columns['service_style_col'], "All Disposable", eventFormat)
                else:
                    worksheet.write(rowCounter, columns['service_style_col'], row.serviceStyle, eventFormat)
            else:
                worksheet.write(rowCounter, columns['service_style_col'], "", eventFormat)
            # Only write to event column in special circumstances PHASE 2
            worksheet.write(rowCounter, columns['event_style_col'], "", eventFormat)
            if row.pickUpTime:
                worksheet.write(rowCounter, columns['pick_up_time_col'], row.pickUpTime, eventFormat)
            elif row.endTime:
                worksheet.write(rowCounter, columns['pick_up_time_col'], row.endTime, eventFormat)
            else:
                worksheet.write(rowCounter, columns['pick_up_time_col'], "", eventFormat)
            worksheet.write(rowCounter, columns['assigned_caterer_col'], "", eventFormat)
            if row.specialNotes:
                # TODO Add logic to iterate over the special notes here
                worksheet.write(rowCounter, columns['special_instructions_col'], "", attendFormat)
            else:
                worksheet.write(rowCounter, columns['special_instructions_col'], "", eventFormat)
            worksheet.write(rowCounter, columns['lead_on_event_col'], "", eventFormat)
            worksheet.write(rowCounter, columns['vehicle_col'], "", eventFormat)
            #print 'Finished a row'
            rowCounter += 1

        # insert the end day row
        end_entries = AccountStaticDailyEntry.objects.filter(account=account, position='end')
        if end_entries:
            # Put a blank entry for each column
            # Then add in the start format columns
            for columnCounter in range(len(columns)):
                worksheet.write(rowCounter, columnCounter, "", eventFormat)
            columnCounter = 0
            for entry in end_entries:
                if entry.column == 'service_style':
                    worksheet.merge_range(
                        rowCounter,
                        columns.get('service_style_col'),
                        rowCounter,
                        columns.get('event_style_col'),
                        entry.value,
                        endFormat)
                else:
                    worksheet.write(rowCounter, columns.get(entry.column + '_col'), entry.value, endFormat)

        workbook.close()
        return path

    def emailFile(self, user, path, date):
        logger.debug('Emailing the file');
        try:
            email_add = user.email
            subject = ('Daily ' + date)
            email = EmailMessage(subject, 'Automated Daily file attached.', 'dailienator.py@gmail.com', [email_add])
            email.attach_file(path)
            email.send()
        except:
            raise Exception("Error emailing Daily.")
        finally:
                os.remove(path)
        return "done"

    def generateDaily(self, user, date):
        '''
            Generate the Daily file using the AccountUser information
            as well as the date.
        '''
        try:
            parsedDate = date
            user_account = user.account
            parser = import_module('dailienator.daily.' + user_account.slug + '_parser')
            parser = getattr(parser, 'Parser')
            my_parser = parser()

            logger.info('Generating daily for account ' + user_account.name +
                        ' and date ' + parsedDate);
            startNormal = time.time()
            logger.debug('The password for catertrax is: ' + user.catertrax_password)
            data = self.retrieveSheetData(user.catertrax_username,
                                user.catertrax_password,
                                parsedDate, user_account.catertrax_url)


            #The input data is the raw information received from Catertrax
            #We can use this to determine if the user is logged in or not.
            self.isLoggedIn(data)

            # Start parsing of data
            rowList = my_parser.buildEntries(data)

            finishNormal = time.time()
            totalNormal = (finishNormal - startNormal)

            #startKitchen = time.time()
            #rowList = self.addKitchenSheetInfo(user.catertrax_user,
            #                    base64.decodestring(user.catertrax_password),
            #                    user_account.catertrax_url, rowList)
            #finishKitchen = time.time()
            #totalKitchen = (finishKitchen - startKitchen)


            startNormal1 = time.time()

            # Start of Generic
            rowList = self.sortRowList(rowList)
            daily = self.buildExcelSheet(rowList, parsedDate, user_account)
            self.emailFile(user, daily, parsedDate)
            finishNormal1 = time.time()

            logger.info('Finished generating daily for account '
                        + user_account.name + ' and date ' + parsedDate);

            totalNormal1 = (finishNormal1 - startNormal1)
            sumNormal = totalNormal + totalNormal1
            logger.debug('Time for normal functions = ' + str(sumNormal))
            #logger.debug('Time for kitchen retrieval = ' + str(totalKitchen))

        except Exception as e:
            logger.error(traceback.format_exc())
            raise Exception(str(e))

        logger.debug('Completing the dailienator process')
        return "done"
