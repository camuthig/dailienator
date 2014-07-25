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
import base64
from time import strftime

from dailienator.sodexoaccounts.models import AccountUser, Account

# global variables
# Column numbers
guestColNum = 0
setTimeColNum = 1
contractNumColNum = 2
locationColNum = 3
serviceColNum = 4
eventColNum = 5
pickUpColNum = 6
assignedCatererColNum = 7
specialColNum = 8
leadColNum = 9
vehicleColNum = 10

logger = logging.getLogger('django.request')
	
class RowData(object):
	"""A class representing the data for a single row in the target Excel 
	sheet. This is empty because it is just data attributes"""
	pass

class DailyGenerator():
	def validateDate(self, date):
		try:
			time.strptime(date, '%m/%d/%Y')
		except ValueError:
			raise ValueError("Invalid date")

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
			elif shipInfo[shipCount].get_text().strip() == 'Room #/Room Name:' :
				rowData.room = shipInfo[shipCount + 1].get_text().strip()	
			elif shipInfo[shipCount].get_text().strip() == 'Floor:' :
				rowData.floor = shipInfo[shipCount + 1].get_text().strip()
			elif shipInfo[shipCount].get_text().strip() == 'Service Style:' :
				rowData.serviceStyle = shipInfo[shipCount + 1].get_text().strip()
			elif shipInfo[shipCount].get_text().strip() == 'Event Style:' :
				rowData.eventStyle = shipInfo[shipCount + 1].get_text().strip()
			
			shipCount = shipCount + 2
		return rowData

	def testDef(self):
		f = open('/var/lib/openshift/524f394ee0b8cd488d000029/app-root/repo/wsgi/openshift/long_day.html', 'r')
		data = f.read()
		print 'Got the sheet data from test file'
		return data
		
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
			# TASK I need to find some way to handle this list properly
			allRows.append(rowData)
			orderCount = orderCount + 1
			
		#print 'Finished building row data'
		logger.debug('Finished building row data')
		return allRows

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
		

	def buildPickUpData(self, rowList):
		"""
		    For each row currently in RowData, 
		    create the corresponding pick up time.
		"""
		newList = list()
		for rowData in rowList:
			# Do not build a pick up row if the service style or the event style contains 'All Disposable'
			# Conditions:
			# 	service style exists and is all disposable OR event style exists and is all disposable
			# 	AND there is a pickUpTime to set as the delivery time
			if (((hasattr(rowData, 'serviceStyle') and'all disposable' in rowData.serviceStyle.lower()) 
			or (hasattr(rowData, 'eventStyle') and 'all disposable' in rowData.eventStyle.lower()))
			== False) and hasattr(rowData, 'pickUpTime') == True:
				newRow = RowData()
				newRow.guestCount = 'P/U'
				if hasattr(rowData, 'orderID'):
					newRow.orderID = rowData.orderID
				if hasattr(rowData, 'pickUpTime'):
					newRow.deliveryTime = rowData.pickUpTime
				if hasattr(rowData, 'building'):
					newRow.building = rowData.building
				if hasattr(rowData, 'room'):
					newRow.room = rowData.room
				if hasattr(rowData, 'floor'):
					newRow.floor = rowData.floor
				newList.append(newRow)
		rowList.extend(newList)
		#print 'finished building pick up rows'
		return rowList		

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

	def buildExcelSheet(self, input, date, account):
		""" 
			Build out the excel sheet 
			Iterate through the list of RowObjects, writing information in 
			proper format
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
			path = os.path.join(os.getcwd(),'..', '..', '..', '..', 'tests', fileName) 
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
		'font_size': 20,
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
		endDayLocationFormat = workbook.add_format({
		'border': 1,
		'bold': True,
		'font_color': '#0000FF',
		'align': 'center',
		'valign': 'vjustify',
		'text_wrap': True,
		'font_name': 'Arial',
		'font_size': 10,
		'fg_color': '#FFFF00',
		})
		endDayTimeCatererFormat = workbook.add_format({
		'border': 1,
		'align': 'center',
		'valign': 'vcenter',
		'text_wrap': True,
		'font_name': 'Arial',
		'font_size': 10,
		'fg_color': '#3366FF',
		})
		endDayInstructionsFormat = workbook.add_format({
		'border': 1,
		'align': 'center',
		'valign': 'vcenter',
		'text_wrap': True,
		'font_name': 'Arial',
		'font_size': 10,
		'font_color': '#FF0000',
		'bold': True,
		})
	
		# Column widths
		worksheet.set_column(guestColNum, guestColNum, 6)
		worksheet.set_column(setTimeColNum, setTimeColNum, 10)
		worksheet.set_column(contractNumColNum, contractNumColNum, 11)
		worksheet.set_column(locationColNum, locationColNum, 19)
		worksheet.set_column(serviceColNum, serviceColNum, 13)
		worksheet.set_column(eventColNum, eventColNum, 13)
		worksheet.set_column(pickUpColNum, pickUpColNum, 20)
		worksheet.set_column(assignedCatererColNum, assignedCatererColNum, 22)
		worksheet.set_column(specialColNum, specialColNum, 20)
		worksheet.set_column(leadColNum, leadColNum, 19)
		worksheet.set_column(vehicleColNum, vehicleColNum, 9)
	
		# build cover row
		worksheet.set_row(0, 75)
		worksheet.merge_range(0, guestColNum, 0, contractNumColNum, "", coverFormat)
		# worksheet.insert_image(0, setTimeColNum, 'images\emory_catering.jpeg', {'x_offset': -30, 'y_offset': 10})
		worksheet.merge_range(0, locationColNum, 0, pickUpColNum, "inspirational saying", coverSayingFormat)
		# Build out the date
		writeDate = time.strftime('%A , %B %d, %Y', inputDate)
		worksheet.merge_range(0, assignedCatererColNum, 0, vehicleColNum, writeDate, coverFormat)
		# build header rows
		columnCounter = 0
		for header in headers:
			if header == 'Service Type':
				worksheet.merge_range(1, columnCounter, 1, columnCounter + 1, header, headerFormat)
				columnCounter += 2
			else:
				worksheet.write(1, columnCounter, header, headerFormat)
				columnCounter += 1
	
		
		columnCounter = 0
		if account.site == 'https://emory.catertrax.com/':
			# insert the start day row
			for columnCounter in range (len(headers) + 1):
				if columnCounter == locationColNum:
					worksheet.write(2, locationColNum, "Thermometer/ Sanitizer/Temp Log", startFormat)
				elif columnCounter == setTimeColNum:
					worksheet.write(2, columnCounter, "", startFormat)
				elif columnCounter == specialColNum:
					worksheet.write(2, specialColNum, "UNLOCK SOUTH ELEVATOR & HALLWAY DOOR", startFormat)
				else:
					worksheet.write(2, columnCounter, "", eventFormat)	
				columnCounter += 1
			rowCounter = 3
		else:
			#Only Emory has a start row setup  for now
			rowCounter = 2
		# Iterate through the input row data, adding the information as needed
		
		for row in input:
			worksheet.set_row(rowCounter, 42)
			if hasattr(row, 'deliveryTime'):
				worksheet.write(rowCounter, setTimeColNum, row.deliveryTime, eventFormat)
			if hasattr(row, 'guestCount') and row.guestCount == "P/U":
				worksheet.write(rowCounter, guestColNum, row.guestCount, pickUpFormat)
				worksheet.write(rowCounter, contractNumColNum, "", eventFormat)
			elif hasattr(row, 'guestCount'):
				worksheet.write(rowCounter, guestColNum, row.guestCount, eventFormat)
				worksheet.write(rowCounter, contractNumColNum, row.orderID, eventFormat)
			# Build location string
			locationString = self.buildLocationString(row)
			worksheet.write(rowCounter, locationColNum, locationString, eventFormat)
			# Write the service style column
			if hasattr(row, 'serviceStyle'):
				# If this is a All Disposable event, write service style as "All Disposable"
				if ((hasattr(row, 'serviceStyle') and'all disposable' in row.serviceStyle.lower()) 
				or (hasattr(row, 'eventStyle') and 'all disposable' in row.eventStyle.lower())):
					worksheet.write(rowCounter, serviceColNum, "All Disposable", eventFormat)
				else:
					worksheet.write(rowCounter, serviceColNum, row.serviceStyle, eventFormat)
			else:
				worksheet.write(rowCounter, serviceColNum, "", eventFormat)
			# Only write to event column in special circumstances PHASE 2
			worksheet.write(rowCounter, eventColNum, "", eventFormat)
			if hasattr(row, 'pickUpTime'):
				worksheet.write(rowCounter, pickUpColNum, row.pickUpTime, eventFormat)
			else:
				worksheet.write(rowCounter, pickUpColNum, "", eventFormat)
			worksheet.write(rowCounter, assignedCatererColNum, "", eventFormat)
			if hasattr(row, 'specialInstructions'):
				worksheet.write(rowCounter, specialColNum, row.specialInstructions, attendFormat)
			else:
				worksheet.write(rowCounter, specialColNum, "", eventFormat)
			worksheet.write(rowCounter, leadColNum, "", eventFormat)
			worksheet.write(rowCounter, vehicleColNum, "", eventFormat)
			#print 'Finished a row'
			rowCounter += 1
	
		# insert the end day row
		if account.site == 'https://emory.catertrax.com/':
			#Only Emory has a setup for the end of day row so far
			columnCounter = 0
			for columnCounter in range (len(headers) + 1):
				worksheet.set_row(rowCounter, 42)
				if columnCounter == locationColNum:
					worksheet.write(rowCounter, columnCounter, 
									"COX HALL & PANTRY LOCK UP", 
									endDayLocationFormat)
				elif columnCounter == specialColNum:
					worksheet.merge_range(rowCounter, columnCounter, 
											rowCounter, columnCounter + 1, 
											"Be Sure To Sweep & Mop Elevators "
											"- ONLY LOCK SOUTH ELEVATORS", 
											endDayInstructionsFormat)
					columnCounter += 1
				elif columnCounter == leadColNum:
					# do nothing
					pass
				elif columnCounter == setTimeColNum:
					worksheet.write(rowCounter, setTimeColNum, "", 
									endDayTimeCatererFormat)
				elif columnCounter == assignedCatererColNum:
					worksheet.write(rowCounter, assignedCatererColNum, "", 
									endDayTimeCatererFormat)
				else:
					worksheet.write(rowCounter, columnCounter, "", eventFormat)
				columnCounter += 1
	
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

	def executeDailyCreation(self, username, password, date):
		"""
			Function used for manually testing the daily generation without having an
			AccountUser object.
		"""
		print 'start'
		logger.debug('Starting the dailienator process')
		# data = self.testDef()
		logger.debug('Retrieving data')
		data = self.retrieveSheetData(username, password, date)
		logger.debug('Verifying we are logged in')
		loggedIn = self.isLoggedIn(data)
		if loggedIn == "connection_error":
			return "error"
		# Check that the username was correct
		if loggedIn == "false":
			return "error"
		# Check for any unknown errors logging in
		elif loggedIn == "unknown_error":
			return "error"
		logger.debug('Building row data')
		rowList = self.buildRowData(data)
		if rowList == "error":
			return "error"
		logger.debug('Building pick up data')
		rowList = self.buildPickUpData(rowList)
		logger.debug('Sorting row data')
		rowList = self.sortRowList(rowList)
		logger.debug('Building the excel sheet')
		daily = self.buildExcelSheet(rowList, date)
		#self.emailFile(daily, date)
		logger.debug('Completing the dailienator process')
		return "done"
	
	def generateDaily(self, user, date):
		'''
			Generate the Daily file using the AccountUser information
			as well as the date. 
		'''
		try:
			parsedDate = date.strftime('%m/%d/%Y')
			user_account = user.account
			
			logger.info('Generating daily for account ' + user_account.name + 
						' and date ' + parsedDate);
			startNormal = time.time()
			data = self.retrieveSheetData(user.catertrax_user, 
								base64.decodestring(user.catertrax_password), 
								parsedDate, user_account.site)
			
			
			#The input data is the raw information received from Catertrax
			#We can use this to determine if the user is logged in or not.
			self.isLoggedIn(data)
			rowList = self.buildRowData(data)
			
			finishNormal = time.time()
			totalNormal = (finishNormal - startNormal)
			
			#startKitchen = time.time()
			#rowList = self.addKitchenSheetInfo(user.catertrax_user, 
            #                    base64.decodestring(user.catertrax_password), 
            #                    user_account.site, rowList)
			#finishKitchen = time.time()
			#totalKitchen = (finishKitchen - startKitchen)
			
			
			startNormal1 = time.time()
			rowList = self.buildPickUpData(rowList)
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
			logger.error(str(e))
			raise Exception(str(e))
		
		logger.debug('Completing the dailienator process')
		return "done"