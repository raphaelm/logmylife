import os
import sqlite3
import urllib
import json
import email.utils
import time
from datetime import date, datetime, timedelta, tzinfo

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.dates as md

from utils import daterange
import base
		
class Download(base.Download):
	def __init__(self, FILE, USER):
		self.FILE = FILE
		self.USER = USER
		
	def download(self):
		if os.path.exists(self.FILE):
			conn = sqlite3.connect(self.FILE)
			c = conn.cursor()
			c.execute('SELECT MAX(id) FROM tweets')
			last = c.fetchone()[0]
			if last is None:
				last = 0
		else:
			conn = sqlite3.connect(self.FILE)
			c = conn.cursor()
			c.execute('''CREATE TABLE tweets (id text unique on conflict ignore, text text, timestamp real)''')
			last = 0

		maxid = ''
		for page in range(1,17): # Absolute limit by twitter :(
			if page == 1:
				if last != 0:
					f = urllib.urlopen("https://api.twitter.com/1/statuses/user_timeline.json?include_entities=true&include_rts=false&trim_user=1&screen_name=%s&count=200&since_id=%s" % (self.USER, last))
				else:
					f = urllib.urlopen("https://api.twitter.com/1/statuses/user_timeline.json?include_entities=true&include_rts=false&trim_user=1&screen_name=%s&count=200" % (self.USER))
			else:
				if last != 0:
					f = urllib.urlopen("https://api.twitter.com/1/statuses/user_timeline.json?include_entities=true&include_rts=false&trim_user=1&screen_name=%s&count=200&since_id=%s&max_id=%s" % (self.USER, last, maxid))
				else:
					f = urllib.urlopen("https://api.twitter.com/1/statuses/user_timeline.json?include_entities=true&include_rts=false&trim_user=1&screen_name=%s&count=200&max_id=%s" % (self.USER, maxid))

			tree = json.loads(f.read())
			if len(tree) == 0:
				break
			else:
				for tweet in tree:
					timestamp = time.mktime(email.utils.parsedate(tweet['created_at'])) # guesses best
					c.execute("INSERT INTO tweets (id, text, timestamp) VALUES (?,?,?)",
						(tweet['id'], tweet['text'], timestamp))
				maxid = tweet['id']
			conn.commit()
			print("%d pages downloaded" % page)

		c.close()
		conn.close()


class Charts(base.Charts):
	
	def chart_date_time(self):
		x_total = []
		y_total = []
		
		self.c.execute('SELECT timestamp FROM tweets')
		for row in self.c:
			t = time.localtime(float(row[0]))
			x = date.fromtimestamp(time.mktime(t))
			y = t.tm_hour + (t.tm_min/60.0)
			x_total.append(x)
			y_total.append(y)
			
		# Tweets Scatter
		plt.clf()
		ax = plt.subplot(111)
		x_total = md.date2num(x_total)
		plt.scatter(x_total, y_total, s=5, marker=(0,3,0), linewidths=0)
		labels = ax.get_xticklabels()
		plt.setp(labels, rotation=30, fontsize=10)
		min_t = min(x_total)
		max_t = max(x_total)
		plt.axis([min_t, max_t, 0, 24])
		plt.title("Tweets")
		ax.xaxis_date()
		plt.yticks(range(0, 25))
		ax.xaxis.set_major_formatter( md.DateFormatter('%m/%Y') )
		ax.set_ylabel("time of day")
		plt.savefig(self.FILEPREFIX+"times.png")
		self.charts.append(self.FILEPREFIX+"times.png")
			
		# Tweets Histogram
		plt.clf()
		ax = plt.subplot(111)
		plt.hist(y_total, bins=range(0,25))
		plt.xlim(0,24)
		plt.title("Tweets distribution")
		plt.xticks(range(0, 25))
		ax.set_xlabel("time of day")
		plt.savefig(self.FILEPREFIX+"times.hist.png")
		self.charts.append(self.FILEPREFIX+"times.hist.png")
		
	def chart_tweetsperday(self):
		self.c.execute('SELECT MIN(timestamp), MAX(timestamp) FROM tweets')
		firstt, lastt = self.c.fetchone()
		x = []
		days = []
		day = {}
		month = 0
		months = []
		x_months = []
		
		self.c.execute('SELECT timestamp FROM tweets WHERE timestamp > 0')
		for row in self.c:
			t = time.localtime(float(row[0]))
			d = date.fromtimestamp(time.mktime(t)).isoformat()
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
		plt.title("Tweets per day")
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
		plt.title("Tweets per day (averaged by month)")
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
		plt.title("Tweets per day (distribution)")
		ax.set_xlabel("count")
		ax.set_ylabel("days")
		plt.savefig(self.FILEPREFIX+"perday.hist.png")
		self.charts.append(self.FILEPREFIX+"perday.hist.png")
		
	def chart_tweetswithlink(self):
		self.c.execute('SELECT COUNT(*) FROM tweets')
		cnt = self.c.fetchone()[0]
		self.c.execute('SELECT COUNT(*) FROM tweets WHERE text LIKE "%http://%" OR text LIKE "%https://%"')
		cnt_link = self.c.fetchone()[0]
			
		plt.clf()
		plt.figure(figsize=(7,7))
		ax = plt.subplot(111)
		plt.pie((cnt_link, cnt-cnt_link), labels=('Tweets with a link', 'Tweets without a link'), autopct='%1.1f%%', shadow=True)
		plt.title("Links in tweets")
		plt.savefig(self.FILEPREFIX+"links.png")
		self.charts.append(self.FILEPREFIX+"links.png")
		
	def create_simple_html(self):
		html = "<html><head>"
		html += "<title>Twitter statistics for %s</title>" % self.USER
		html += "</head><body><h1>Twitter statistics for %s</h1><a href='./'>Overview</a><br />" % self.USER
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
		self.chart_tweetsperday()
		self.chart_tweetswithlink()
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
