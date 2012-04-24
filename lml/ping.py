import time
import os
import urllib
import codecs
from datetime import date, datetime, timedelta

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.dates as md

import base
from utils import daterange

class Download(base.Download):
	def __init__(self, FILE, SERVER, HASH, DEVICE):
		self.FILE = FILE
		self.SERVER = SERVER
		self.HASH = HASH
		self.DEVICE = DEVICE
		
	def download(self):
		f = urllib.urlopen("%sdata/pings.%s.%s.txt" % (self.SERVER, self.HASH, self.DEVICE))
		f2 = open(self.FILE, 'w')
		f2.write(f.read())
		f.close()
		f2.close()
		
class Charts(base.Charts):
	
	def chart_date_time(self):
		x_total = []
		y_total = []
		y_week = []
		y_weekend = []
		
		f = open(self.FILE)
		for row in f:
			t = time.localtime(float(row.strip()))
			x = date.fromtimestamp(time.mktime(t))
			y = t.tm_hour + (t.tm_min/60.0)
			if t.tm_wday > 4:
				y_weekend.append(y)
			else:
				y_week.append(y)
			x_total.append(x)
			y_total.append(y)
		
		# Pings Scatter
		plt.clf()
		ax = plt.subplot(111)
		x_total = md.date2num(x_total)
		plt.scatter(x_total, y_total, s=5, marker=(0,3,0), linewidths=0)
		labels = ax.get_xticklabels()
		plt.setp(labels, rotation=30, fontsize=10)
		min_t = min(x_total)
		max_t = max(x_total)
		plt.axis([min_t, max_t, 0, 24])
		plt.title(_("Pings"))
		ax.xaxis_date()
		plt.yticks(range(0, 25))
		ax.xaxis.set_major_formatter( md.DateFormatter('%m/%Y') )
		ax.set_ylabel(_("time of day"))
		plt.savefig(self.FILEPREFIX+"times.png")
		self.charts.append(self.FILEPREFIX+"times.png")
						
		# Pings Histogram
		plt.clf()
		ax = plt.subplot(111)
		plt.hist(y_total, bins=range(0,25))
		plt.xlim(0,24)
		plt.title(_("Pings distribution"))
		plt.xticks(range(0, 25))
		ax.set_xlabel(_("time of day"))
		ax.set_ylabel(_("count"))
		plt.savefig(self.FILEPREFIX+"times.hist.png")
		self.charts.append(self.FILEPREFIX+"times.hist.png")
		
		if len(y_week) > 0:
			# Pings Histogram, weekdays
			plt.clf()
			ax = plt.subplot(111)
			plt.hist(y_week, bins=range(0,25))
			plt.xlim(0,24)
			plt.title(_("Pings distribution on weekdays"))
			plt.xticks(range(0, 25))
			ax.set_xlabel(_("time of day"))
			ax.set_ylabel(_("count"))
			plt.savefig(self.FILEPREFIX+"times.hist.week.png")
			self.charts.append(self.FILEPREFIX+"times.hist.week.png")
					
		if len(y_weekend) > 0:	
			# Pings Histogram, weekends
			plt.clf()
			ax = plt.subplot(111)
			plt.hist(y_weekend, bins=range(0,25))
			plt.xlim(0,24)
			plt.title(_("Pings distribution at the weekends"))
			plt.xticks(range(0, 25))
			ax.set_xlabel(_("time of day"))
			ax.set_ylabel(_("count"))
			plt.savefig(self.FILEPREFIX+"times.hist.we.png")
			self.charts.append(self.FILEPREFIX+"times.hist.we.png")
		
	def create_simple_html(self):
		html = "<html><head>"
		html += ("<title>"+_("Online statistics for %s")+"</title>") % self.DEVICE
		html += ("</head><body><h1>"+_("Online statistics for %s")+"</h1><a href='./'>"+_("Overview")+"</a><br />") % self.DEVICE
		for c in self.charts:
			html += "<img src='%s' /><br />" % os.path.join((os.path.relpath(os.path.dirname(c), os.path.dirname(self.FILEPREFIX))), os.path.basename(c))
		html += _("generated %s") % date.today().isoformat()
		html += "</body></html>"
		f = codecs.open(self.FILEPREFIX+"all.html", mode="w", encoding='utf-8')
		f.write(html)
		f.close()
		return self.FILEPREFIX+"all.html"
		
	def create(self):		
		self.charts = []
		self.chart_date_time()
		return self.create_simple_html()
			
	def __init__(self, FILE, FILEPREFIX, DEVICE):
		self.FILEPREFIX = FILEPREFIX
		self.FILE = FILE
		self.DEVICE = DEVICE
		
		if not os.path.exists(FILE):
			print _("Data not found!")
			exit()
