#!/usr/bin/python

# imports
from bs4 import BeautifulSoup
from pushbullet import Pushbullet

import urllib
import cfscrape

# user provided info
pushbulletAPI = "o.AHKh671q9bc91LVmvRx4olNE7eV3LIgF"
carousellWebsiteLink = "https://carousell.com/search/products/?query="
searchTerm = "overcoming+gravity" # note: search term should not have spaces, replace with +

# process carousell URL
def processURL(link):
	scraper = cfscrape.create_scraper()
	url = scraper.get(carousellWebsiteLink + searchTerm).content
	soup = BeautifulSoup(url, "lxml")

	# print(soup.prettify().encode('utf-8'))
	# for link in soup.find_all('script'):
	# 	print(len(list(link.children)))
	link = soup.find_all('script')
	children = link[1].children
	print(list(children)[0])

processURL(carousellWebsiteLink)
