import time
import os
import sqlite3
import urllib
import xml.etree.ElementTree
from datetime import date, datetime, timedelta

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.dates as md

import base
from utils import daterange

class DownloadLastFm(base.Download):
	def __init__(self, FILE, USER, APIK, OFFSET):
		self.FILE = FILE
		self.USER = USER
		self.APIK = APIK
		self.OFFSET = OFFSET
		
	def download(self):
		if os.path.exists(self.FILE):
			conn = sqlite3.connect(self.FILE)
			c = conn.cursor()
			c.execute('SELECT MAX(timestamp) FROM tracks')
			last = c.fetchone()[0]
			if last is None:
				last = self.OFFSET
		else:
			conn = sqlite3.connect(self.FILE)
			c = conn.cursor()
			c.execute('''CREATE TABLE tracks (artist text, name text, album text, timestamp real)''')
			last = self.OFFSET

		# Check number of Pages
		f = urllib.urlopen("http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=%s&api_key=%s&limit=200&page=0&from=%d" % (self.USER, self.APIK, last))
		tree = xml.etree.ElementTree.fromstring(f.read())
		rt = tree.find("recenttracks")
		total = int(rt.attrib['total'])
		totalPages = int(rt.attrib['totalPages'])

		if total > 0:
			for page in range(1,totalPages+1):
				f = urllib.urlopen("http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=%s&api_key=%s&limit=200&page=%d&from=%d" % (self.USER, self.APIK, page, last))
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
				print("%d%% downloaded" % int((float(page)/float(totalPages))*100))
					
		else:
			print("Nothing to do. Listen to more music!")

		c.close()
		conn.close()
		
class Charts(base.Charts):
	
	def chart_date_time(self):
		x_total = []
		y_total = []
		
		self.c.execute('SELECT timestamp FROM tracks')
		for row in self.c:
			ts = row[0]
			x = date.fromtimestamp(ts)
			y = (ts % (3600*24))/3600
			x_total.append(x)
			y_total.append(y)
			
		# Tracks Scatter
		plt.clf()
		ax = plt.subplot(111)
		x_total = md.date2num(x_total)
		plt.scatter(x_total, y_total, s=2, marker=(0,3,0), linewidths=0)
		labels = ax.get_xticklabels()
		plt.setp(labels, rotation=30, fontsize=10)
		min_t = min(x_total)
		max_t = max(x_total)
		plt.axis([min_t, max_t, 0, 24])
		plt.title("Listening to music")
		ax.xaxis_date()
		plt.yticks(range(0, 25))
		ax.xaxis.set_major_formatter( md.DateFormatter('%m/%Y') )
		ax.set_ylabel("time of day")
		plt.savefig(self.FILEPREFIX+"times.png")
		self.charts.append(self.FILEPREFIX+"times.png")
			
		# Tracks Histogram
		plt.clf()
		ax = plt.subplot(111)
		plt.hist(y_total, bins=range(0,25))
		plt.xlim(0,24)
		plt.title("Listening to music (distribution)")
		plt.xticks(range(0, 25))
		ax.set_xlabel("time of day")
		plt.savefig(self.FILEPREFIX+"times.hist.png")
		self.charts.append(self.FILEPREFIX+"times.hist.png")
		
	def chart_tracksperday(self):
		self.c.execute('SELECT MIN(timestamp), MAX(timestamp) FROM tracks')
		firstt, lastt = self.c.fetchone()
		x = []
		days = []
		day = {}
		month = 0
		months = []
		x_months = []
		
		self.c.execute('SELECT timestamp FROM tracks WHERE timestamp > 0')
		for row in self.c:
			ts = row[0]
			d = date.fromtimestamp(ts).isoformat()
			if d in day:
				day[d] += 1
			else:
				day[d] = 1

		for single_date in daterange(date.fromtimestamp(firstt), date.fromtimestamp(lastt)):
			days.append(single_date)
			d = single_date.isoformat()
			if d[0:7] != month:
				month = d[0:7]
				months.append(single_date)
				x_months.append([0,0])
				
			if d in day:
				x.append(day[d])
				x_months[len(x_months)-1][0] += day[d]
			else:
				x.append(0)
			x_months[len(x_months)-1][1] += 1
		
		days = md.date2num(days)
		months = md.date2num(months)
		x_months = [float(_x[0])/float(_x[1]) for _x in x_months]
		
		plt.clf()
		ax = plt.subplot(111)
		plt.plot(days, x)
		plt.title("Tracks played per day")
		ax.set_ylabel("count")
		ax.xaxis_date()
		plt.axis([min(days), max(days), 0, max(x)+5])
		ax.xaxis.set_major_formatter( md.DateFormatter('%m/%Y') )
		labels = ax.get_xticklabels()
		plt.setp(labels, rotation=30, fontsize=10)
		plt.savefig(self.FILEPREFIX+"perday.png")
		self.charts.append(self.FILEPREFIX+"perday.png")
		
		plt.clf()
		ax = plt.subplot(111)
		plt.plot(months, x_months)
		plt.title("Tracks played per day (averaged by month)")
		ax.set_ylabel("count")
		ax.xaxis_date()
		plt.axis([min(months), max(months), 0, max(x_months)+5])
		ax.xaxis.set_major_formatter( md.DateFormatter('%m/%Y') )
		labels = ax.get_xticklabels()
		plt.setp(labels, rotation=30, fontsize=10)
		plt.savefig(self.FILEPREFIX+"perday.avg.png")
		self.charts.append(self.FILEPREFIX+"perday.avg.png")
		
		plt.clf()
		ax = plt.subplot(111)
		plt.hist(x, bins=30, color='b')
		plt.title("Tracks played per day (distribution)")
		ax.set_xlabel("count")
		ax.set_ylabel("days")
		plt.savefig(self.FILEPREFIX+"perday.hist.png")
		self.charts.append(self.FILEPREFIX+"perday.hist.png")
		
	def chart_toptracks_range(self, start = 0, label = "total", n = 20):
		artists = []
		values = []		
		self.c.execute('SELECT name, COUNT(*) as cnt FROM tracks WHERE timestamp > %d GROUP by name ORDER by cnt DESC LIMIT %d' % (start, n))
		for row in self.c:
			artists.append(unicode(row[0], 'utf-8'))
			values.append(row[1])
		plt.clf()
		ax = plt.subplot(111)
		plt.barh(range(0,n), values, align='center', height=1)
		plt.yticks(range(0,n), artists)
		plt.autoscale()
		plt.subplots_adjust(left=0.25, right=0.9)
		plt.title("Top tracks ("+label+")")
		ax.set_xlabel("times played")
		plt.savefig(self.FILEPREFIX+"toptracks."+label+".png")
		self.charts.append(self.FILEPREFIX+"toptracks."+label+".png")
		
	def charts_toptracks(self):
		self.chart_toptracks_range(0, "total")
		self.chart_toptracks_range(time.time()-3600*24*7, "last week")
		self.chart_toptracks_range(time.time()-3600*24*31, "last month")
		self.chart_toptracks_range(time.time()-3600*24*365, "last year")
		
	def chart_topartists_range(self, start = 0, label = "total", n = 20):
		artists = []
		values = []		
		self.c.execute('SELECT artist, COUNT(*) as cnt FROM tracks WHERE timestamp > %d GROUP by artist ORDER by cnt DESC LIMIT %d' % (start, n))
		for row in self.c:
			artists.append(unicode(row[0], 'utf-8'))
			values.append(row[1])
		plt.clf()
		ax = plt.subplot(111)
		plt.barh(range(0,n), values, align='center', height=1)
		plt.yticks(range(0,n), artists)
		plt.autoscale()
		plt.subplots_adjust(left=0.25, right=0.9)
		plt.title("Top artists ("+label+")")
		ax.set_xlabel("tracks played")
		plt.savefig(self.FILEPREFIX+"topartists."+label+".png")
		self.charts.append(self.FILEPREFIX+"topartists."+label+".png")
		
	def charts_topartists(self):
		self.chart_topartists_range(0, "total")
		self.chart_topartists_range(time.time()-3600*24*7, "last week")
		self.chart_topartists_range(time.time()-3600*24*31, "last month")
		self.chart_topartists_range(time.time()-3600*24*365, "last year")
		
	def create_simple_html(self):
		html = "<html><head>"
		html += "<title>Last.fm statistics for %s</title>" % self.USER
		html += "</head><body><h1>Last.fm statistics for %s</h1><a href='./'>Overview</a><br />" % self.USER
		for c in self.charts:
			html += "<img src='%s' /><br />" % os.path.join((os.path.relpath(os.path.dirname(c), os.path.dirname(self.FILEPREFIX))), os.path.basename(c))
		html += "generated %s" % date.today().isoformat()
		html += "</body></html>"
		f = open(self.FILEPREFIX+"all.html", "w")
		f.write(html)
		f.close()
		return self.FILEPREFIX+"all.html"
		
	def create(self):		
		self.charts = []
		self.chart_date_time()
		self.chart_tracksperday()
		self.charts_topartists()
		self.charts_toptracks()
		return self.create_simple_html()
			
	def __init__(self, FILE, FILEPREFIX, USER):
		self.FILEPREFIX = FILEPREFIX
		self.FILE = FILE
		self.USER = USER
		
		if os.path.exists(FILE):
			self.conn = sqlite3.connect(FILE)
			self.c = self.conn.cursor()
		else:
			print "Database not found!"
			exit()
		self.conn.text_factory = str
