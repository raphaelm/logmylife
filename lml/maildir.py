import sqlite3
import os
import re
import email.parser
import email.utils
import time
import sys
from datetime import date, datetime, timedelta

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.dates as md

from utils import daterange
import base

class Scan(base.Scan):
	def parsemail(self, f):
		fp = open(f)
		p = email.parser.Parser()
		r = p.parse(fp)
		fp.close()
		d = email.utils.parsedate(r.get("Date"))
		msgid = r.get("Message-ID")
		if d is not None and r.get("X-Autoreply") != "yes":
			self.c.execute("INSERT INTO mails (msgid, msg_to, msg_from, contenttype, msg_time, replyto, filesize) VALUES (?,?,?,?,?,?,?)",
				(
					msgid,
					email.utils.parseaddr(r.get("To"))[1],
					email.utils.parseaddr(r.get("From"))[1],
					r.get("Content-Type", ""),
					time.mktime(d),
					r.get("In-Reply-To", ""),
					os.path.getsize(f)
				))
			if self.i % 10 == 0:
				sys.stdout.write("\r%05d mails scanned" % self.i)
				sys.stdout.flush()
				self.conn.commit()
			self.i += 1
		
	def scan(self):		
		for f in os.listdir(self.MDIR+'cur'):
			self.parsemail(self.MDIR+'cur/'+f)
			
		for f in os.listdir(self.MDIR+'new'):
			self.parsemail(self.MDIR+'new/'+f)
		
		print "\rScanned.                          "
		self.conn.commit()
		self.c.close()
			
			
	def __init__(self, MDIR, FILE):
		self.MDIR = MDIR
		self.i = 0
		print "Scanning maildir",
		if os.path.exists(FILE):
			self.conn = sqlite3.connect(FILE)
			self.c = self.conn.cursor()
		else:
			self.conn = sqlite3.connect(FILE)
			self.c = self.conn.cursor()
			self.c.execute('''CREATE TABLE mails (msgid text unique on conflict ignore, msg_to text, msg_from text, contenttype text, msg_time real, replyto text, filesize real)''')
		self.conn.text_factory = str
		
class Charts(base.Charts):
	def chart_date_time(self):
		
		x_total = []
		y_total = []
		x_out = []
		y_out = []
		x_in = []
		y_in = []
		
		mere = re.compile(self.ME)
		
		self.c.execute('SELECT msg_time, msg_from, msg_to, msgid FROM mails WHERE msg_time > 0')
		for row in self.c:
			ts = row[0]
			x = date.fromtimestamp(ts)
			y = (ts % (3600*24))/3600
			if mere.match(row[1]) is None or mere.match(row[2]) is not None:
				# Mails to myself shouldn't be counted, they are either spam
				# or "irrelevant" for my communication profile
				x_in.append(x)
				y_in.append(y)
			else:
				x_out.append(x)
				y_out.append(y)
			x_total.append(x)
			y_total.append(y)
			
			
			
		# Total Scatter
		plt.clf()
		ax = plt.subplot(111)
		x_total = md.date2num(x_total)
		plt.scatter(x_in, y_in, s=3, marker=(0,3,0), linewidths=0, c='g', label='Incoming')
		plt.scatter(x_out, y_out, s=3, marker=(0,3,0), linewidths=0, c='b', label='Outgoing')
		plt.legend(loc=3)
		labels = ax.get_xticklabels()
		plt.setp(labels, rotation=30, fontsize=10)
		plt.axis([min(x_total), max(x_total), 0, 24])
		plt.title("Mail (total)")
		ax.xaxis_date()
		plt.yticks(range(0, 25))
		ax.xaxis.set_major_formatter( md.DateFormatter('%m/%Y') )
		ax.set_ylabel("time of day")
		plt.savefig(self.FILEPREFIX+"times_total.png")
		self.charts.append(self.FILEPREFIX+"times_total.png")
			
		# Total Histogram
		plt.clf()
		ax = plt.subplot(111)
		#plt.hist(y_in, bins=range(0,25), color='g', label='Incoming')
		#plt.hist(y_out, bins=range(0,25), color='b', label='Outgoing')
		plt.hist([y_out, y_in], bins=range(0,25), color=['b', 'g'], label=['outgoing', 'incoming'], histtype='barstacked')
		plt.xlim(0,24)
		plt.legend(loc=0)
		plt.title("Mail distribution (total)")
		plt.xticks(range(0, 25))
		ax.set_xlabel("time of day")
		plt.savefig(self.FILEPREFIX+"times_total.hist.png")
		self.charts.append(self.FILEPREFIX+"times_total.hist.png")
			
		# Incoming Scatter
		plt.clf()
		ax = plt.subplot(111)
		x_in = md.date2num(x_in)
		plt.scatter(x_in, y_in, s=3, marker=(0,3,0), linewidths=0, c='g')
		labels = ax.get_xticklabels()
		plt.setp(labels, rotation=30, fontsize=10)
		plt.axis([min(x_total), max(x_total), 0, 24])
		plt.title("Mail (incoming)")
		ax.xaxis_date()
		plt.yticks(range(0, 25))
		ax.xaxis.set_major_formatter( md.DateFormatter('%m/%Y') )
		ax.set_ylabel("time of day")
		plt.savefig(self.FILEPREFIX+"times_in.png")
		self.charts.append(self.FILEPREFIX+"times_in.png")
			
		# Incoming Histogram
		plt.clf()
		ax = plt.subplot(111)
		plt.hist(y_in, bins=range(0,25), color='g', label='Incoming')
		plt.xlim(0,24)
		plt.title("Mail distribution (incoming)")
		plt.xticks(range(0, 25))
		ax.set_xlabel("time of day")
		plt.savefig(self.FILEPREFIX+"times_in.hist.png")
		self.charts.append(self.FILEPREFIX+"times_in.hist.png")
			
		# Outgoing Scatter
		plt.clf()
		ax = plt.subplot(111)
		x_out = md.date2num(x_out)
		plt.scatter(x_out, y_out, s=3, marker=(0,3,0), linewidths=0, c='b')
		labels = ax.get_xticklabels()
		plt.setp(labels, rotation=30, fontsize=10)
		plt.axis([min(x_total), max(x_total), 0, 24])
		plt.title("Mail (outgoing)")
		ax.xaxis_date()
		plt.yticks(range(0, 25))
		ax.xaxis.set_major_formatter( md.DateFormatter('%m/%Y') )
		ax.set_ylabel("time of day")
		plt.savefig(self.FILEPREFIX+"times_out.png")
		self.charts.append(self.FILEPREFIX+"times_out.png")
			
		# Outgoing Histogram
		plt.clf()
		ax = plt.subplot(111)
		plt.hist(y_out, bins=range(0,25), color='b', label='Outgoing')
		plt.xlim(0,24)
		plt.title("Mail distribution (outgoing)")
		plt.xticks(range(0, 25))
		ax.set_xlabel("time of day")
		plt.savefig(self.FILEPREFIX+"times_out.hist.png")
		self.charts.append(self.FILEPREFIX+"times_out.hist.png")

	def chart_filesize(self):
		x_total = []
		x_out = []
		x_in = []
		
		mere = re.compile(self.ME)
		
		self.c.execute('SELECT filesize, msg_from, msg_to FROM mails')
		for row in self.c:
			fs = row[0]
			x = fs
			if mere.match(row[1]) is None or mere.match(row[2]) is not None:
				# Mails to myself shouldn't be counted, they are either spam
				# or "irrelevant" for my communication profile
				x_in.append(x)
			else:
				x_out.append(x)
			x_total.append(x)
		
		plt.clf()
		ax = plt.subplot(111)
		plt.hist([x_out, x_in], bins=30, color=['b', 'g'], label=['outgoing', 'incoming'], log=True)
		plt.title("Mail size (distribution)")
		ax.set_xlabel("bytes")
		ax.set_ylabel("count")
		plt.legend(loc=0)
		plt.ylim(ymin=1)
		plt.savefig(self.FILEPREFIX+"size.png")
		self.charts.append(self.FILEPREFIX+"size.png")
		
	def chart_mailsperday(self):
		self.c.execute('SELECT MIN(msg_time), MAX(msg_time) FROM mails')
		firstmail, lastmail = self.c.fetchone()
		x_out = []
		x_in = []
		day_out = {}
		day_in = {}
		days = []
		month = 0
		months = []
		x_months_in = []
		x_months_out = []
		
		mere = re.compile(self.ME)
		
		self.c.execute('SELECT msg_time, msg_from, msg_to, msgid FROM mails WHERE msg_time > 0')
		for row in self.c:
			ts = row[0]
			x = date.fromtimestamp(ts)
			d = x.isoformat()
			if mere.match(row[1]) is None or mere.match(row[2]) is not None:
				# Mails to myself shouldn't be counted, they are either spam
				# or "irrelevant" for my communication profile
				if d in day_in:
					day_in[d] += 1
				else:
					day_in[d] = 1
			else:
				if d in day_out:
					day_out[d] += 1
				else:
					day_out[d] = 1

		for single_date in daterange(date.fromtimestamp(firstmail), date.fromtimestamp(lastmail)):
			days.append(single_date)
			d = single_date.isoformat()
				
			if d[0:7] != month:
				month = d[0:7]
				months.append(single_date)
				x_months_in.append([0,0])
				x_months_out.append([0,0])
				
			if d in day_in:
				x_in.append(day_in[d])
				x_months_in[len(x_months_in)-1][0] += day_in[d]
			else:
				x_in.append(0)
			if d in day_out:
				x_out.append(day_out[d])
				x_months_out[len(x_months_out)-1][0] += day_out[d]
			else:
				x_out.append(0)
			x_months_in[len(x_months_in)-1][1] += 1
			x_months_out[len(x_months_out)-1][1] += 1
			
		days = md.date2num(days)
		months = md.date2num(months)
		x_months_out = [float(_x[0])/float(_x[1]) for _x in x_months_out]
		x_months_in = [float(_x[0])/float(_x[1]) for _x in x_months_in]
		
		plt.clf()
		ax = plt.subplot(111)
		plt.plot(days, x_out, 'b', label='outgoing')
		plt.plot(days, x_in, 'g', label='incoming')
		plt.title("Mails per day")
		ax.set_ylabel("count")
		ax.xaxis_date()
		plt.axis([min(days), max(days), 0, max((max(x_in), max(x_out)))+5])
		ax.xaxis.set_major_formatter( md.DateFormatter('%m/%Y') )
		labels = ax.get_xticklabels()
		plt.legend(loc=0)
		plt.setp(labels, rotation=30, fontsize=10)
		plt.savefig(self.FILEPREFIX+"perday.png")
		self.charts.append(self.FILEPREFIX+"perday.png")
		
		plt.clf()
		ax = plt.subplot(111)
		plt.plot(months, x_months_out, 'b', label='outgoing')
		plt.plot(months, x_months_in, 'g', label='incoming')
		plt.title("Mails per day (averaged by month)")
		ax.set_ylabel("count")
		ax.xaxis_date()
		plt.axis([min(months), max(months), 0, max((max(x_months_in), max(x_months_out)))+5])
		ax.xaxis.set_major_formatter( md.DateFormatter('%m/%Y') )
		labels = ax.get_xticklabels()
		plt.legend(loc=0)
		plt.setp(labels, rotation=30, fontsize=10)
		plt.savefig(self.FILEPREFIX+"perday.avg.png")
		self.charts.append(self.FILEPREFIX+"perday.avg.png")
		
		plt.clf()
		ax = plt.subplot(111)
		plt.hist([x_out, x_in], bins=100, color=['b', 'g'], label=['outgoing', 'incoming'], histtype='barstacked', log=False)
		plt.title("Mails per day (distribution)")
		ax.set_xlabel("count")
		ax.set_ylabel("days")
		plt.xlim(0, 50)
		plt.legend(loc=0)
		plt.savefig(self.FILEPREFIX+"perday.hist.png")
		self.charts.append(self.FILEPREFIX+"perday.hist.png")
		
	def create_simple_html(self):
		html = "<html><head>"
		html += "<title>Email statistics for %s</title>" % self.ACCOUNT
		html += "</head><body><h1>Email statistics for %s</h1><a href='./'>Overview</a><br />" % self.ACCOUNT
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
		self.chart_filesize()
		self.chart_mailsperday()
		return self.create_simple_html()
			
	def __init__(self, FILE, FILEPREFIX, ME, ACCOUNT):
		self.FILEPREFIX = FILEPREFIX
		self.FILE = FILE
		self.ME = ME
		self.ACCOUNT = ACCOUNT
		
		if os.path.exists(FILE):
			self.conn = sqlite3.connect(FILE)
			self.c = self.conn.cursor()
		else:
			print "Database not found!"
			sys.exit()
		self.conn.text_factory = str