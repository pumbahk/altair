inifile = development.ini

clean:
	find . -name "*.pyc" -exec rm {} \;
	rm -rf altaircms/plugins/static/*
	if [ -d altaircms/demo/asset ]; then rm -r altaircms/demo/asset; fi

test:
	python -m unittest discover
	# nosetests -q

printpage:
	pscript -e env -c ${inifile} -s scripts/pscript/print_page.py

printapp:
	pmain -c onetime.ini -s scripts.pmain.printapp

checkpage:
	cat altaircms/templates/front/original/original.html | tr "\n" " "| sed 's/[ \t\n]//g'> /tmp/before.log
	paster pmain -E env onetime.ini scripts.pmain.original5 > /tmp/after.html
	cat /tmp/after.html | tr "\n" " "| sed 's/[ \t\n]//g'> /tmp/after.log
	diff -u /tmp/before.log /tmp/after.log

