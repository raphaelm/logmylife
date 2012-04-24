from datetime import date
import os
import locale
import gettext

class Scan:
	def scan(self):
		raise NotImplementedError( "Should have implemented this" )
		
	def __init__(self, FILE, FILEPREFIX):
		self.FILEPREFIX = FILEPREFIX
		self.FILE = FILE
		
class Download:
	def download(self):
		raise NotImplementedError( "Should have implemented this" )
		
class Charts:
	def create(self):
		raise NotImplementedError( "Should have implemented this" )

class Generator:
	charts = []
	
	def create_simple_html_index(self, path):
		html = "<html><head>"
		html += "<title>"+_("Statistics :: Logged life")+"</title>"
		html += "</head><body><h1>"+_("Statistics")+"</h1><ul>"
		for c in self.charts:
			html += "<li><a href='%s'>%s</a></li>" % (
					os.path.join((os.path.relpath(os.path.dirname(c[0]), os.path.dirname(path))), os.path.basename(c[0])), 
					c[1]
					)
		html += ("</ul><p>"+_("generated %s")+"</p>") % date.today().isoformat()
		html += "</body></html>"
		f = open(path, "w")
		f.write(html)
		f.close()
		
	def __init__(self):
		locale.setlocale(locale.LC_ALL, '') # use user's preferred locale
		# take first two characters of country code
		loc = locale.getlocale()
		filename = "res/messages_%s.mo" % locale.getlocale()[0][0:2]
		
		try:
			trans = gettext.GNUTranslations(open( filename, "rb" ) )
		except IOError:
			trans = gettext.NullTranslations()

		trans.install(True)
