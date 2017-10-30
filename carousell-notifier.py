#!/usr/bin/python

# imports
from bs4 import BeautifulSoup
from pushbullet import Pushbullet, InvalidKeyError, PushbulletError
import urllib
import cfscrape
import cPickle as pickle
import sys
import re
import os
import configparser

# user provided info
carousellWebsiteLink = "https://carousell.com/search/products/?query="
carousellBaseLink = "https://carousell.com"
searchTerms = [] # note: search term should not have spaces, replace with +

# global vars - do not change!
pushbulletAPI = ""
newListings = []
newListingsDictList = []

# carousell object
class Carousell(object):
	def __init__(self):
		self.id = ""		# (integer) id for carousell object
		self.title = ""		# (string) title for listing
		self.link = ""
		self.price = ""
	def __hash__(self):
		return hash(self.id)
	def __eq__(self, other):
		return (isinstance(other, self.__class__) and getattr(other, 'id') == self.id)
	def addListing(self, listingId, listingTitle, listingLink, listingPrice):
		self.id = listingId;
		self.title = listingTitle;
		self.desc = listingDesc;	
		self.link = listingLink
		self.price = listingPrice

# get product ID from href
def getProductId(href):
	# href looks something like this:
	# /p/a-little-life-by-hanya-yanagihara-91606615/?ref=search&amp;ref_query=overcoming%20gravity&amp;ref_referrer=%2Fsearch%2Fproducts%2F%3Fquery%3Dovercoming%2Bgravity&amp;ref_reqId=NQAu0aCv9lO1soG0gpxzWtjk1kgVYUx3
	pattern = re.compile("^\/p\/.*?-(\d+)\/")
	matches = re.findall(pattern, href)
	if len(matches) > 0:
		return matches[0]
	else:
		print "unable to read id from href: " + href
		return "-1"

# process carousell URL
def processURL(link):
	scraper = cfscrape.create_scraper()
	url = scraper.get(carousellWebsiteLink + searchTerm).content
	soup = BeautifulSoup(url, "lxml")

	#print(soup.prettify().encode('utf-8'))
	#for link in soup.find_all('script'):
		#print(link.contents)
        cards = soup.find_all("div", "row card-row")[0].contents[0].contents
	for card in cards:
		link =  card.find_all("a", id="productCardThumbnail")[0]['href']
		title = card.find_all("h4", id="productCardTitle")[0].string
		price = card.find_all("span", id="productCardPrice")[0]['title']
		listing = Carousell();
		listing.id = getProductId(link)
		listing.title = title
		listing.link = carousellBaseLink + link
		listing.price = price
		newListings.append(listing)

# set working directory to current path
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# read config file and load parameters
config = configparser.ConfigParser()
config.read('config.cfg')
pushbulletAPI = config['Pushbullet']['api']

try: 
	pb = Pushbullet(pushbulletAPI)
except InvalidKeyError:
	print "Pushbullet API key was invalid! No notification will be sent. Quitting program"
	sys.exit()

# read search terms from file
try: 
	file = open('searchTerms.txt', 'r')
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
	oldListingsJSON = []
	oldFileExists = True

	oldFileName = "oldListings" + searchTerm.rstrip() + ".pkl"

	try:
		with open(oldFileName, 'rb') as input:
			while True:
				try:
					oldListings = pickle.load(input)
				except (EOFError):
					break
	except IOError:
		print "File not found. Continuing anyways...\n"
		oldFileExists = False

	newListingsAdded = list(set(newListings) - set(oldListings))

	print "New listings in website: "
	for listing in newListings:
		print str(listing.id) + ": " + listing.title
	print " "

	print "Old listings stored internally: "
	for listing in oldListings:
		print str(listing.id) + ": " + listing.title
	print " "

	if oldFileExists:
		for listing in newListingsAdded: 
			try:
				push = pb.push_note("A new listing has been found for " + searchTerm.rstrip(), listing.title + "\n" + listing.price + "\n" + listing.link)
			except PushbulletError:
				print "Pushbullet push error for " + listing.title
	else:
		print "Since old file does not exist, not spamming pushbullet with multiple listings. New listings will be pushed to your device!"

	print ("There were " + str(len(newListings)) + " listings found on the website with " + str(len(newListingsAdded)) + " listings newly added")
	print " "

	# append new listings to old listings storage
	with open(oldFileName, 'ab') as output:
		pickle.dump(newListingsAdded, output, protocol=-1)
