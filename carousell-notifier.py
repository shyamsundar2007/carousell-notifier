#!/usr/bin/python

# imports
from bs4 import BeautifulSoup
from pushbullet import Pushbullet

import urllib

# user provided info
pushbulletAPI = "o.AHKh671q9bc91LVmvRx4olNE7eV3LIgF"
carousellWebsiteLink = "https://carousell.com/"

# process carousell URL
def processURL(link):
	url = urllib.urlopen(link).read()
	soup = BeautifulSoup(url, "lxml")

	print(soup.prettify())

processURL(carousellWebsiteLink)
