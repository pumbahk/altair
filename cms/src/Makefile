inifile = development.ini

clean:
	find . -name "*.pyc" | xargs rm 

test:
	python -m unittest discover

printpage:
	paster pscript  -E env ${inifile} scripts/pscript/print_page.py

printapp:
	paster pscript  -E app ${inifile} scripts/pscript/printapp.py