run: gencsv events performances bound
	
gencsv:
	python convert_from_scraped.py --infile="testdata-events-20120528.txt" --dburl="mysql+pymysql://altaircms:altaircms@localhost/altaircms?charset=utf8"
	
events:
	loadfromcsv --dburl="mysql+pymysql://altaircms:altaircms@localhost/altaircms?charset=utf8" altaircms.event.models:Event ./events.csv

performances:
	loadfromcsv --dburl="mysql+pymysql://altaircms:altaircms@localhost/altaircms?charset=utf8" altaircms.models:Performance ./performances.csv

bound:
	python bound_event_and_performances.py --dburl="mysql+pymysql://altaircms:altaircms@localhost/altaircms?charset=utf8"
