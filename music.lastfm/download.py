#!/usr/bin/env python
"""
Downloads all your track history from last.fm and exports it into
a sqlite3 database file.
"""
USER = "rami95"
FILE = "%s.lastfm.sqlite.db" % USER
APIK = "b8258575158335e66482df0777e5b331"

import os
import sqlite3
import urllib
import xml.etree.ElementTree

if os.path.exists(FILE):
	conn = sqlite3.connect(FILE)
	c = conn.cursor()
	c.execute('SELECT MAX(timestamp) FROM tracks')
	last = c.fetchone()[0]
	if last is None:
		last = 0
else:
	conn = sqlite3.connect(FILE)
	c = conn.cursor()
	c.execute('''CREATE TABLE tracks (artist text, name text, album text, timestamp real)''')
	last = 0

# Check number of Pages
f = urllib.urlopen("http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=%s&api_key=%s&limit=200&page=0&from=%d" % (USER, APIK, last))
tree = xml.etree.ElementTree.fromstring(f.read())
rt = tree.find("recenttracks")
total = int(rt.attrib['total'])
totalPages = int(rt.attrib['totalPages'])

if total > 0:
	for page in range(1,totalPages+1):
		f = urllib.urlopen("http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=%s&api_key=%s&limit=200&page=%d&from=%d" % (USER, APIK, page, last))
		tree = xml.etree.ElementTree.fromstring(f.read())
		rt = tree.find("recenttracks")
		for track in rt.iter("track"):
			artist = track.find("artist").text
			name = track.find("name").text
			album = track.find("album").text
			if "nowplaying" in track.attrib and track.attrib["nowplaying"] == "true":
				continue # We get to that later.
			else:
				timestamp = int(track.find("date").attrib['uts'])
				c.execute("INSERT INTO tracks (artist, name, album, timestamp) VALUES (?,?,?,?)",
					(artist, name, album, timestamp))
		conn.commit()
		print("%d%% downloaded" % int((page/totalPages)*100))
			
else:
	print("Nothing to do. Listen to more music!")

c.close()
conn.close()
