#!/usr/bin/python

# imports
from bs4 import BeautifulSoup
from pushbullet import Pushbullet

import urllib
import cfscrape
import pickle
import re
import os
import configparser

# user provided info
carousellWebsiteLink = "https://carousell.com/search/products/?query="
searchTerms = [] # note: search term should not have spaces, replace with +

# global vars - do not change!
pushbulletAPI = ""
newListings = []

# carousell object
class Carousell(object):
	def __init__(self):
		self.id = 0		# (integer) id for carousell object
		self.title = ""		# (string) title for listing
		self.desc = ""		# (string) description for listing
	def __hash__(self):
		return hash(self.id)
	def __eq__(self, other):
		return (isinstance(other, self.__class__) and getattr(other, 'id') == self.id)
	def addListing(self, listingId, listingTitle, listingDesc):
		self.id = listingId;
		self.title = listingTitle;
		self.desc = listingDesc;	

# process carousell URL
def processURL(link):
	scraper = cfscrape.create_scraper()
	url = scraper.get(carousellWebsiteLink + searchTerm).content
	soup = BeautifulSoup(url, "lxml")

	# print(soup.prettify().encode('utf-8'))
	# for link in soup.find_all('script'):
	# 	print(len(list(link.children)))
	link = soup.find_all('script')
	content = link[1].contents[0]
	#print(content)
	unicodeContent = unicode(content)
	pattern = re.compile("\"id\"\:(\d*)\,\"title\"\:\"(.*?)\"\,\"description\"\:\"(.*?)\"")
	matches = re.findall(pattern, unicodeContent)
	for matchObj in matches:
		listing = Carousell();
		listing.id = int(matchObj[0])
		listing.title = unicode(matchObj[1])
		listing.desc = unicode(matchObj[2])
		newListings.append(listing)


# read config file and load parameters
config = configparser.ConfigParser()
config.read('config.cfg')
pushbulletAPI = config['Pushbullet']['api']

# read search terms from file
try: 
	searchTermsFile = os.getenv("HOME") + "/Scripts/carousell-notifier/searchTerms.txt"
	file = open(searchTermsFile, 'r')
	for line in file:
		searchTerms.append(line)
	file.close()
except IOError:
	print "File not found. Nothing to search for!"

# fetch new listings for each search term
for searchTerm in searchTerms:
	print ("Searching for " + searchTerm.rstrip() + " on carousell website...")
	# clear new fetchings for each search term
	newListings = []

	# fetch listings for search term
	processURL(carousellWebsiteLink + searchTerm)

	# compare new listings with old
	oldListings = []
	pb = Pushbullet(pushbulletAPI)
	oldFileName = "oldListings" + searchTerm.rstrip() + ".pkl"

	try:
		with open(oldFileName, 'rb') as input:
			while True:
				try:
					oldListing = pickle.load(input)
					# print oldListing.title
					oldListings.append(oldListing)
				except (EOFError):
					break
	except IOError:
		print "File not found. Continuing anyways...\n"

	newListingsAdded = list(set(newListings) - set(oldListings))

	'''
	print "New listings in website: "
	for listing in newListings:
		print listing.title
	print " "

	print "Old listings stored internally: "
	for listing in oldListings:
		print listing.title
	print " "
	'''

	#print "New listings to be added to storage: "
	for listing in newListingsAdded: 
		#print listing.title
		 push = pb.push_note("A new listing has been found for " + searchTerm.rstrip(), listing.title + listing.desc)
	#print " "

	print ("There were " + str(len(newListings)) + " listings found on the website with " + str(len(newListingsAdded)) + " listings newly added")
	print " "

	# append new listings to old listings storage
	for listing in newListingsAdded:
		with open(oldFileName, 'ab') as output:
		# 	print ("Adding listings: " + str(listing.id))
			pickle.dump(listing, output, -1)
