DBURL=mysql+pymysql://altaircms:altaircms@localhost/altaircms?charset=utf8

run: gencsv events performances bound
	
gencsv:
	python convert_from_scraped.py --infile="testdata-events-20120528.txt" --dburl="${DBURL}"
	
events:
	loadfromcsv --dburl="${DBURL}" altaircms.event.models:Event ./events.csv

performances:
	loadfromcsv --dburl="${DBURL}" altaircms.models:Performance ./performances.csv

bound:
	python bound_event_and_performances.py --dburl="${DBURL}"
