#!/usr/bin/env python
import os
import time
import datetime
from optparse import OptionParser
import traceback
import sys

import lml.base

if not os.path.exists('data'):
	os.mkdir('data')
if not os.path.exists('charts'):
	os.mkdir('charts')

class Generator(lml.base.Generator):
	
	def twitter(self, download = True):
		print "Twitter"
		import lml.twitter
		USER = "_rami_"
		FILE = "data/%s.twitter.sqlite.db" % USER
		FILEPREFIX = "charts/%s.twitter.chart." % USER
		try:
			if download:
				lml.twitter.Download(FILE, USER).download()
			chart = lml.twitter.Charts(FILE, FILEPREFIX, USER).create()
			self.charts.append((chart, _("Twitter: %s") % USER))
			print "Twitter done."
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
			print "Twitter error."

	def mail(self, scan = True):
		print "Mail"
		import lml.maildir
		ACCOUNT = "raphaelmichel95.gmail.com"
		FILE = "data/%s.maildir.sqlite.db" % ACCOUNT
		FILEPREFIX = "charts/%s.maildir.chart." % ACCOUNT
		ME = "(raphaelmichel95@(googlemail|gmail).com|.+@raphaelmichel.de|michel@schlusen.net|rami@daquel.de|raphaelm@php.net|raphael@geeksfactory.de)"
		MDIR = os.path.expanduser("~/backup/gmail/")
		try:
			if scan:
				lml.maildir.Scan(MDIR, FILE).scan()
			chart = lml.maildir.Charts(FILE, FILEPREFIX, ME, ACCOUNT).create()
			self.charts.append((chart, _("Email: %s") % "raphaelmichel95@gmail.com"))
			print "Mail done."
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
			print "Mail error."

	def lastfm(self, download = True):
		print "Music"
		import lml.music
		USER = "rami95"
		FILE = "data/%s.lastfm.sqlite.db" % USER
		FILEPREFIX = "charts/%s.lastfm.chart." % USER
		APIK = "b8258575158335e66482df0777e5b331"
		OFFSET = time.mktime(datetime.datetime(2010,01,01).timetuple())
		try:
			if download:
				lml.music.DownloadLastFm(FILE, USER, APIK, OFFSET).download()
			chart = lml.music.Charts(FILE, FILEPREFIX, USER).create()
			self.charts.append((chart, _("Music (Last.fm): %s") % USER))
			print "Music done."
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
			print "Music error."
		
	def ping(self, download = True):
		print "Ping"
		import lml.ping
		KEYHASH = "0e0f17629059a77b7d4b0a6d95845e5b7a1c4490" # SHA1 hash of my "ping" key
		SERVER = "http://www.raphaelmichel.de/stats/pingserver/"
		
		DEVICE = "PC"
		FILE = "data/%s.ping.raw.txt" % DEVICE
		FILEPREFIX = "charts/%s.ping.chart." % DEVICE
		try:
			if download:
				lml.ping.Download(FILE, SERVER, KEYHASH, DEVICE).download()
			chart = lml.ping.Charts(FILE, FILEPREFIX, DEVICE).create()
			self.charts.append((chart, _("Online time: desktop computer")))
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
			print "Ping error."
		
		DEVICE = "android"
		FILE = "data/%s.ping.raw.txt" % DEVICE
		FILEPREFIX = "charts/%s.ping.chart." % DEVICE
		try:
			if download:
				lml.ping.Download(FILE, SERVER, KEYHASH, DEVICE).download()
			chart = lml.ping.Charts(FILE, FILEPREFIX, DEVICE).create()
			self.charts.append((chart, _("Online time: smartphone")))
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
			print "Ping error."
		
		print "Ping done."
		
def main():
	parser = OptionParser()
	parser.add_option("-m", "--no-mail",
					  action="store_false", dest="mail", default=True,
					  help="Don't scan mail")
	parser.add_option("-t", "--no-twitter",
					  action="store_false", dest="twitter", default=True,
					  help="Don't scan twitter")
	parser.add_option("-l", "--no-music",
					  action="store_false", dest="lastfm", default=True,
					  help="Don't scan last.fm")
	parser.add_option("-p", "--no-ping",
					  action="store_false", dest="ping", default=True,
					  help="Don't scan ping data")
	parser.add_option("-d", "--no-downloads",
					  action="store_false", dest="dl", default=True,
					  help="Don't use data we not already have")

	(options, args) = parser.parse_args()

	g = Generator()
	if options.mail:
		g.mail(options.dl)
	if options.twitter:
		g.twitter(options.dl)
	if options.lastfm:
		g.lastfm(options.dl)
	if options.ping:
		g.ping(options.dl)

	g.create_simple_html_index("charts/index.html")

if __name__ == '__main__':
	main()
