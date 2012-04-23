from datetime import date
import os

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
		html += "<title>Statistics :: Logged life</title>"
		html += "</head><body><h1>Statistics</h1><ul>"
		for c in self.charts:
			html += "<li><a href='%s'>%s</a></li>" % (
					os.path.join((os.path.relpath(os.path.dirname(c[0]), os.path.dirname(path))), os.path.basename(c[0])), 
					c[1]
					)
		html += "</ul><p>generated %s</p>" % date.today().isoformat()
		html += "</body></html>"
		f = open(path, "w")
		f.write(html)
		f.close()
		
