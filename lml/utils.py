from datetime import timedelta

def daterange(start_date, end_date):
	for n in range((end_date - start_date).days):
		yield start_date + timedelta(n)