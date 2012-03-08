inifile = development.ini

clean:
	find . -name "*.pyc" | xargs rm 
	test -d altaircms/demo/asset && rm -r altaircms/demo/asset

test:
	python -m unittest discover
	# nosetests -q

printpage:
	paster pscript  -E env ${inifile} scripts/pscript/print_page.py

printapp:
	paster pmain -E app onetime.ini scripts.pmain.printapp

checkpage:
	cat altaircms/templates/front/original/original.html | tr "\n" " "| sed 's/[ \t\n]//g'> /tmp/before.log
	paster pmain -E env onetime.ini scripts.pmain.original5 > /tmp/after.html
	cat /tmp/after.html | tr "\n" " "| sed 's/[ \t\n]//g'> /tmp/after.log
	diff -u /tmp/before.log /tmp/after.log

