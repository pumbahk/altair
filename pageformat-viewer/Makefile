HTTPD=httpd
PYTHON=python

pageformat-viewer.js: src/*.js
	$(PYTHON) compile.py -o $@ src/pageformat-viewer.js

run: pageformat-viewer.js
	@test -d "${PWD}/tmp" || mkdir "${PWD}/tmp"
	@$(HTTPD) -f "${PWD}/httpd.test.conf"

stop:
	@if test -e "${PWD}/tmp/pid"; then \
		kill -TERM `cat "${PWD}/tmp/pid"`; \
	else \
		echo "Server not running"; \
	fi

clean:
	rm pageformat-viewer.js

.PHONY: run stop clean
